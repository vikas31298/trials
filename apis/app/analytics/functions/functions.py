
def get_project_status(project_id: int):
    return f"Project {project_id} is currently 'In Progress' 🚀"

def allocate_resources(project_id: int):
    return f"Resources have been allocated to Project {project_id} ✅"

def get_team_availability():
    return "Team availability: 3 developers, 2 designers, 1 PM 🏗️"


def get_project_resources(project_name: str):
    return f"I will list the team members working on {project_name}"


def get_resources_with_given_skills(skill_name:str):
    print(f"I will list the team members who posses the {skill_name}")
    
    return f"SELECT * FROM resourcifyschema.person where skills like '%{skill_name}%'"


def greeting(greeting_text:str):
    user_input = greeting_text
    greetings = ["hi", "hello", "hey", "hola", "greetings"]
    user_input_lower = user_input.lower()

    if any(greeting in user_input_lower for greeting in greetings):
        return "Hello! How can I assist you today?"
    else:
        return "I didn't quite catch that. How can I help you?"


