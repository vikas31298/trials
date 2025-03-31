

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

        function_map = {
            "get_project_status": get_project_status,
            "allocate_resources": allocate_resources,
            "get_team_availability": get_team_availability,
            "get_project_resources": get_project_resources,
            "get_resources_with_given_skills": get_resources_with_given_skills,
        }

        if function_name in function_map:
            return function_map[function_name](**arguments)
    return "Sorry, I didn't understand your question. "

# user_prompt = "is the team orange available during next week?"


user_prompt = "What is capital of India"
print(call_appropriate_function(user_prompt))


def get_project_status(project_id: int):
    return f"Project {project_id} is currently 'In Progress' 🚀"

def allocate_resources(project_id: int):
    return f"Resources have been allocated to Project {project_id} ✅"

def get_team_availability():
    return "Team availability: 3 developers, 2 designers, 1 PM 🏗️"


def get_project_resources(project_name: str):
    return f"I will list the team members working on {project_name}"


def get_resources_with_given_skills(skill_name:str):
    return f"I will list the team members who posses the {skill_name}"



