from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize LLM
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

# Predefined query-to-function mapping
query_intent_mapping = {
    "monthly sales report": "get_monthly_sales_report",
    "top customers by revenue": "get_top_customers",
    "total sales for the year": "get_annual_sales",
}

def classify_query(state):
    user_query = state["query"].lower()
    
    for key in query_intent_mapping:
        if key in user_query:
            return {"type": "function", "function_name": query_intent_mapping[key]}
    
    sql_pattern = r"\b(select|from|where|join|insert|update|delete)\b"
    if re.search(sql_pattern, user_query, re.IGNORECASE):
        return {"type": "sql"}
    
    return {"type": "natural_language"}

def execute_function(state):
    function_name = state["function_name"]
    function_results = {
        "get_monthly_sales_report": "Here is the sales report for this month.",
        "get_top_customers": "Top 10 customers based on revenue are: A, B, C...",
        "get_annual_sales": "Total sales for the year is $5M.",
    }
    return {"response": function_results.get(function_name, "Function not found.")}

def generate_and_run_sql(state):
    user_query = state["query"]
    sql_prompt = PromptTemplate(
        input_variables=["question"],
        template="Convert the following natural language question into an SQL query: {question}"
    )
    sql_chain = LLMChain(llm=llm, prompt=sql_prompt)
    sql_query = sql_chain.run(question=user_query)
    
    def execute_sql_query(query):
        return f"Executed SQL: {query} (Results: XYZ)"
    
    return {"response": execute_sql_query(sql_query)}

def generate_natural_response(state):
    return {"response": llm.invoke(state["query"]) }

# Define workflow
graph = StateGraph()
graph.add_node("classify", classify_query)
graph.add_node("execute_function", execute_function)
graph.add_node("generate_and_run_sql", generate_and_run_sql)
graph.add_node("generate_natural_response", generate_natural_response)

graph.add_edge("classify", "execute_function", condition=lambda state: state["type"] == "function")
graph.add_edge("classify", "generate_and_run_sql", condition=lambda state: state["type"] == "sql")
graph.add_edge("classify", "generate_natural_response", condition=lambda state: state["type"] == "natural_language")

graph.set_entry_point("classify")
app = graph.compile()

# Example queries
queries = [
    {"query": "Show me the monthly sales report."},
    {"query": "What were the total sales last year?"},
    {"query": "Which product has the best ROI?"},
]

# Run the queries
for query in queries:
    print(app.invoke(query))
