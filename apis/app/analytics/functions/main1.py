import json
from openai import OpenAI
from config import OPENAI_API_KEY
from functions import (
    get_project_status,
    allocate_resources,
    get_team_availability,
    get_project_resources,
    get_resources_with_given_skills,
    greeting
)
from ExecuteSQLQuery import answer_user_query, execute_sql_query
from SQLAgent import generate_sql_query

with open("functions.json", "r") as file:
    functions = json.load(file)


FUNCTION_MAP = {
    "get_project_status": get_project_status,
    "allocate_resources": allocate_resources,
    "get_team_availability": get_team_availability,
    "get_project_resources": get_project_resources,
    "get_resources_with_given_skills": get_resources_with_given_skills,
    "greeting": greeting,
}

QUERY_MEMORY = {}

def call_appropriate_function(user_input):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": user_input}],
        functions=functions,
    )
    function_call = response.choices[0].message.function_call
    if function_call:
        function_name = function_call.name
        arguments = function_call.arguments
        try:
            arguments = json.loads(arguments)  
        except json.JSONDecodeError:
            return "Error: Failed to parse function arguments."

        function_map = FUNCTION_MAP

        if function_name in function_map:
            return function_map[function_name](**arguments)
    return None


def fetch_information(user_prompt):
    """Fetches information using functions or SQL query. Returns a meaningful response."""
    
    query_or_result = call_appropriate_function(user_prompt)
    
    if query_or_result:
    
        if isinstance(query_or_result, str) and query_or_result.lower().startswith("select"):
            sql_query = query_or_result
            response = answer_user_query(user_prompt, sql_query)  
            
            if not response:
                return "Sorry, no information is available."
            
            return response
        
        return query_or_result
    else:
        print("Generating through.00000000000000000000000000000.")
        sql_query = generate_sql_query(user_prompt)
        response = answer_user_query(user_prompt, sql_query)  
            
        if not response:
            return "Sorry, no information is available."
            
        return response
        


# Example Usage
# user_prompt = "Which employees are currently unassigned?"
# user_prompt = "can you provide me a list of top 20 employees with max workload"
user_prompt = "Hi"

print(fetch_information(user_prompt))
