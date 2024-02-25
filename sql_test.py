import streamlit as st
import mysql.connector
import pandas as pd
from config import DATABASE_CONFIG
def app():
    st.title("Search Data")

    # Function to get database connection
    def get_db_connection():
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection

    # Text area for SQL query
    query = st.text_area("Enter your SQL query", height=150)
    execute_query = st.button("Execute Query")

    if execute_query:
        if query:
            try:
                # Connection to the database
                connection = get_db_connection()
                # Executing the query
                df = pd.read_sql(query, connection)
                st.write(df)
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                connection.close()
        else:
            st.error("Please enter a SQL query.")

if __name__ == "__main__":
    app()
