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
# CSS
# ==================================================

st.markdown("""
<style>

div.stButton > button {
    background: linear-gradient(90deg, #4F46E5, #06B6D4);
    color: white;
    border-radius: 10px;
    font-weight: bold;
}

div.stButton > button:hover {
    background: linear-gradient(90deg, #06B6D4, #4F46E5);
}

/* sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# FIREBASE
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
# SESSION
# ==================================================

if "auth" not in st.session_state:
    st.session_state.auth = False

if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = None

# ==================================================
# LOGIN
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

    st.session_state.auth = True
    st.session_state.empresa_id = user.get("empresa_id")

    return True

# ==================================================
# LOGOUT
# ==================================================

def logout():

    st.session_state.auth = False
    st.session_state.empresa_id = None
    st.rerun()

# ==================================================
# LOGIN SCREEN
# ==================================================

if not st.session_state.auth:

    st.title("🔐 ServiçoPro SaaS")

    if st.button("Entrar"):

        if login():

            st.success("Login OK")

            st.rerun()

        else:

            st.error("Erro login")

    st.stop()

# ==================================================
# EMPRESA
# ==================================================

empresa_id = st.session_state.empresa_id

empresa_ref = db.collection("empresas").document(empresa_id)

clientes_ref = empresa_ref.collection("clientes")
servicos_ref = empresa_ref.collection("servicos")

# ==================================================
# SIDEBAR LOGO (ROBUSTA)
# ==================================================

if os.path.exists("assets/logo.png"):
    st.sidebar.image("assets/logo.png", width=160)
else:
    st.sidebar.markdown("## 🚀 ServiçoPro")

st.sidebar.write(f"Empresa: {empresa_id}")

st.sidebar.button("🚪 Logout", on_click=logout)

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Clientes", "Serviços"])

# ==================================================
# DASHBOARD
# ==================================================

if menu == "Dashboard":

    st.title("📊 Dashboard")

    st.metric("Clientes", len(clientes_ref.get()))
    st.metric("Serviços", len(servicos_ref.get()))

# ==================================================
# CLIENTES
# ==================================================

elif menu == "Clientes":

    st.title("👤 Clientes")

    nome = st.text_input("Nome")

    if st.button("➕ Adicionar") and nome:

        clientes_ref.add({"nome": nome})

        st.success("Adicionado")

        st.rerun()

    st.divider()

    for c in clientes_ref.get():

        data = c.to_dict()

        col1, col2, col3 = st.columns([6, 2, 2])

        with col1:
            st.write(f"👤 {data.get('nome')}")

        # EDITAR
        with col2:

            if st.button("✏️ Editar", key="e"+c.id):

                novo_nome = st.text_input(
                    "Novo nome",
                    value=data.get("nome"),
                    key="edit_"+c.id
                )

                if st.button("Salvar", key="save"+c.id):

                    clientes_ref.document(c.id).update({
                        "nome": novo_nome
                    })

                    st.rerun()

        # EXCLUIR COM CONFIRMAÇÃO
        with col3:

            if st.button("🗑", key=c.id):

                st.warning("Tem certeza?")

                if st.button("Confirmar exclusão", key="del"+c.id):

                    clientes_ref.document(c.id).delete()

                    st.rerun()

# ==================================================
# SERVIÇOS
# ==================================================

elif menu == "Serviços":

    st.title("🛠 Serviços")

    cliente = st.text_input("Cliente")
    servico = st.text_input("Serviço")

    if st.button("➕ Salvar") and cliente and servico:

        servicos_ref.add({
            "cliente": cliente,
            "servico": servico
        })

        st.success("Salvo")

        st.rerun()

    st.divider()

    for s in servicos_ref.get():

        data = s.to_dict()

        col1, col2, col3 = st.columns([6, 2, 2])

        with col1:
            st.write(f"🛠 {data.get('cliente')} - {data.get('servico')}")

        with col2:

            if st.button("✏️", key="e"+s.id):

                novo = st.text_input(
                    "Editar serviço",
                    value=data.get("servico"),
                    key="se"+s.id
                )

                if st.button("Salvar", key="ss"+s.id):

                    servicos_ref.document(s.id).update({
                        "servico": novo
                    })

                    st.rerun()

        with col3:

            if st.button("🗑", key=s.id):

                st.warning("Confirmar exclusão")

                if st.button("Sim", key="del"+s.id):

                    servicos_ref.document(s.id).delete()

                    st.rerun()
