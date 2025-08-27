import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

import streamlit as st
from Classes.Campeonato import Tournaments, Gerenciador

pasta_bases = 'DataBase/bases'

def criar_circuito(bases):
    st.subheader("🏆 Criar Novo Circuito")
    
    jogo = st.text_input("Jogo")
    nome = st.text_input("Nome do Circuito")
    
    if st.button("Criar Circuito", type="primary"):
        if not jogo or not nome:
            st.error("Por favor, preencha todos os campos!")
            return
        
        nome_arquivo = f'{jogo}-{nome}.db'
        
        if nome_arquivo in bases:
            st.warning(f'Já existe um circuito com este nome!')
            
            # Criar um form para confirmação
            with st.form("confirm_delete_form"):
                st.error("⚠️ ATENÇÃO: Isso apagará todos os dados existentes!")
                confirm = st.text_input("Digite 'APAGAR' para confirmar:")
                submitted = st.form_submit_button("Confirmar Exclusão e Recriar")
                
                if submitted and confirm == 'APAGAR':
                    try:
                        # Lógica para apagar e recriar
                        # Gerenciador(jogo, nome)
                        st.success("Circuito recriado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
                elif submitted:
                    st.error("Confirmação incorreta!")
        else:
            # Criar novo circuito
            try:
                # Gerenciador(jogo, nome)
                st.success("Circuito criado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")
        

def main():
    st.set_page_config(
        page_title="Camp-Now - Sistema de Campeonatos",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    bases = os.listdir('DataBase/bases')
    circuito_main = st.sidebar.selectbox("Selecione o gerenciador", bases)

    st.title(f"Camp-Now - Gerenciador de Campeonatos")

    with st.expander("➕ Criar Novo Circuito", expanded=True):
        criar_circuito(bases)

    
    

if __name__ == '__main__':
    main()