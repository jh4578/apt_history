import streamlit as st
import mysql.connector
from datetime import datetime
from config import DATABASE_CONFIG

def app():
    st.title("添加公寓")
    
    # Function to get database connection
    def get_db_connection():
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection

    def get_builidng_name():
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
    
    # Function to add a unit
    def add_building():
       
        with st.form("building_form"):
            col1, col2 = st.columns(2)
    
            with col1:
                # Column 1 fields
                building_name = st.text_input("大楼名称")
                website = st.text_input("大楼网站")
                location = st.selectbox("区域", ["New Jersey", "Manhattan upper", "Manhattan mid", "Manhattan lower", "LIC", "Brooklyn", "Bronx", "Queens", "Other"])
                address = st.text_input("详细地址")
                city = st.text_input("城市")
                state = st.text_input("州")
                zipcode = st.text_input("邮编")
                building_description = st.text_area("大楼介绍")
    
            with col2:
                # Column 2 fields
                building_location_image = st.text_input("大楼位置图片url")
                amenity_image = st.text_input("设施图片url")
                washer_dryer_image = st.text_input("洗烘设备url")
                pet = st.checkbox("宠物友好", value=False)
                application_material = st.text_area("申请材料")
                guarantee_policy = st.text_area("担保政策")
    
            building_form_submitted = st.form_submit_button("添加公寓")
            
            if building_form_submitted:
                
                try:
                    connection = get_db_connection()
                    cursor = connection.cursor()

                    building_insert_query = """
                        INSERT INTO Building (
                            building_name, website, location, address, city, state, zipcode, building_description, 
                            building_location_image, pet, 
                            application_material, amenity_image, washer_dryer_image, guarantee_policy 
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(building_insert_query, (
                        building_name, website, location, address, city, state, zipcode, building_description, 
                        building_location_image, pet, 
                        application_material, amenity_image, washer_dryer_image, guarantee_policy 
                    ))
    
                    connection.commit()
                    
                    st.success("大楼信息已成功添加！")
                    
                except mysql.connector.Error as e:
                    st.error(f"数据库错误: {e}")
                finally:
                    cursor.close()
                    connection.close()    

        
    # Call the function to render the form
    add_building()

if __name__ == "__main__":
    app()

