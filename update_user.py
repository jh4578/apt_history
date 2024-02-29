import streamlit as st
import mysql.connector
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from config import DATABASE_CONFIG
    
def app():
    st.title("更新User")

    # Function to get database connection
    def get_db_connection():
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection

    # Function to execute read query
    def execute_read_query(query=None):
        # st.write(query)
        connection = get_db_connection()
        if query is None:
            # Adjust this default query as per your requirements
            query = """
            SELECT Unit.*, Building.building_name, Building.location
            FROM Unit
            JOIN Building ON Unit.building_id = Building.building_id
            """
        df = pd.read_sql(query, connection)
        connection.close()
        return df

    # Function to execute write query (update, delete)
    def execute_write_query(query):
        # st.write(query)
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()

    def get_chatbot_wx_ids():
        query = "SELECT DISTINCT chatbot_wx_id FROM user WHERE chatbot_wx_id IS NOT NULL"
        df = execute_read_query(query)
        return df['chatbot_wx_id'].tolist()
        
    with st.form("search_form"):
        chatbot_wx_ids = get_chatbot_wx_ids()
        chatbot_wx_id = st.selectbox("Chatbot 微信ID", ['Any'] + chatbot_wx_ids)
        sche_listing_options = ["Any", "Yes", "No"]
        sche_listing = st.selectbox("是否推房", options=sche_listing_options)
        search_user = st.form_submit_button("显示表格")

    # Handle Search
    if search_user:
        search_query = """
        SELECT user_id, preference, roommate_preference, sex, wechat_id, conversation, chatbot_wx_id, sche_listing, is_group
        FROM user
        WHERE 1=1
        """
        if chatbot_wx_id != 'Any':
            search_query += f" AND chatbot_wx_id = '{chatbot_wx_id}'"

        if sche_listing != "Any":
            sche_listing_value = 1 if sche_listing == "Yes" else 0
            search_query += f" AND sche_listing = {sche_listing_value}"

        df = execute_read_query(search_query)
        st.session_state['search_results'] = df

    # Display Search Results
    if 'search_results' in st.session_state:
        df = st.session_state['search_results']

        # Set up AgGrid options for editable grid
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=True, minWidth=150)
        gb.configure_selection('multiple', use_checkbox=True)
        grid_options = gb.build()

        # Display the grid
        grid_response = AgGrid(
            df, 
            gridOptions=grid_options,
            height=400, 
            width='100%',
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED',
            fit_columns_on_grid_load=True
        )

        if 'data' in grid_response:
            updated_df = grid_response['data']
            if not updated_df.equals(df):
                if st.button('更新'):
                    user_column_name_mapping = {
                        'preference': 'preference',
                        'roommate_preference': 'roommate_preference',
                        'sex': 'sex',
                        'wechat_id': 'wechat_id',
                        'chatbot_wx_id': 'chatbot_wx_id',
                        'sche_listing': 'sche_listing',
                        'is_group':'is_group'
                    }

                    for i in updated_df.index:
                        user_update_query = "UPDATE user SET "
                        user_update_query += ", ".join([f"{user_column_name_mapping[col]} = '{updated_df.at[i, col]}'" for col in updated_df.columns if col in user_column_name_mapping])
                        user_update_query += f" WHERE user_id = {updated_df.at[i, 'user_id']}"
                        execute_write_query(user_update_query)
                    st.success("更新成功！")

        selected = grid_response['selected_rows']
        if selected:
            st.session_state['selected_for_deletion'] = selected
            
            if st.button('删除'):
                for row in st.session_state['selected_for_deletion']:
                    user_delete_query = f"DELETE FROM user WHERE user_id = {row['user_id']}"
                    execute_write_query(user_delete_query)
                st.success("删除成功！")
    
    with st.form("add_user_form"):
        st.write("添加新用户")
        # 添加字段
        new_wechat_id = st.text_input("客人备注名", "")
        new_preference = st.text_input("租房需求", "")
        # new_roommate_preference = st.text_input("室友偏好", "")
        # new_sex = st.selectbox("性别", ["", "Male", "Female", "Other"])
        new_chatbot_wx_id = st.text_input("Chatbot昵称", "")
        new_sche_listing = st.checkbox("定时推房",value = False)
        is_group = st.checkbox('群聊',value = False)
        
        # 提交按钮
        submit_new_user = st.form_submit_button("添加用户")
        
    if submit_new_user:
       
        # 插入新用户数据到数据库
        insert_query = f"""
        INSERT INTO user (wechat_id, preference, chatbot_wx_id, sche_listing,is_group)
        VALUES ('{new_wechat_id}', '{new_preference}', '{new_chatbot_wx_id}', {new_sche_listing},{is_group})
        """
        execute_write_query(insert_query)
        st.success("用户添加成功！")
       

if __name__ == "__main__":
    app()
