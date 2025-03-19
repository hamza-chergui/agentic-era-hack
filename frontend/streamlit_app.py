import streamlit as st
from frontend.chatbot import chatbot_page
from frontend.courses import courses_page
from frontend.tests import tests_page

def main():
    st.set_page_config(page_title="Playground", layout="wide")
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Aller à :", ["Chatbot 🤖", "Courses 📚", "Tests 🎯"])

    if page == "Chatbot 🤖":
        chatbot_page()
    elif page == "Courses 📚":
        courses_page()
    elif page == "Tests 🎯":
        tests_page()

if __name__ == "__main__":
    main()
