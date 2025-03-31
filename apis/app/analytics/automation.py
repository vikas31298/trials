from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from sqlalchemy.orm import Session
from models import Resource, Task, SessionLocal

# Initialize LLM agent (GPT-4, Llama2, etc.)
llm = ChatOpenAI(model="gpt-4", temperature=0.5)

# Memory to track ongoing decisions
memory = ConversationBufferMemory(memory_key="chat_history")

def assign_resource_agent(task_id: int):
    session = SessionLocal()
    task = session.query(Task).filter(Task.id == task_id).first()
    if not task:
        return "Task not found."
    
    available_resources = session.query(Resource).filter(Resource.availability == True).all()

    # Convert resource data to text format for LLM reasoning
    resource_data = "\n".join(
        [f"ID: {r.id}, Name: {r.name}, Skillset: {r.skillset}, Workload: {r.workload}" for r in available_resources]
    )

    # LLM prompt
    prompt = f"""
    Given the following available resources:

    {resource_data}

    And the task details:
    Task ID: {task.id}, Name: {task.name}, Complexity: {task.complexity}, Estimated Hours: {task.estimated_hours}

    Select the best resource for this task based on skill match and workload balance.
    """
    
    decision = llm.predict(prompt)  # AI decides who to assign
    print(f"Agent Decision: {decision}")

    # Extract selected resource
    selected_resource = None
    for r in available_resources:
        if r.name in decision:
            selected_resource = r
            break

    if selected_resource:
        task.resource_id = selected_resource.id
        selected_resource.workload += task.estimated_hours / 40  # Workload update
        session.commit()
        return f"Task '{task.name}' assigned to {selected_resource.name}."
    
    return "No suitable resource found."

def detect_bottleneck_agent():
    session = SessionLocal()
    resources = session.query(Resource).all()
    
    bottleneck_resources = []
    for resource in resources:
        if resource.workload > 0.85:  # AI detects bottleneck
            bottleneck_resources.append(resource.name)
    
    if bottleneck_resources:
        hiring_suggestion = llm.predict(f"The following resources are overloaded: {bottleneck_resources}. Should we hire?")
        return f"Bottlenecks detected: {bottleneck_resources}. AI Suggests: {hiring_suggestion}"
    
    return "No bottlenecks detected."

def reassign_tasks_agent(resource_id: int):
    session = SessionLocal()
    resource = session.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource or resource.availability:
        return "Resource is still available."

    # Get tasks that need reassignment
    tasks = session.query(Task).filter(Task.resource_id == resource.id).all()
    
    if not tasks:
        return "No tasks to reassign."

    # Find new suitable resources
    available_resources = session.query(Resource).filter(Resource.availability == True).all()
    
    reassignments = []
    for task in tasks:
        best_match = llm.predict(f"""
        We need to reassign '{task.name}' (complexity: {task.complexity}, hours: {task.estimated_hours}).
        Available resources: {[(r.name, r.skillset, r.workload) for r in available_resources]}

        Choose the best replacement.
        """)
        
        # Extract best resource
        selected_resource = None
        for r in available_resources:
            if r.name in best_match:
                selected_resource = r
                break

        if selected_resource:
            task.resource_id = selected_resource.id
            selected_resource.workload += task.estimated_hours / 40  # Workload update
            reassignments.append(f"{task.name} -> {selected_resource.name}")

    session.commit()
    return f"Reassigned tasks: {reassignments}" if reassignments else "No suitable replacements found."
