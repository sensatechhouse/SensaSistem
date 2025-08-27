import streamlit as st

def main():
    st.set_page_config(
        page_title="Camp-Now - Sistema de Campeonatos",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("Camp-Now")

if __name__ == '__main__':
    main()