
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

load_dotenv()


GROQ_API_KEY= os.environ.get("GROQ_API_KEY")
OPENAI_API_KEY =os.environ.get("OPENAI_API_KEY")


ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
DATABASE_URL = os.environ.get("DATABASE_URL")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    # allow_origins=ALLOWED_HOSTS, 
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


    