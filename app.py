import streamlit as st

st.set_page_config(
    page_title="Bot FURIA CS:GO",
    page_icon="🔥",
    layout="centered"
)

# CSS personalizado
st.markdown("""
<style>
    .logo {
        display: block;
        margin: 0 auto;
        max-width: 200px;
    }
    .btn {
        display: block;
        width: 200px;
        margin: 20px auto;
        padding: 10px;
        background-color: #FF4B4B;
        color: white;
        text-align: center;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
    }
    .btn:hover {
        background-color: #FF2B2B;
    }
    .container {
        text-align: center;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Conteúdo da página
st.markdown("""
<div class="container">
    <img src="https://seeklogo.com/images/F/furia-esports-logo-9BAEAE9E9D-seeklogo.com.png" alt="FURIA logo" class="logo" />
    <h1>🔥 Bot FURIA CS:GO</h1>
    <p>Seu companheiro interativo para tudo sobre a FURIA no CS:GO! Elenco, jogos, curiosidades e mais.</p>
    <a href="https://t.me/ChatFuriaBot" class="btn" target="_blank">Abrir no Telegram</a>
</div>
""", unsafe_allow_html=True)