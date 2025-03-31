from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel


from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
from pathlib import Path
from fastapi import APIRouter, Body, Depends, HTTPException
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from ..config import GROQ_API_KEY,OPENAI_API_KEY
from ..config import DATABASE_URL

router = APIRouter(prefix="/analytics", tags=["Analytics"])
USE_POSTGRES = True 

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="Llama3-8b-8192", streaming=True)

def configure_db():
    if USE_POSTGRES:
        # connection_url = DATABASE_URL
        connection_url= "postgresql://postgres:Postgres%401@127.0.0.1:5432/ResourcifyDB?options=-c%20search_path=resourcifyschema"
        engine = create_engine(connection_url)
   
    return SQLDatabase(engine)

db = configure_db()

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

class QueryRequest(BaseModel):
    prompt: str
    




training_data = [

    {"query": "How many resources we have in total", "sql": "SELECT count(*) FROM Person;"},
    {"query": "Show me the top 5 employees with max workload", "sql": "SELECT * FROM employees ORDER BY workload DESC LIMIT 5;"},
    {"query": "Which employees are currently unassigned?", "sql": "SELECT * FROM employees WHERE project_id IS NULL;"},
]

embedding_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
vector_store = FAISS.from_texts([q["query"] for q in training_data], embedding_model)

def find_similar_query(user_query):
    result = vector_store.similarity_search(user_query, k=1)
    return result[0].page_content if result else None

def handle_query(user_query):
    matched_query = find_similar_query(user_query)

    if matched_query:
        for item in training_data:
            if item["query"] == matched_query:
                return item["sql"]

    generated_sql = llm(user_query)
    training_data.append({"query": user_query, "sql": generated_sql})
    vector_store.add_texts([user_query])
    
    return generated_sql

@router.post("/query")
async def query_database(request: QueryRequest):
    try:
        user_query = request.prompt
        # response = handle_query(user_query)
        response = agent.run(user_query)
        return {"query": user_query, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

