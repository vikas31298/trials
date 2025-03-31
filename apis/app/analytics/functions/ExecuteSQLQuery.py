import psycopg2
from langchain_openai.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from config import OPENAI_API_KEY, DATABASE_URL

# Initialize LLM
llm = ChatOpenAI(model="gpt-4-turbo")
# , openai_api_key=OPENAI_API_KEY)

def generate_sql_query(user_prompt: str) -> str:
    """Use GPT to generate an SQL query from a natural language user prompt."""
    system_message = SystemMessage(content="""
    You are an expert SQL assistant. Convert natural language queries into SQL queries.
    Only return the SQL query without any explanations. Assume the table names based on the query context.
    """)
    user_message = HumanMessage(content=f"Convert this request into an SQL query: {user_prompt}")

    response = llm.invoke([system_message, user_message])
    return response.content.strip()


def execute_sql_query(query: str):
    """Executes the given SQL query on the database and returns the results."""
    try:
        
        print(DATABASE_URL)
        print(query)
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(query)
        
        if query.lower().startswith("select"):
            results = cursor.fetchall()
        else:
            conn.commit()  # Commit for INSERT, UPDATE, DELETE queries
            results = "Query executed successfully."

        cursor.close()
        conn.close()
        return results
    except Exception as e:
        return f"Error executing query: {str(e)}"


def answer_user_query(user_prompt: str, sql_query: str) -> str:
    
    
    """Combines SQL generation, execution, and AI-based response interpretation."""
    
    # sql_query = generate_sql_query(user_prompt)  # Generate SQL dynamically
    print(f"Generated SQL Query: {sql_query}")  # Debugging

    results = execute_sql_query(sql_query)

    # If the query fails, return an error message
    if isinstance(results, str) and results.startswith("Error"):
        return results

    # Convert SQL results into a user-friendly response
    ai_prompt = f"""
    User asked: '{user_prompt}'
    SQL Query: '{sql_query}'
    Database Results: {results}
    
    Provide a user-friendly response summarizing the results.
    """
    response = llm.invoke([HumanMessage(content=ai_prompt)])

    return response.content.strip()


