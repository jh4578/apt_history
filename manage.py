import streamlit as st
import mysql.connector
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from config import DATABASE_CONFIG


def app():
    st.title("Property Management Dashboard")

    # Function to get database connection
    def get_db_connection():
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection

    # Function to execute read query
    def execute_read_query():
        connection = get_db_connection()
        query = """SELECT * FROM Unit"""  # Adjust the query as needed
        df = pd.read_sql(query, connection)
        connection.close()
        return df

    # Function to execute write query (update, delete)
    def execute_write_query(query):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()

    # Fetch data
    df = execute_read_query()

    # Set up AgGrid options for editable grid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, minWidth=150)
    gb.configure_selection('multiple', use_checkbox=True)
    grid_options = gb.build()

    # Display the grid
    grid_response = AgGrid(
        df, 
        gridOptions=grid_options,
        height=300, 
        width='100%',
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED',
        fit_columns_on_grid_load=True
    )

    if 'data' in grid_response:
        updated_df = grid_response['data']
        if not updated_df.equals(df):
            st.session_state['updated_df'] = updated_df

    # Store selected rows for deletion
    selected = grid_response['selected_rows']
    if selected:
        st.session_state['selected_for_deletion'] = selected
        st.write("Selected rows:", selected)

    # Confirm Update Button
    if st.button('Confirm Update'):
        if 'updated_df' in st.session_state:
            # Truncate the existing table
            truncate_query = "TRUNCATE TABLE Unit"
            execute_write_query(truncate_query)

            # Prepare and execute the insert query for the updated DataFrame
            for i in st.session_state['updated_df'].index:
                columns = ', '.join(st.session_state['updated_df'].columns)
                values = ', '.join([f"'{st.session_state['updated_df'].at[i, col]}'" for col in st.session_state['updated_df'].columns])
                insert_query = f"INSERT INTO Unit ({columns}) VALUES ({values})"
                execute_write_query(insert_query)

            # Execute deletions
            if 'selected_for_deletion' in st.session_state:
                for row in st.session_state['selected_for_deletion']:
                    delete_query = f"DELETE FROM Unit WHERE Unit_ID = {row['Unit_ID']}" # Replace 'ID' with your primary key column name
                    execute_write_query(delete_query)

            st.success("Database Updated Successfully")
            del st.session_state['updated_df']  # Clear the updated data from the session state

if __name__ == "__main__":
    app()
