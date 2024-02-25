import streamlit as st
# import insert_build
import insert_build
import insert_unit
import search
import sql_test
import update_user
import manage
import hmac

st.set_page_config(layout="wide", initial_sidebar_state="auto")
st.title("房源数据管理")

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        entered_username = st.session_state["username"]
        entered_password = st.session_state["password"]
    
        # Check if the entered username exists in the secrets
        if entered_username in st.secrets["users"]:
            # Compare the entered password with the stored one
            correct_password = st.secrets["users"][entered_username]
            if hmac.compare_digest(entered_password, correct_password):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the username or password.
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

if not check_password():
    st.stop()

def logout():
    # Reset or remove login-related session state variables
    for key in ['password_correct', 'username', 'password']:
        if key in st.session_state:
            del st.session_state[key]

if 'password_correct' in st.session_state and st.session_state['password_correct']:
    def main():
    
        st.sidebar.title("目录")
        choice = st.sidebar.selectbox("选择", ["搜索房源", "更新User","添加公寓", "添加单元", "测试"])
        
        if choice == "搜索房源":
            search.app()
        elif choice == "添加公寓":
            insert_build.app()
        elif choice == "添加单元":
            insert_unit.app()
        elif choice == "测试":
            sql_test.app()
        elif choice == "更新User":
            update_user.app()
        
    if __name__ == "__main__":
        main()

    st.header('')
    st.header('')
    st.header('')
    st.header('')
    st.header('')
    # col1, col2 = st.columns([0.88, 0.12])
    # with col2:
    #     if st.button('**Logout**', type="primary"):
    #         logout()
    #         st.experimental_rerun()

    col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
    # col1, col2, col3 = st.beta_columns([1,1,1])
    
    with col2:
        if st.button('**Logout**', type="primary"):
            logout()
            st.experimental_rerun()
