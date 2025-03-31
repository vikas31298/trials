import requests
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.tools import tool
import json

# LLM with OpenAI function calling
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, openai_api_key="YOUR_OPENAI_KEY")

# Define the available functions
functions = [
    {
        "name": "assign_resource",
        "description": "Assigns a resource to a task based on skills and workload.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "The ID of the task to assign"},
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "detect_bottlenecks",
        "description": "Detects bottlenecks and suggests hiring recommendations.",
        "parameters": {}
    },
    {
        "name": "reassign_tasks",
        "description": "Reassigns tasks from an unavailable resource.",
        "parameters": {
            "type": "object",
            "properties": {
                "resource_id": {"type": "integer", "description": "The ID of the unavailable resource"},
            },
            "required": ["resource_id"]
        }
    }
]

# Function to call the appropriate API
def call_api(action, params={}):
    base_url = "http://127.0.0.1:8000"  # Assuming FastAPI is running locally

    if action == "assign_resource":
        task_id = params.get("task_id")
        response = requests.post(f"{base_url}/assign_resource/{task_id}")
    
    elif action == "detect_bottlenecks":
        response = requests.get(f"{base_url}/detect_bottlenecks/")
    
    elif action == "reassign_tasks":
        resource_id = params.get("resource_id")
        response = requests.post(f"{base_url}/reassign_tasks/{resource_id}")
    
    else:
        return "Unknown action."

    return response.json()

# Function to process user input and call the correct function
def process_user_input(user_prompt):
    messages = [
        SystemMessage(content="You are an AI assistant that decides which function to call based on user input."),
        HumanMessage(content=user_prompt)
    ]

    response = llm.predict_messages(messages, functions=functions)

    if response.additional_kwargs and "function_call" in response.additional_kwargs:
        function_call = response.additional_kwargs["function_call"]
        function_name = function_call["name"]
        parameters = json.loads(function_call["arguments"])
        return call_api(function_name, parameters)
    
    return "Sorry, I couldn't understand your request."
