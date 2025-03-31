
import faiss
import numpy as np
import os
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

GROQ_API_KEY = "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"
OPENAI_API_KEY = "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"
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="Llama3-8b-8192")

training_data = [
    {"query": "Show top 5 employees with max workload", "sql": "SELECT * FROM employees ORDER BY workload DESC LIMIT 5;"},
    {"query": "List employees without assigned projects", "sql": "SELECT * FROM employees WHERE project_id IS NULL;"},
]

# Convert queries to embeddings
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vector_store = FAISS.from_texts([item["query"] for item in training_data], embedding_model)

# Debug: Show initial FAISS stored queries
print("\n🔹 Initial FAISS Queries Stored:")
for item in training_data:
    print(f"- {item['query']}")

# Function to find a similar query
def find_similar_query(user_query):
    print(f"\n🔍 Searching for similar query: {user_query}")
    results = vector_store.similarity_search(user_query, k=1)
    
    if results:
        for item in training_data:
            if item["query"] == results[0].page_content:
                print(f"✅ Found similar query: {item['query']}")
                return item
    print("❌ No similar query found.")
    return None

# Function to handle user queries
def handle_query(user_query):
    matched_item = find_similar_query(user_query)

    if matched_item:
        print(f"🎯 Returning stored SQL: {matched_item['sql']}")
        return matched_item["sql"]

    # If no match, generate a new SQL query
    print(f"🤖 Generating SQL for new query: {user_query}")
    response = llm.invoke(user_query)
    
    # Debug: Print raw LLM response
    print(f"📜 Raw LLM Response: {response}")

    generated_sql = response.content.strip()

    # Store the new query in training data
    new_entry = {"query": user_query, "sql": generated_sql}
    training_data.append(new_entry)

    # Debug: Show updated training data
    print(f"🆕 Stored new query: {new_entry}")

    # Update FAISS index
    vector_store.add_texts([user_query])

    # Debug: Check if FAISS added the query
    print(f"🔄 FAISS Updated: {user_query}")

    return generated_sql

# Function to generate SQL with context
def generate_sql_with_context(user_query):
    similar_item = find_similar_query(user_query)

    if similar_item:
        prompt = f"""
        You are an SQL expert. The user wants an SQL query for: "{user_query}".
        A similar query was asked before: "{similar_item['query']}".
        The previous SQL query used was:
        ```
        {similar_item['sql']}
        ```
        Use this as a reference to generate a more optimized SQL query.
        """
    else:
        prompt = f"You are an expert SQL generator. Generate an SQL query for: {user_query}"

    print(f"\n📝 Sending Prompt to LLM:\n{prompt}")

    response = llm.invoke(prompt)

    # Debug: Print raw response from LLM
    print(f"📜 LLM Response: {response}")

    return response.content.strip()

# Example usage
print("\n🚀 Running Example Query")
print(generate_sql_with_context("Show the employees with the highest workload"))
