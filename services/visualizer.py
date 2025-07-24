#services/visualizer.py
 
import streamlit as st
import numpy as np
import plotly.express as px
 
def show_visual(df, user_input=""):
    user_input = user_input.lower().strip()
    print("User query:", user_input)  # Debug print
 
    if "pie" in user_input and "bar" not in user_input:
        chart_type = "pie"
    else:
        chart_type = "bar"
 
    if df.shape[1] >= 1:
        label_col = df.columns[0]
        value_col = df.columns[1] if df.shape[1] > 1 else None
 
        st.write(f"Label Column: `{label_col}`")
        if value_col:
            st.write(f"Value Column: `{value_col}`")
 
        # Prepare chart data
        if value_col and np.issubdtype(df[value_col].dtype, np.number):
            chart_data = df.groupby(label_col)[value_col].sum().reset_index()
        else:
            chart_data = df.groupby(label_col).size().reset_index(name='Count')
            value_col = 'Count'
 
        if chart_type == "pie":
            st.subheader("Pie Chart (Plotly)")
           
            fig_pie = px.pie(chart_data, names=label_col, values=value_col, title="Pie Chart")
            st.plotly_chart(fig_pie)
        else:
            st.subheader("Bar Chart (Plotly)")
           
            fig_bar = px.bar(chart_data, x=label_col, y=value_col, color=label_col, title="Bar Chart")
            st.plotly_chart(fig_bar)
 
    else:
        st.warning("Query returned insufficient columns for visualization.")