import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="ServiçoPro SaaS",
    layout="wide",
    page_icon="🚀"
)

st.write("🚀 App iniciado")

# ==================================================
# FIREBASE INIT
# ==================================================

try:

    firebase_admin.get_app()

    st.write("✅ Firebase já inicializado")

except ValueError:

    try:

        firebase_config = st.secrets["firebase"]

        firebase_dict = dict(firebase_config)

        firebase_dict["private_key"] = firebase_dict[
            "private_key"
        ].replace("\\n", "\n")

        cred = credentials.Certificate(firebase_dict)

        firebase_admin.initialize_app(cred)

        st.write("✅ Firebase inicializado")

    except Exception as e:

        st.error(f"❌ Erro Firebase: {e}")

        st.stop()

# ==================================================
# FIRESTORE
# ==================================================

try:

    db = firestore.client()

    st.write("✅ Firestore conectado")

except Exception as e:

    st.error(f"❌ Erro Firestore: {e}")

    st.stop()

# ==================================================
# SESSION
# ==================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "uid" not in st.session_state:
    st.session_state.uid = None

if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = None

if "role" not in st.session_state:
    st.session_state.role = None

# ==================================================
# LOGIN
# ==================================================

def login(email):

    try:

        st.write("🔍 Procurando usuário...")

        query = db.collection(
            "usuarios"
        ).where(
            "email",
            "==",
            email
        ).limit(1)

        docs = query.get()

        st.write(f"📦 Usuários encontrados: {len(docs)}")

        if len(docs) == 0:
            return False

        user_doc = docs[0]

        usuario = user_doc.to_dict()

        st.session_state.uid = user_doc.id

        st.session_state.empresa_id = usuario.get(
            "empresa_id"
        )

        st.session_state.role = usuario.get(
            "role",
            "member"
        )

        st.session_state.authenticated = True

        st.write("✅ Sessão criada")

        return True

    except Exception as e:

        st.error(f"❌ Erro login: {e}")

        return False

# ==================================================
# LOGOUT
# ==================================================

def logout():

    st.session_state.authenticated = False

    st.session_state.uid = None

    st.session_state.empresa_id = None

    st.session_state.role = None

    st.rerun()

# ==================================================
# LOGIN SCREEN
# ==================================================

if not st.session_state.authenticated:

    st.title("🔐 Login ServiçoPro SaaS")

    email = st.text_input("Email")

    if st.button("Entrar"):

        sucesso = login(email)

        st.write(st.session_state)

        if sucesso:

            st.success("✅ Login realizado")

            st.rerun()

        else:

            st.error("❌ Usuário não encontrado")

    st.stop()

# ==================================================
# EMPRESA
# ==================================================

empresa_id = st.session_state.empresa_id

st.write(f"🏢 Empresa: {empresa_id}")

if not empresa_id:

    st.error("❌ Empresa inválida")

    st.stop()

# ==================================================
# REFERÊNCIAS
# ==================================================

empresa_ref = db.collection(
    "empresas"
).document(
    empresa_id
)

clientes_ref = empresa_ref.collection(
    "clientes"
)

servicos_ref = empresa_ref.collection(
    "servicos"
)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("🚀 ServiçoPro")

st.sidebar.write(
    f"Empresa: {empresa_id}"
)

st.sidebar.write(
    f"Perfil: {st.session_state.role}"
)

st.sidebar.button(
    "🚪 Logout",
    on_click=logout
)

menu = st.sidebar.selectbox(

    "📌 Menu",

    [
        "📊 Dashboard",
        "👤 Clientes",
        "🛠 Serviços",
        "💳 Plano"
    ]
)

# ==================================================
# DASHBOARD
# ==================================================

if menu == "📊 Dashboard":

    st.title("📊 Dashboard SaaS")

    try:

        clientes = clientes_ref.get()

        servicos = servicos_ref.get()

        st.success("✅ Dashboard carregado")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Empresa",
            empresa_id
        )

        col2.metric(
            "Clientes",
            len(clientes)
        )

        col3.metric(
            "Serviços",
            len(servicos)
        )

        chart_data = pd.DataFrame({

            "Categoria": [
                "Clientes",
                "Serviços"
            ],

            "Total": [
                len(clientes),
                len(servicos)
            ]

        })

        st.bar_chart(
            chart_data.set_index(
                "Categoria"
            )
        )

    except Exception as e:

        st.error(f"❌ Erro dashboard: {e}")

# ==================================================
# CLIENTES
# ==================================================

elif menu == "👤 Clientes":

    st.title("👤 Clientes")

    nome = st.text_input(
        "Nome do cliente"
    )

    if st.button("➕ Adicionar Cliente"):

        try:

            clientes_ref.add({
                "nome": nome
            })

            st.success("✅ Cliente adicionado")

            st.rerun()

        except Exception as e:

            st.error(f"❌ Erro: {e}")

# ==================================================
# SERVIÇOS
# ==================================================

elif menu == "🛠 Serviços":

    st.title("🛠 Serviços")

    cliente = st.text_input("Cliente")

    servico = st.text_input("Serviço")

    if st.button("➕ Salvar Serviço"):

        try:

            servicos_ref.add({

                "cliente": cliente,
                "servico": servico

            })

            st.success("✅ Serviço salvo")

            st.rerun()

        except Exception as e:

            st.error(f"❌ Erro: {e}")

# ==================================================
# PLANO
# ==================================================

elif menu == "💳 Plano":

    st.title("💳 Plano SaaS")

    st.success("✅ Sistema estabilizado")
