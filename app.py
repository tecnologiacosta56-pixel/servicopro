import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import mercadopago
import pandas as pd

# ==============================
# CONFIG
# ==============================

st.set_page_config(
    page_title="ServiçoPro SaaS",
    layout="wide",
    page_icon="🚀"
)

# ==============================
# FIREBASE
# ==============================

if not firebase_admin._apps:
    firebase_dict = dict(st.secrets["firebase"])
    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

sdk = mercadopago.SDK(
    st.secrets["mercadopago"]["MP_ACCESS_TOKEN"]
)

# ==============================
# 🔐 SESSION DEFAULT
# ==============================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "uid" not in st.session_state:
    st.session_state["uid"] = None

if "empresa_id" not in st.session_state:
    st.session_state["empresa_id"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

# ==============================
# 🔐 LOGIN FUNCTION (SIMULADO FIREBASE AUTH)
# ==============================

def login(email, password):
    users = db.collection("usuarios").where("email", "==", email).stream()

    for u in users:
        data = u.to_dict()

        # aqui futuramente valida auth real Firebase Auth
        st.session_state["uid"] = u.id
        st.session_state["empresa_id"] = data["empresa_id"]
        st.session_state["role"] = data.get("role", "member")
        st.session_state["authenticated"] = True
        return True

    return False

# ==============================
# 🚪 LOGOUT
# ==============================

def logout():
    st.session_state.clear()
    st.rerun()

# ==============================
# 🔐 LOGIN SCREEN
# ==============================

if not st.session_state["authenticated"]:

    st.title("🔐 Login ServiçoPro")

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if login(email, password):
            st.success("Login realizado!")
            st.rerun()
        else:
            st.error("Credenciais inválidas")

    st.stop()

# ==============================
# 🏢 CONTEXTO EMPRESA
# ==============================

empresa_id = st.session_state["empresa_id"]

empresa_ref = db.collection("empresas").document(empresa_id)

clientes_ref = empresa_ref.collection("clientes")
servicos_ref = empresa_ref.collection("servicos")
plano_ref = empresa_ref.collection("plano")

# ==============================
# LOGOUT BUTTON
# ==============================

st.sidebar.button("🚪 Logout", on_click=logout)

# ==============================
# MENU
# ==============================

menu = st.sidebar.selectbox("📌 Menu", [
    "📊 Dashboard",
    "👤 Clientes",
    "🛠 Serviços",
    "💳 Plano"
])

# ==============================
# DASHBOARD
# ==============================

if menu == "📊 Dashboard":
    st.title("📊 Dashboard SaaS")

    clientes = list(clientes_ref.stream())
    servicos = list(servicos_ref.stream())

    col1, col2, col3 = st.columns(3)

    col1.metric("Empresa", empresa_id)
    col2.metric("Clientes", len(clientes))
    col3.metric("Serviços", len(servicos))

    st.bar_chart(pd.DataFrame({
        "Categoria": ["Clientes", "Serviços"],
        "Total": [len(clientes), len(servicos)]
    }).set_index("Categoria"))

# ==============================
# CLIENTES
# ==============================

elif menu == "👤 Clientes":
    st.title("👤 Clientes")

    nome = st.text_input("Novo cliente")

    if st.button("➕ Adicionar"):
        if nome:
            clientes_ref.add({"nome": nome})
            st.success("Adicionado!")

    for c in clientes_ref.stream():
        data = c.to_dict()

        col1, col2 = st.columns([8, 2])

        with col1:
            st.markdown(f"👤 {data['nome']}")

        if st.session_state.get(f"edit_{c.id}"):

            novo = st.text_input("Editar", value=data["nome"], key=f"inp_{c.id}")

            colA, colB = st.columns(2)

            with colA:
                if st.button("Salvar", key=f"s_{c.id}"):
                    clientes_ref.document(c.id).update({"nome": novo})
                    st.session_state[f"edit_{c.id}"] = False
                    st.rerun()

            with colB:
                if st.button("Cancelar", key=f"c_{c.id}"):
                    st.session_state[f"edit_{c.id}"] = False
                    st.rerun()

        else:
            if st.button("✏️", key=f"e_{c.id}"):
                st.session_state[f"edit_{c.id}"] = True
                st.rerun()

        if st.button("🗑", key=f"d_{c.id}"):
            clientes_ref.document(c.id).delete()
            st.rerun()

# ==============================
# SERVIÇOS
# ==============================

elif menu == "🛠 Serviços":
    st.title("🛠 Serviços")

    cliente = st.text_input("Cliente")
    servico = st.text_input("Serviço")

    if st.button("➕ Salvar"):
        if cliente and servico:
            servicos_ref.add({
                "cliente": cliente,
                "servico": servico
            })
            st.success("Salvo!")

    for s in servicos_ref.stream():
        data = s.to_dict()

        col1, col2 = st.columns([8, 2])

        with col1:
            st.markdown(f"🛠 {data['cliente']} - {data['servico']}")

        if st.button("🗑", key=f"ds_{s.id}"):
            servicos_ref.document(s.id).delete()
            st.rerun()

# ==============================
# PLANO
# ==============================

elif menu == "💳 Plano":
    st.title("💳 Plano")

    st.info("Sistema pronto para upgrade SaaS real")
