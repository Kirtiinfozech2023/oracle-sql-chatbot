#import os
from openai import OpenAI
import streamlit as st
#from dotenv import load_dotenv
import pandas as pd
import logging
from services.rag_engine import build_faiss_index, retrieve_context, load_chunks
 
#load_dotenv()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
 
 
# Load and build RAG context
rag_chunks = load_chunks("services/oracle_chatbot_knowledge.txt")
faiss_index, chunk_texts, _ = build_faiss_index(rag_chunks)
 
# Configure logging
logging.basicConfig(
    filename='chatbot_debug.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
 
# Used to classify intent
def classify_intent(user_input):
    logging.info(f"Classifying intent for user input: {user_input}")
    prompt = f"""
Classify the intent of the user message as one of the following:
 
- greeting: Only greetings like \"hi\", \"hello\", \"good morning\", etc., without any database-related ask.
- sql_query: If the message includes any database-related question or request for data, even if it starts with a greeting.
- question: A general question that is not a SQL query.
- irrelevant: Messages not related to data or questions.
 
Examples:
\"Hi, I want to know invoice count\" → sql_query
\"hello\" → greeting
\"What is SQL?\" → question
\"Are you real?\" → irrelevant
 
Now classify this input:
\"{user_input}\"
 
Intent:
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        intent = response.choices[0].message.content.strip().lower()
        logging.info(f"Intent classified as: {intent}")
        return intent
    except Exception as e:
        logging.error(f"Error classifying intent: {e}")
        return "error"
 
# Used to generate greeting reply
def generate_greeting_reply(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a friendly assistant that replies warmly to greetings and encourages users to ask a valid database question."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error generating greeting reply: {e}")
        return "Hello! Please feel free to ask a database-related question."
 
 
 
# Used to generate SQL
def generate_sql(user_input):
    logging.info(f"Generating SQL for input: {user_input}")
    rag_context = "\n".join(retrieve_context(user_input, faiss_index, chunk_texts, top_k=4))
    # Log to console or file for debugging
    print("\n🔍 Retrieved RAG Context:\n", rag_context)
    prompt = f"""
    You are an Oracle SQL expert for a Telecom Tower Billing system. Convert the following natural language question to a valid Oracle SQL query.Only return the SQL starting directly with SELECT. Do not prepend it with 'sql:' or ```sql``` or any explanation.
    Convert the following natural language question into a valid Oracle SQL query.
    Only return the SQL code.
    Use only these tables and columns:
    {rag_context}
    Question: {user_input}
    Only return the SQL code without explanation.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        sql = response.choices[0].message.content.strip()
        logging.info(f"Generated SQL: {sql}")
        if sql.startswith("```sql"):
            sql = sql.split("```sql")[-1].strip("`").strip()
        return sql.rstrip(";")
    except Exception as e:
        logging.error(f"Error generating SQL: {e}")
        return ""
 
# Used to generate explanation
def generate_explanation(df):
    sample_data = df.head(5).to_string(index=False)
    prompt = f"""
You are a business analyst. Provide a short, natural language summary of the business insight from the result below. Do not mention SQL.
Result Preview:
{sample_data}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error generating explanation: {e}")
        return "Explanation generation failed."
    


