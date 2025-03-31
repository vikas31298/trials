import re
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from sqlalchemy import create_engine
from config import GROQ_API_KEY, OPENAI_API_KEY, DATABASE_URL
import json

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="Llama3-8b-8192", streaming=True)

def configure_db():
    connection_url = "postgresql://postgres:Postgres%401@127.0.0.1:5432/ResourcifyDB?options=-c%20search_path=resourcifyschema"
    engine = create_engine(connection_url)
    return SQLDatabase(engine)

db = configure_db()



with open("SQLTraining.json", "r") as file:
    training_data = json.load(file)



embedding_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
vector_store = FAISS.from_texts([q["query"] for q in training_data], embedding_model)

def find_similar_query(user_query):
    """Find the most similar query from training data."""
    result = vector_store.similarity_search(user_query, k=1)
    return result[0].page_content if result else None

def extract_parameters(user_query, query_template):
    """Extract parameters dynamically from the user query."""
    param_values = {}

    match = re.search(r'top\s(\d+)', user_query, re.IGNORECASE)
    if match:
        param_values['limit'] = int(match.group(1))

    return param_values

def handle_query(user_query):
    """Handle query matching and dynamic parameter replacement."""
    matched_query = find_similar_query(user_query)

    if matched_query:
        for item in training_data:
            if item["query"] == matched_query:
                query_template = item["sql"]
                param_keys = item.get("params", [])

                user_params = extract_parameters(user_query, query_template)

                for key in param_keys:
                    if key in user_params:
                        query_template = query_template.replace(f"{{{key}}}", str(user_params[key]))

                return query_template

    generated_sql = llm.invoke(user_query)
    return generated_sql

def generate_sql_query(user_query: str):
    """Generate SQL query dynamically with parameters extracted from user input."""
    try:
        sql_query = handle_query(user_query)
        return sql_query
    except Exception as e:
        raise Exception(f"Error generating SQL query: {str(e)}")
