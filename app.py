import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import os

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="ServiçoPro SaaS",
    layout="wide",
    page_icon="🚀"
)

# ==================================================
# CSS (UI SaaS)
# ==================================================

st.markdown("""
<style>

/* Botões com degradê */
div.stButton > button {
    background: linear-gradient(90deg, #4F46E5, #06B6D4);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: bold;
}

/* Hover botão */
div.stButton > button:hover {
    background: linear-gradient(90deg, #06B6D4, #4F46E5);
    color: white;
}

/* Sidebar estilo SaaS */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# FIREBASE INIT
# ==================================================

try:
    firebase_admin.get_app()

except ValueError:

    firebase_config = st.secrets["firebase"]

    firebase_dict = dict(firebase_config)

    firebase_dict["private_key"] = firebase_dict[
        "private_key"
    ].replace("\\n", "\n")

    cred = credentials.Certificate(firebase_dict)

    firebase_admin.initialize_app(cred)

db = firestore.client()

# ==================================================
# SESSION STATE
# ==================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = None

# ==================================================
# LOGIN FIXO (user123)
# ==================================================

def login():

    doc = db.collection(
        "usuarios"
    ).document(
        "user123"
    ).get()

    if not doc.exists:
        return False

    user = doc.to_dict()

    st.session_state.authenticated = True
    st.session_state.empresa_id = user.get("empresa_id")

    return True

# ==================================================
# LOGOUT
# ==================================================

def logout():

    st.session_state.authenticated = False
    st.session_state.empresa_id = None
    st.rerun()

# ==================================================
# LOGIN SCREEN
# ==================================================

if not st.session_state.authenticated:

    st.title("🔐 ServiçoPro SaaS")

    if st.button("Entrar"):

        if login():

            st.success("Login OK")

            st.rerun()

        else:

            st.error("Usuário não encontrado")

    st.stop()

# ==================================================
# EMPRESA CONTEXTO
# ==================================================

empresa_id = st.session_state.empresa_id

empresa_ref = db.collection(
    "empresas"
).document(
    empresa_id
)

clientes_ref = empresa_ref.collection("clientes")
servicos_ref = empresa_ref.collection("servicos")

# ==================================================
# SIDEBAR (LOGO SEGURA)
# ==================================================

if os.path.exists("assets/logo.png"):
    st.sidebar.image("assets/logo.png", width=160)
else:
    st.sidebar.markdown("## 🚀 ServiçoPro")

st.sidebar.title("ServiçoPro")

st.sidebar.write(f"Empresa: {empresa_id}")

st.sidebar.button("🚪 Logout", on_click=logout)

menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Clientes", "Serviços"]
)

# ==================================================
# DASHBOARD
# ==================================================

if menu == "Dashboard":

    st.title("📊 Dashboard SaaS")

    clientes = clientes_ref.get()
    servicos = servicos_ref.get()

    col1, col2 = st.columns(2)

    col1.metric("Clientes", len(clientes))
    col2.metric("Serviços", len(servicos))

# ==================================================
# CLIENTES
# ==================================================

elif menu == "Clientes":

    st.title("👤 Clientes")

    nome = st.text_input("Nome")

    if st.button("➕ Adicionar"):

        if nome:

            clientes_ref.add({
                "nome": nome
            })

            st.success("Cliente adicionado")

            st.rerun()

    st.divider()

    for c in clientes_ref.get():

        data = c.to_dict()

        col1, col2 = st.columns([8, 2])

        with col1:
            st.write(f"👤 {data.get('nome')}")

        with col2:

            if st.button("🗑", key=c.id):

                clientes_ref.document(c.id).delete()

                st.rerun()

# ==================================================
# SERVIÇOS
# ==================================================

elif menu == "Serviços":

    st.title("🛠 Serviços")

    cliente = st.text_input("Cliente")
    servico = st.text_input("Serviço")

    if st.button("➕ Salvar"):

        if cliente and servico:

            servicos_ref.add({
                "cliente": cliente,
                "servico": servico
            })

            st.success("Salvo")

            st.rerun()

    st.divider()

    for s in servicos_ref.get():

        data = s.to_dict()

        col1, col2 = st.columns([8, 2])

        with col1:
            st.write(f"🛠 {data.get('cliente')} - {data.get('servico')}")

        with col2:

            if st.button("🗑", key=s.id):

                servicos_ref.document(s.id).delete()

                st.rerun()
