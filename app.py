import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
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
# CSS (UI SaaS LIMPA)
# ==================================================

st.markdown("""
<style>

div.stButton > button {
    background: linear-gradient(90deg, #4F46E5, #06B6D4);
    color: white;
    border-radius: 10px;
    font-weight: bold;
    border: none;
}

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

if "auth" not in st.session_state:
    st.session_state.auth = False

if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = None

# ==================================================
# LOGIN FIXO (user123)
# ==================================================

def login():

    doc = db.collection("usuarios").document("user123").get()

    if not doc.exists:
        return False

    user = doc.to_dict()

    empresa = user.get("empresa_id")

    if not empresa:
        return False

    st.session_state.auth = True
    st.session_state.empresa_id = empresa

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
            st.rerun()
        else:
            st.error("Erro login")

    st.stop()

# ==================================================
# CONTEXTO EMPRESA
# ==================================================

empresa_id = st.session_state.empresa_id

empresa_ref = db.collection("empresas").document(empresa_id)

clientes_ref = empresa_ref.collection("clientes")
servicos_ref = empresa_ref.collection("servicos")

# ==================================================
# SIDEBAR (LOGO SEGURA)
# ==================================================

if os.path.exists("assets/logo.png"):
    st.sidebar.image("assets/logo.png", width=160)
else:
    st.sidebar.markdown("🚀 ServiçoPro")

st.sidebar.title("ServiçoPro")

st.sidebar.write(f"Empresa: {empresa_id}")

st.sidebar.button("🚪 Logout", on_click=logout)

menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Clientes", "Serviços"]
)

# ==================================================
# DASHBOARD (ESTILO STRIPE)
# ==================================================

if menu == "Dashboard":

    st.title("📊 Dashboard")

    clientes = list(clientes_ref.get())
    servicos = list(servicos_ref.get())

    total_clientes = len(clientes)
    total_servicos = len(servicos)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 👤 Clientes")
        st.metric("Total", total_clientes)

    with col2:
        st.markdown("### 🛠 Serviços")
        st.metric("Total", total_servicos)

    with col3:
        st.markdown("### 🚀 Empresa")
        st.metric("ID", empresa_id)

    st.divider()

    st.subheader("📈 Visão geral")

    colA, colB = st.columns(2)

    with colA:
        st.markdown("#### Crescimento")
        st.progress(min(total_clientes / 10, 1.0))
        st.caption("Meta: 10 clientes")

    with colB:
        st.markdown("#### Operação")
        st.progress(min(total_servicos / 20, 1.0))
        st.caption("Meta: 20 serviços")

    st.divider()

    st.subheader("🧠 Insights")

    if total_clientes == 0:
        st.info("Nenhum cliente ainda.")

    elif total_clientes < 5:
        st.warning("Base inicial pequena.")

    else:
        st.success("Base ativa 🚀")

# ==================================================
# CLIENTES
# ==================================================

elif menu == "Clientes":

    st.title("👤 Clientes")

    nome = st.text_input("Nome")

    if st.button("➕ Adicionar") and nome:
        clientes_ref.add({"nome": nome})
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

    if st.button("➕ Salvar") and cliente and servico:
        servicos_ref.add({
            "cliente": cliente,
            "servico": servico
        })
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
