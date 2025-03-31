import json
from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage
from langchain_core.tools import StructuredTool
from config import OPENAI_API_KEY
from ExecuteSQLQuery import answer_user_query



from functions import (
    get_project_status,
    allocate_resources,
    get_team_availability,
    get_project_resources,
    get_resources_with_given_skills,
)

# Load function schemas
with open("functions.json", "r") as file:
    functions = json.load(file)

# Function mapping
FUNCTION_MAP = {
    "get_project_status": get_project_status,
    "allocate_resources": allocate_resources,
    "get_team_availability": get_team_availability,
    "get_project_resources": get_project_resources,
    "get_resources_with_given_skills": get_resources_with_given_skills,
}

QUERY_MEMORY = {}

llm = ChatOpenAI(
    model_name="gpt-4-turbo",  
    api_key=OPENAI_API_KEY
)


def call_appropriate_function(user_input):
    """Attempts to call an appropriate function. If not available, generates an SQL query."""
    
    response = llm.invoke([HumanMessage(content=user_input)])

    function_call = response.additional_kwargs.get("tool_calls")
    
    if function_call:
        for tool in function_call:
            function_name = tool.get("name")
            try:
                arguments = json.loads(tool.get("arguments", "{}"))
                if function_name in FUNCTION_MAP:
                    return FUNCTION_MAP[function_name](**arguments)
            except json.JSONDecodeError:
                return "Error: Failed to parse function arguments."

    return generate_sql_query(user_input)


def generate_sql_query(user_input):
    """Generates an SQL query using OpenAI and stores it in memory."""
    
    normalized_input = user_input.lower()

    if normalized_input in QUERY_MEMORY:
        return QUERY_MEMORY[normalized_input]  # Return cached SQL query

    response = llm.invoke([HumanMessage(content=f"Generate an SQL query for: {user_input}")])

    sql_query = response.content.strip()
    QUERY_MEMORY[normalized_input] = sql_query  # Store in memory for optimization
    return sql_query


def fetch_information(user_prompt):
    """Fetches information using functions or SQL query. Returns a meaningful response."""
    
    query_or_result = call_appropriate_function(user_prompt)
    
    if isinstance(query_or_result, str) and query_or_result.lower().startswith("select"):
        response = answer_user_query(query_or_result)  # Execute the SQL query
        
        if not response:
            print(f"Didn't find response for: {user_prompt}")
            return "Sorry, no information is available."
        
        return response
    
    return query_or_result


# Example Usage
user_prompt = "List employees who know Java"
print(fetch_information(user_prompt))
