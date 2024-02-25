import streamlit as st
import mysql.connector
import pandas as pd
from config import DATABASE_CONFIG

def app():
    st.title("查询推房记录")

    # Function to get database connection
    def get_db_connection():
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection

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

    with st.form("search_form"):
        chatbot_wechat_id = st.text_input("你的微信名", "")
        fetch_ids = st.form_submit_button("加载客户微信备注")

    if fetch_ids and chatbot_wechat_id:
        # Fetch and update the user_wechat_ids based on chatbot_wechat_id
        user_wechat_ids = fetch_user_wechat_ids(chatbot_wechat_id)
        st.session_state['user_wechat_ids'] = user_wechat_ids

    if st.session_state['user_wechat_ids']:
        selected_user_wechat_id = st.selectbox("客户微信备注", st.session_state['user_wechat_ids'])
        if st.button("搜索"):
            query = """
            SELECT Unit.building_name, Unit.unit_number, Unit.rent_price, Unit.floorplan, Unit.available_date
            FROM Unit_user
            JOIN Unit ON Unit_user.unit_id = Unit.unit_id
            WHERE Unit_user.user_wechat_id = %s AND Unit_user.chatbot_wechat_id = %s
            """
            connection = get_db_connection()
            df = pd.read_sql(query, connection, params=(selected_user_wechat_id, chatbot_wechat_id))
            connection.close()
            st.write(df)

if __name__ == "__main__":
    app()
