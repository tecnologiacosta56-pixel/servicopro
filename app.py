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
# STATE
# ==================================================

if "auth" not in st.session_state:
    st.session_state.auth = False

if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = None

if "delete_client" not in st.session_state:
    st.session_state.delete_client = None

if "delete_service" not in st.session_state:
    st.session_state.delete_service = None

# ==================================================
# LOGIN
# ==================================================

def login():

    doc = db.collection("usuarios").document("user123").get()

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
# SIDEBAR LOGO (SEGURA)
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
        st.rerun()

    st.divider()

    for c in clientes_ref.get():

        data = c.to_dict()
        cid = c.id

        col1, col2, col3 = st.columns([6, 2, 2])

        with col1:
            st.write(f"👤 {data.get('nome')}")

        # EDITAR
        with col2:

            if st.button("✏️", key="ec"+cid):
                st.session_state["edit_c_"+cid] = True

            if st.session_state.get("edit_c_"+cid):

                novo = st.text_input(
                    "Editar cliente",
                    value=data.get("nome"),
                    key="ic_"+cid
                )

                if st.button("Salvar", key="sc_"+cid):

                    clientes_ref.document(cid).update({"nome": novo})

                    st.session_state["edit_c_"+cid] = False
                    st.rerun()

                if st.button("Cancelar", key="cc_"+cid):

                    st.session_state["edit_c_"+cid] = False
                    st.rerun()

        # EXCLUIR
        with col3:

            if st.button("🗑", key="dc"+cid):
                st.session_state.delete_client = cid

    # CONFIRMAÇÃO CLIENTE
    if st.session_state.delete_client:

        st.warning("Excluir cliente?")

        c1, c2 = st.columns(2)

        if c1.button("Sim"):
            clientes_ref.document(st.session_state.delete_client).delete()
            st.session_state.delete_client = None
            st.rerun()

        if c2.button("Cancelar"):
            st.session_state.delete_client = None
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
        sid = s.id

        col1, col2, col3 = st.columns([6, 2, 2])

        with col1:
            st.write(f"🛠 {data.get('cliente')} - {data.get('servico')}")

        # EDITAR SERVIÇO
        with col2:

            if st.button("✏️", key="es"+sid):
                st.session_state["edit_s_"+sid] = True

            if st.session_state.get("edit_s_"+sid):

                novo = st.text_input(
                    "Editar serviço",
                    value=data.get("servico"),
                    key="is_"+sid
                )

                if st.button("Salvar", key="ss_"+sid):

                    servicos_ref.document(sid).update({
                        "servico": novo
                    })

                    st.session_state["edit_s_"+sid] = False
                    st.rerun()

                if st.button("Cancelar", key="cs_"+sid):

                    st.session_state["edit_s_"+sid] = False
                    st.rerun()

        # EXCLUIR SERVIÇO
        with col3:

            if st.button("🗑", key="ds"+sid):
                st.session_state.delete_service = sid

    # CONFIRMAÇÃO SERVIÇO
    if st.session_state.delete_service:

        st.warning("Excluir serviço?")

        s1, s2 = st.columns(2)

        if s1.button("Sim"):
            servicos_ref.document(st.session_state.delete_service).delete()
            st.session_state.delete_service = None
            st.rerun()

        if s2.button("Cancelar"):
            st.session_state.delete_service = None
            st.rerun()
