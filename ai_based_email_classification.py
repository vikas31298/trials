import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from transformers import BertTokenizer, BertForSequenceClassification
from torch.optim import AdamW
from transformers import InputExample, InputFeatures
import torch
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset
import warnings
warnings.filterwarnings('ignore')

# Step 1: Create dummy email dataset
def create_dummy_data(num_samples=800):
    departments = ['Sales', 'Support', 'Billing', 'Technical', 'HR']
    email_types = ['Inquiry', 'Feedback']
    
    data = []
    for _ in range(num_samples):
        department = np.random.choice(departments)
        email_type = np.random.choice(email_types)
        
        if department == 'Sales':
            if email_type == 'Inquiry':
                subject = "Question about your products"
                body = "Hello, I'm interested in your product lineup. Can you send me more information about pricing and features?"
            else:
                subject = "Great product experience"
                body = "I recently purchased your product and I'm extremely satisfied with its performance. Keep up the good work!"
        
        elif department == 'Support':
            if email_type == 'Inquiry':
                subject = "Need help with setup"
                body = "I'm having trouble setting up the device. Can you guide me through the process?"
            else:
                subject = "Excellent customer service"
                body = "Your support team was very helpful in resolving my issue quickly. Thank you!"
        
        elif department == 'Billing':
            if email_type == 'Inquiry':
                subject = "Invoice discrepancy"
                body = "I noticed a discrepancy in my latest invoice. Can you please check and correct it?"
            else:
                subject = "Smooth billing process"
                body = "The billing process was seamless and the invoice was very clear. Good job!"
        
        elif department == 'Technical':
            if email_type == 'Inquiry':
                subject = "Bug report"
                body = "I encountered an error when trying to use feature X. Here are the details..."
            else:
                subject = "Feature suggestion"
                body = "Your software is great! I'd like to suggest adding feature Y to make it even better."
        
        elif department == 'HR':
            if email_type == 'Inquiry':
                subject = "Job application"
                body = "I'm interested in applying for the open position. What is the application process?"
            else:
                subject = "Positive interview experience"
                body = "I recently interviewed with your company and wanted to say the process was very professional."
        
        # Combine subject and body for the model input
        text = f"Subject: {subject}\n\n{body}"
        
        data.append({
            'text': text,
            'department': department,
            'email_type': email_type,
            'subject': subject,
            'body': body
        })
    
    return pd.DataFrame(data)

# Create dummy dataset
df = create_dummy_data()
print(f"Created dummy dataset with {len(df)} emails")
print(df.head())

# Step 2: Preprocess data
# Combine department and email_type for multi-label classification (simplified approach)
df['combined_label'] = df['department'] + "_" + df['email_type']

# Encode labels
label_encoder = LabelEncoder()
df['encoded_label'] = label_encoder.fit_transform(df['combined_label'])

# Split data
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
print(f"Train size: {len(train_df)}, Test size: {len(test_df)}")

# Step 3: Prepare BERT model and tokenizer
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(
    model_name,
    num_labels=len(label_encoder.classes_),
    output_attentions=False,
    output_hidden_states=False
)

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Convert data to BERT input format
def convert_to_features(texts, labels, max_length=128):
    input_ids = []
    attention_masks = []
    
    for text in texts:
        encoded_dict = tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        input_ids.append(encoded_dict['input_ids'])
        attention_masks.append(encoded_dict['attention_mask'])
    
    input_ids = torch.cat(input_ids, dim=0)
    attention_masks = torch.cat(attention_masks, dim=0)
    labels = torch.tensor(labels)
    
    return input_ids, attention_masks, labels

# Convert training and testing data
train_inputs, train_masks, train_labels = convert_to_features(
    train_df['text'].tolist(), 
    train_df['encoded_label'].tolist()
)

test_inputs, test_masks, test_labels = convert_to_features(
    test_df['text'].tolist(), 
    test_df['encoded_label'].tolist()
)

# Create DataLoader
batch_size = 16

train_data = TensorDataset(train_inputs, train_masks, train_labels)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(
    train_data, 
    sampler=train_sampler, 
    batch_size=batch_size
)

test_data = TensorDataset(test_inputs, test_masks, test_labels)
test_sampler = SequentialSampler(test_data)
test_dataloader = DataLoader(
    test_data, 
    sampler=test_sampler, 
    batch_size=batch_size
)

# Step 4: Training setup
optimizer = AdamW(model.parameters(), lr=3e-5, eps=1e-8)
epochs = 4

# Training function
def train(model, train_dataloader, optimizer, epochs):
    model.train()
    
    for epoch in range(epochs):
        total_loss = 0
        
        for batch in train_dataloader:
            batch = tuple(t.to(device) for t in batch)
            b_input_ids, b_input_mask, b_labels = batch
            
            model.zero_grad()
            
            outputs = model(
                b_input_ids,
                attention_mask=b_input_mask,
                labels=b_labels
            )
            
            loss = outputs.loss
            total_loss += loss.item()
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
        
        avg_train_loss = total_loss / len(train_dataloader)
        print(f"Epoch {epoch + 1}/{epochs}, Average Training Loss: {avg_train_loss:.4f}")

# Evaluation function
def evaluate(model, test_dataloader):
    model.eval()
    predictions, true_labels = [], []
    
    for batch in test_dataloader:
        batch = tuple(t.to(device) for t in batch)
        b_input_ids, b_input_mask, b_labels = batch
        
        with torch.no_grad():
            outputs = model(
                b_input_ids,
                attention_mask=b_input_mask
            )
        
        logits = outputs.logits
        logits = logits.detach().cpu().numpy()
        label_ids = b_labels.to('cpu').numpy()
        
        predictions.append(logits)
        true_labels.append(label_ids)
    
    # Calculate accuracy
    flat_predictions = np.concatenate(predictions, axis=0)
    flat_predictions = np.argmax(flat_predictions, axis=1).flatten()
    flat_true_labels = np.concatenate(true_labels, axis=0)
    
    accuracy = accuracy_score(flat_true_labels, flat_predictions)
    print(f"Test Accuracy: {accuracy * 100:.2f}%")
    
    return accuracy

# Train the model
print("Training the model...")
train(model, train_dataloader, optimizer, epochs)

# Evaluate the model
print("Evaluating the model...")
evaluate(model, test_dataloader)

# Step 5: Prediction function
def classify_email(email_text):
    # Tokenize and prepare the input
    inputs = tokenizer.encode_plus(
        email_text,
        add_special_tokens=True,
        max_length=128,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )
    
    # Move tensors to the device
    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)
    
    # Make prediction
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
    
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=1).cpu().numpy()[0]
    predicted_label_idx = torch.argmax(logits, dim=1).item()
    predicted_label = label_encoder.inverse_transform([predicted_label_idx])[0]
    
    # Split back into department and type
    department, email_type = predicted_label.split('_')
    
    return {
        'department': department,
        'email_type': email_type,
        'confidence': probabilities[predicted_label_idx]
    }

# Test with sample emails
sample_emails = [
    """Subject: Problem with my account
    
    Hi, I can't log into my account. It says my password is incorrect but I'm sure it's right. Can you help?""",
    
    """Subject: Amazing service!
    
    I just wanted to say that your customer service team was incredibly helpful yesterday. The representative was patient and solved my issue quickly.""",
    
    """Subject: Question about pricing plans
    
    I'm considering upgrading my plan but I'm not sure about the differences between the premium and enterprise tiers. Can you clarify?"""
]

print("\nTesting with sample emails:")
for i, email in enumerate(sample_emails, 1):
    result = classify_email(email)
    print(f"\nSample Email {i}:")
    print(email)
    print("\nClassification Results:")
    print(f"Department: {result['department']}")
    print(f"Type: {result['email_type']}")
    print(f"Confidence: {result['confidence']:.4f}")
    


import openai

openai.api_key = "your_openai_api_key"

# Define the possible categories
CATEGORIES = ["Work", "Spam", "Personal", "Promotions", "Social", "Finance", "Updates"]

# System message gives GPT-4o instructions once
SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are an intelligent email classification assistant. "
        "Classify emails into one of the following categories: "
        f"{', '.join(CATEGORIES)}. "
        "Respond only with the category name. No explanation needed."
    )
}

# Function to classify a single email
def classify_email(email_text):
    messages = [
        SYSTEM_MESSAGE,
        {"role": "user", "content": email_text}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.0,
        max_tokens=10,
    )

    category = response.choices[0].message["content"].strip()
    return category

# Example usage
if __name__ == "__main__":
    sample_emails = [
        "Hi, please find attached the invoice for this month.",
        "Congratulations! You've won a free vacation to the Bahamas.",
        "Hey, are we still on for dinner tonight?",
        "Your OTP for login is 123456.",
        "Join us for an exclusive product launch offer!"
    ]

    for email in sample_emails:
        category = classify_email(email)
        print(f"Email: {email}\n→ Classified as: {category}\n")
