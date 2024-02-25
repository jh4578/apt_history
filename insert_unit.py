import streamlit as st
import mysql.connector
from datetime import datetime
from config import DATABASE_CONFIG


def app():
    st.title("添加单元")
    
    # Function to get database connection
    def get_db_connection():
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection

    def get_building_name():
        connection = get_db_connection()
        cursor = connection.cursor()
        building_name_options = ['other']
        # Check if the building exists
        cursor.execute("SELECT Building_name FROM Building")
        building_names = cursor.fetchall()
        for building_name in building_names:
            building_name_options.append(building_name[0])

        connection.close()
        return building_name_options
        
    def add_unit():
        if 'unit_data' not in st.session_state:
            st.session_state['unit_data'] = None
        with st.form("add_unit_form"):
            col1, col2 = st.columns(2)
    
            with col1:
                # Column 1 fields
                building_name_options = get_building_name()
                building_name = st.selectbox("公寓名称", building_name_options)
                unit_number = st.text_input("单元号")
                rent_price = st.number_input("租金", min_value=0)
                floorplan = st.selectbox("户型", ['Studio', '1b1b', '2b2b', '2b1b', '3b2b', '3b3b', '4b3b', 'other'])
                available_date = st.date_input("起租日期")
                size = st.number_input("单元面积", min_value=0)
                washer_dryer = st.checkbox("室内洗烘", value=False)
                
    
            with col2:
                # Column 2 fields
                # unit_image = st.text_input("单元图片URL")
                unit_video = st.text_input("单元视频URL")
                floorplan_image = st.text_input("户型图URL")
                direction = st.selectbox("房间朝向", ["N", "S", "E", "W", "NE", "NW", "SE", "SW"])
                concession = st.text_input("优惠政策")
                broker_fee = st.number_input("中介费", min_value=0)
                interest_pp_num = st.number_input("在拼人数", min_value=0)
                on_market = st.checkbox("On Market", value=False)
                
            unit_description = st.text_area("单元描述")
    
            unit_form_submitted = st.form_submit_button("添加单元")
            
        if unit_form_submitted:         

            # Assuming you have a function to handle the database connection
            connection = get_db_connection()   
            cursor = connection.cursor()

            # Check if the building exists
            cursor.execute("SELECT Building_ID FROM Building WHERE Building_name = %s", (building_name,))
            building = cursor.fetchone()

            if not building:
                st.warning("请先添加公寓信息")
        
            else:
                building_id = building[0]
                unit_insert_query = """
                    INSERT INTO Unit (
                        building_id, unit_number, rent_price, floorplan, floorplan_image, 
                        size, concession, direction,unit_video, unit_description, broker_fee,  
                        available_date, washer_dryer, interest_pp_num,on_market
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(unit_insert_query, (
                    building_id, unit_number, rent_price, floorplan, floorplan_image, 
                    size, concession, direction,unit_video, unit_description, broker_fee,  
                    available_date, washer_dryer, interest_pp_num, on_market
                ))
    
                # Commit transaction and close connection
                connection.commit()
                cursor.close()
                connection.close()
                
    
                st.success("单元已成功添加!")
                
        
    # Call the function to render the form
    add_unit()

if __name__ == "__main__":
    app()

