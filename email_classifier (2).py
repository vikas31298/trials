import torch
from torch.utils.data import Dataset
from transformers import BertTokenizerFast, BertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd

# Dummy email dataset
emails = [
    ("I need help with my login credentials.", "Support_Inquiry"),
    ("Great experience with your customer service!", "Support_Feedback"),
    ("Can I get a quote for 100 units?", "Sales_Inquiry"),
    ("I want to leave feedback about your app.", "Technical_Feedback"),
    ("Is the job position in HR still open?", "HR_Inquiry"),
    ("The product I ordered arrived damaged.", "Support_Inquiry"),
    ("I have some suggestions for your new website layout.", "Technical_Feedback"),
    ("Thanks for the fast delivery!", "Sales_Feedback"),
    ("Are there any job openings?", "HR_Inquiry"),
    ("Not satisfied with the phone support I received.", "Support_Feedback")
]

# Preprocess text
def preprocess(text):
    return text.strip().lower()

# Prepare dataset
df = pd.DataFrame(emails, columns=["text", "label"])
df['text'] = df['text'].apply(preprocess)

le = LabelEncoder()
df['label_id'] = le.fit_transform(df['label'])

train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# Tokenizer and model
tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=len(le.classes_))

# Dataset class
class EmailDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_length=256):
        self.encodings = tokenizer(
            dataframe["text"].tolist(),
            truncation=True,
            padding=True,
            max_length=max_length
        )
        self.labels = dataframe["label_id"].tolist()

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# Create datasets
train_dataset = EmailDataset(train_df, tokenizer)
test_dataset = EmailDataset(test_df, tokenizer)

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    logging_dir="./logs",
    logging_steps=10,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

# Train the model
trainer.train()

# Save model
model.save_pretrained('./email_classifier_model')
tokenizer.save_pretrained('./email_classifier_tokenizer')

# Load and predict
def predict_email(subject, body):
    # Combine subject and body for prediction
    text = f"Subject: {subject} Body: {body}"
    
    model.eval()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_id = torch.argmax(logits, dim=1).item()
    return le.inverse_transform([predicted_class_id])[0]

# Test prediction
example_subject = "Sales"
example_body = "Can I get a quote for 100 units?"
predicted_label = predict_email(example_subject, example_body)
print(f"\nPredicted Label: {predicted_label}")
