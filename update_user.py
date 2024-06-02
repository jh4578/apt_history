import streamlit as st
import mysql.connector
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from config import DATABASE_CONFIG
    
def app():
    st.title("推房管理")

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
        
    def get_unique_building_names():
        query = "SELECT DISTINCT building_name FROM Unit"
        df = execute_read_query(query)
        return df['building_name'].tolist()

    def delete_record(user_wechat_id, chatbot_wechat_id):
        if user_wechat_id and chatbot_wechat_id:
            query = "DELETE FROM Unit_user WHERE user_wechat_id = %s AND chatbot_wechat_id = %s"
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(query, (user_wechat_id, chatbot_wechat_id))
            connection.commit()  # 不要忘记提交更改
            connection.close()
            st.success("记录已删除")  # 反馈删除操作成功


    # Function to get database connection
    def get_db_connection():
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection

    def get_chatbot_wx_ids():
        query = "SELECT DISTINCT chatbot_wx_id FROM user WHERE chatbot_wx_id IS NOT NULL"
        connection = get_db_connection()
        df = pd.read_sql(query, connection)
        connection.close()
        return df['chatbot_wx_id'].tolist()

    # Function to fetch user_wechat_ids for a given chatbot_wechat_id
    def fetch_user_wechat_ids(chatbot_wechat_id):
        if chatbot_wechat_id:
            query = "SELECT DISTINCT user_wechat_id FROM Unit_user WHERE chatbot_wechat_id = %s"
            connection = get_db_connection()
            df = pd.read_sql(query, connection, params=(chatbot_wechat_id,))
            connection.close()
            return df['user_wechat_id'].tolist()
        return []

    # Initialize or update session state for user_wechat_ids
    if 'user_wechat_ids' not in st.session_state:
        st.session_state['user_wechat_ids'] = []

    with st.form("search"):
        st.write("推房记录")
        chatbot_wx_ids = get_chatbot_wx_ids()
        chatbot_wechat_id = st.selectbox("Chatbot 微信ID", ['Any'] + chatbot_wx_ids)
        fetch_ids = st.form_submit_button("加载客户微信备注")

    if fetch_ids and chatbot_wechat_id:
        # Fetch and update the user_wechat_ids based on chatbot_wechat_id
        user_wechat_ids = fetch_user_wechat_ids(chatbot_wechat_id)
        st.session_state['user_wechat_ids'] = user_wechat_ids

    if st.session_state['user_wechat_ids']:
        selected_user_wechat_id = st.selectbox("客户微信备注", st.session_state['user_wechat_ids'])
        if st.button("搜索"):
            query = """
            SELECT Unit.building_name, Unit.unit_number, Unit.rent_price, Unit.floorplan, Unit.available_date, Unit.direction, Unit.unit_id 
            FROM Unit_user
            JOIN Unit ON Unit_user.unit_id = Unit.unit_id
            WHERE Unit_user.user_wechat_id = %s AND Unit_user.chatbot_wechat_id = %s
            """
            connection = get_db_connection()
            df = pd.read_sql(query, connection, params=(selected_user_wechat_id, chatbot_wechat_id))
            connection.close()
            st.write(df)
            
        if st.button("删除记录"):
            # 调用删除记录的函数
            delete_record(selected_user_wechat_id, chatbot_wechat_id)
            # 更新 session state 中的 user_wechat_ids，因为记录已被删除
            user_wechat_ids = fetch_user_wechat_ids(chatbot_wechat_id)
            st.session_state['user_wechat_ids'] = user_wechat_ids
    with st.form("search_form"):
        chatbot_wx_ids = get_chatbot_wx_ids()
        chatbot_wx_id = st.selectbox("Chatbot 微信ID", ['Any'] + chatbot_wx_ids)
        sche_listing_options = ["Any", "Yes", "No"]
        chatbot_on = st.selectbox("Chatbot_on", options=sche_listing_options)
        search_user = st.form_submit_button("显示表格")

    # Handle Search
    if search_user:
        search_query = """
        SELECT wechat_id, preference, chatbot_wx_id, chatbot_on, sche_listing, is_group, no_building, conversation, frequency, last_sent, user_id
        FROM user
        WHERE 1=1
        """
        if chatbot_wx_id != 'Any':
            search_query += f" AND chatbot_wx_id = '{chatbot_wx_id}'"

        if chatbot_on != "Any":
            chatbot_on = 1 if chatbot_on == "Yes" else 0
            search_query += f" AND chatbot_on = {chatbot_on}"

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
                        'wechat_id': 'wechat_id',
                        'chatbot_wx_id': 'chatbot_wx_id',
                        'sche_listing': 'sche_listing',
                        'is_group':'is_group',
                        'no_building':'no_building',
                        'frequency':'frequency',
                        'last_sent':'last_sent',
                        'chatbot_on':'chatbot_on'
                    }

                    for i in updated_df.index:
                        user_update_query = "UPDATE user SET "
                        user_update_query += ", ".join([f"{user_column_name_mapping[col]} = '{updated_df.at[i, col]}'" for col in updated_df.columns if col in user_column_name_mapping])
                        user_update_query += f" WHERE user_id = {updated_df.at[i, 'user_id']}"
                        execute_write_query(user_update_query)
                    st.success("更新成功！")

        selected = grid_response['selected_rows']
        print(selected)
        if len(selected) > 0:
            st.session_state['selected_for_deletion'] = selected
            
            # # if st.button("添加已推荐大楼"):
            # selected_building = selected[0]
            # building_names = get_unique_building_names()  # 从数据库获取所有唯一的楼名
            
            # # 使用multiselect让用户可以选择多个楼名
            # new_building_names = st.multiselect("选择楼名", options=building_names)
            
            # # 显示一个按钮让用户提交更新
            # if st.button("更新已推大楼"):
            #     # 将用户选择的楼名列表转换成字符串
            #     no_building_str = ', '.join(new_building_names)
                
            #     # 假设'user_id'是选中行中用户的唯一标识符
            #     user_id = selected_building.get("user_id")
            #     update_query = f"""
            #     UPDATE user
            #     SET no_building = '{no_building_str}'
            #     WHERE user_id = {user_id}
            #     """
            #     execute_write_query(update_query)
            #     st.success("楼名更新成功！")
                
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
        frequency = st.number_input("推房频率", min_value=1, step=1, format='%d')
        
        building_names = get_unique_building_names()  # 从数据库获取所有唯一的楼名
        new_nobuilding = st.multiselect("不要推的大楼", options=building_names, default = [])
        chatbot_on = st.checkbox("chatbot_on",value = False)
        is_group = st.checkbox('群聊',value = False)
        
        # 提交按钮
        submit_new_user = st.form_submit_button("添加用户")
        
    if submit_new_user:
        no_building_str = ', '.join(new_nobuilding)
        # 插入新用户数据到数据库
        insert_query = f"""
        INSERT INTO user (wechat_id, preference, chatbot_wx_id, chatbot_on, is_group, no_building, frequency)
        VALUES ('{new_wechat_id}', '{new_preference}', '{new_chatbot_wx_id}', {chatbot_on}, {is_group}, '{no_building_str}',{frequency})
        """
        execute_write_query(insert_query)
        st.success("用户添加成功！")

    

if __name__ == "__main__":
    app()
