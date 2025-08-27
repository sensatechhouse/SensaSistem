import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

import streamlit as st
from Classes.Campeonato import Tournaments, Gerenciador

pasta_bases = 'DataBase/bases'

@st.dialog("Criar um novo Torneio")
def criar_torneio():
    jogo = st.text_input("Jogo")
    nome = st.text_input("Nome do Torneio")
    if st.button("Submit"):
        Gerenciador(jogo, nome)
        st.rerun()
        

def main():
    st.set_page_config(
        page_title="Camp-Now - Sistema de Campeonatos",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    bases = os.listdir('DataBase/bases')
    torneio = st.sidebar.selectbox("Selecione o gerenciador", bases)

    c1, c2 = st.columns([0.8, 0.2])
    with c1:
        st.title(f"Camp-Now - Gerenciador de Torneios")
    with c2:
        if st.button('Criar um novo Torneio'):
            criar_torneio()

        

    
    

if __name__ == '__main__':
    main()