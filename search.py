import streamlit as st
import mysql.connector
import pandas as pd
from config import DATABASE_CONFIG

def app():
    st.title("查询租房记录")

    # Function to get database connection
    def get_db_connection():
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection

    with st.form("search_form"):
        user_wechat_id = st.text_input("客户微信备注", "")
        chatbot_wechat_id = st.text_input("你的微信名", "")
        search = st.form_submit_button("搜索")

    if search and user_wechat_id and chatbot_wechat_id:
        query = """
        SELECT Unit.building_name, Unit.unit_number, Unit.rent_price, Unit.floorplan, Unit.available_date
        FROM Unit_user
        JOIN Unit ON Unit_user.unit_id = Unit.unit_id
        WHERE Unit_user.user_wechat_id = %s AND Unit_user.chatbot_wechat_id = %s
        """
        connection = get_db_connection()
        df = pd.read_sql(query, connection, params=(user_wechat_id, chatbot_wechat_id))
        connection.close()
        st.write(df)

if __name__ == "__main__":
    app()
