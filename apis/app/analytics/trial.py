from openai import OpenAI


def get_project_status(project_id: int):
    return f"Project {project_id} is currently 'In Progress' 🚀"

def allocate_resources(project_id: int):
    return f"Resources have been allocated to Project {project_id} ✅"

def get_team_availability():
    return "Team availability: 3 developers, 2 designers, 1 PM 🏗️"


functions = [
    {
        "name": "get_project_status",
        "description": "Get the status of a project.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "integer", "description": "The project ID"},
            },
            "required": ["project_id"],
        },
    },
    {
        "name": "allocate_resources",
        "description": "Allocate resources to a project.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {"type": "integer", "description": "The project ID"},
            },
            "required": ["project_id"],
        },
    },
    {
        "name": "get_team_availability",
        "description": "Get team availability details.",
        "parameters": {}
    }
]


def call_appropriate_function(user_input):
    client = OpenAI(api_key="your-openai-api-key")

    # Send user prompt to LLM and get function call suggestion
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": user_input}],
        functions=functions,
    )

    # Extract function call
    function_call = response.choices[0].message.function_call

    if function_call:
        function_name = function_call.name
        arguments = function_call.arguments

        # Dynamically call the function
        function_map = {
            "get_project_status": get_project_status,
            "allocate_resources": allocate_resources,
            "get_team_availability": get_team_availability,
        }

        if function_name in function_map:
            return function_map[function_name](**arguments)

    return "No relevant function found 🤖"

# Example usage
user_prompt = "What is the status of project 123?"
print(call_appropriate_function(user_prompt))
