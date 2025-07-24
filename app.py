# app.py
import streamlit as st
from services.db import run_query
from services.openai import generate_sql, generate_explanation, classify_intent, generate_greeting_reply
#from services.visualizer_altair import auto_plot
import numpy as np
import plotly.express as px
from services.visualizer import show_visual



st.title("Natural Language to Oracle SQL Chatbot")


user_input = st.text_input("Ask your question (e.g. How many invoices this month?)")

if st.button("Run Query") and user_input:
    intent = classify_intent(user_input)

    if intent in ["greeting", "irrelevant"]:
        st.markdown("👋 Hi there! Nice to hear from you. Please ask a valid invoice-related question.")

    elif intent == "question":
        st.warning("Please enter a valid database-related question.")

    elif intent == "sql_query":
        sql_query = generate_sql(user_input)
        st.code(sql_query, language="sql")

        if any(word in sql_query.lower() for word in ["insert", "update", "delete"]):
            st.error("❌ Modification queries like INSERT, UPDATE, DELETE are not allowed.")
        else:
            try:
                result = run_query(sql_query)
                if result.empty:
                    st.info("No results found.")
                else:
                    st.subheader("Query Result")
                    st.dataframe(result)

                    st.subheader(" Explanation")
                    st.markdown(generate_explanation(result))

                    st.subheader("Visualization")
                    if "pie" in user_input:
                            chart_type = "pie"
                    elif "line" in user_input:
                            chart_type = "line"
                    else:
                            chart_type = "bar"
 
                    if result.shape[1] >= 1:
                            label_col = result.columns[0]
                            value_col = result.columns[1] if result.shape[1] > 1 else None
 
                            st.write(f"Label Column: `{label_col}`")
                            if value_col:
                                st.write(f"Value Column: `{value_col}`")
 
                            # Prepare chart data
                            if value_col and np.issubdtype(result[value_col].dtype, np.number):
                                chart_data = result.groupby(label_col)[value_col].sum().reset_index()
                            else:
                                chart_data = result.groupby(label_col).size().reset_index(name='Count')
                                value_col = 'Count'
 
                            if chart_type == "pie":
                                st.subheader("Pie Chart (Plotly)")
                                fig_pie = px.pie(chart_data, names=label_col, values=value_col, title="Pie Chart")
                                st.plotly_chart(fig_pie)
                            elif chart_type == "line":
                                st.subheader("Line Chart (Plotly)")
                                fig_line = px.line(chart_data, x=label_col, y=value_col, title="Line Chart")
                                st.plotly_chart(fig_line)
                            else:
                                st.subheader("Bar Chart (Plotly)")
                                fig_bar = px.bar(chart_data, x=label_col, y=value_col, color=label_col, title="Bar Chart")
                                st.plotly_chart(fig_bar)
            except Exception as e:
                st.error(f"Error running query: {e}")
