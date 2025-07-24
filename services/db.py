import oracledb
import streamlit as st
#import os
#from dotenv import load_dotenv
import pandas as pd
# Load environment variables
#load_dotenv()

# Read values
ORACLE_USER = st.secrets["ORACLE_USER"]
ORACLE_PASSWORD = st.secrets["ORACLE_PASSWORD"]
ORACLE_HOST = st.secrets["ORACLE_HOST"]
ORACLE_PORT = st.secrets["ORACLE_PORT"]
ORACLE_SID = st.secrets["ORACLE_SID"]

# Build DSN
ORACLE_DSN = oracledb.makedsn(ORACLE_HOST, ORACLE_PORT, sid=ORACLE_SID)

def get_connection():
    """Return a connection to Oracle DB"""
    return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)

def run_query(sql):
    """Execute SQL and return dataframe"""
   
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    cursor.close()
    conn.close()
    return df
