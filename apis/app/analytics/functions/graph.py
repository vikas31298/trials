import json
import logging
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langgraph.prebuilt import StateGraph
from config import OPENAI_API_KEY
from functions import *
from ExecuteSQLQuery import answer_user_query

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load function mapping JSON
with open("functions.json", "r") as file:
    functions = json.load(file)

# Define function mappings
function_map = {
    "get_project_status": get_project_status,
    "allocate_resources": allocate_resources,
    "get_team_availability": get_team_availability,
    "get_project_resources": get_project_resources,
    "get_resources_with_given_skills": get_resources_with_given_skills,
}

# Define state model for LangGraph
class AgentState(BaseModel):
    user_query: str
    function_response: str = None
    graph_response: str = None
    sql_query: str = None
    final_response: str = None

# Initialize OpenAI LLM
llm = ChatOpenAI(model_name="gpt-4-turbo", api_key=OPENAI_API_KEY)

# Step 1: Try to map the function
def call_appropriate_function(state: AgentState) -> AgentState:
    logging.info(f"Checking if a function exists for: {state.user_query}")
    
    response = llm.predict(
        f"Given the user query: '{state.user_query}', which function should be used? If none, return 'None'."
    )
    
    function_name = response.strip()
    
    if function_name in function_map:
        state.function_response = function_map[function_name]()
        logging.info(f"Function found: {function_name}, executing...")
    else:
        state.function_response = None
        logging.info("No matching function found.")
    
    return state

# Step 2: Query LangGraph for existing knowledge
def query_langgraph(state: AgentState) -> AgentState:
    if state.function_response:
        return state  # Skip if function response is found

    logging.info("Checking LangGraph for relevant information...")
    
    graph_ai = llm.predict(
        f"Check in LangGraph knowledge base for: '{state.user_query}'"
    )

    if graph_ai and "not found" not in graph_ai.lower():
        state.graph_response = graph_ai
        logging.info("Knowledge found in LangGraph.")
    else:
        state.graph_response = None
        logging.info("No relevant data in LangGraph.")

    return state

# Step 3: Generate SQL Query
def generate_sql_query(state: AgentState) -> AgentState:
    if state.function_response or state.graph_response:
        return state  # Skip if prior step has an answer

    logging.info("Generating SQL query...")
    
    sql_query = llm.predict(
        f"Generate an SQL query to retrieve information for: '{state.user_query}'"
    )

    state.sql_query = sql_query
    return state

# Step 4: Execute SQL Query
def execute_sql(state: AgentState) -> AgentState:
    if state.function_response or state.graph_response:
        return state  # Skip if prior step has an answer

    if not state.sql_query:
        state.final_response = "Sorry, no information is available."
        return state

    logging.info(f"Executing SQL query: {state.sql_query}")
    sql_result = answer_user_query(state.sql_query)

    if sql_result:
        state.final_response = sql_result
        logging.info("SQL query returned data.")
    else:
        state.final_response = "Sorry, no information is available."
        logging.info("SQL query did not return relevant data.")

    return state

# Step 5: Final Response Handling
def return_final_response(state: AgentState) -> AgentState:
    if state.function_response:
        state.final_response = state.function_response
    elif state.graph_response:
        state.final_response = state.graph_response
    elif state.sql_query:
        state.final_response = answer_user_query(state.sql_query)

    if not state.final_response:
        state.final_response = "Sorry, no information is available."

    return state

# Create LangGraph Workflow
workflow = StateGraph(AgentState)

workflow.add_node("call_function", call_appropriate_function)
workflow.add_node("query_graph", query_langgraph)
workflow.add_node("generate_sql", generate_sql_query)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("final_response", return_final_response)

workflow.add_edge("call_function", "query_graph")
workflow.add_edge("query_graph", "generate_sql")
workflow.add_edge("generate_sql", "execute_sql")
workflow.add_edge("execute_sql", "final_response")

workflow.set_entry_point("call_function")

# Instantiate LangGraph Executor
executor = workflow.compile()

# Function to process user input
def process_query(user_input):
    initial_state = AgentState(user_query=user_input)
    final_state = executor.invoke(initial_state)
    return final_state.final_response

# Example usage
user_prompt = "when did project alpha start"
response = process_query(user_prompt)
print(response)
