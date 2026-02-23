import streamlit as st

def main():
    st.set_page_config(page_title="My Streamlit App")
    st.header("Welcome to my Streamlit App!")
    user_input = st.text_input("Enter your desired text and press Enter:")
    if user_input:
        st.write(f"You entered: {user_input}")


if __name__ == "__main__":
    main()
