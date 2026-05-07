import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="ServiçoPro SaaS",
    layout="wide"
)

st.write("🚀 App iniciado")

# ==================================================
# FIREBASE
# ==================================================

try:

    firebase_admin.get_app()

    st.write("✅ Firebase já inicializado")

except ValueError:

    firebase_config = st.secrets["firebase"]

    firebase_dict = dict(firebase_config)

    firebase_dict["private_key"] = firebase_dict[
        "private_key"
    ].replace("\\n", "\n")

    cred = credentials.Certificate(firebase_dict)

    firebase_admin.initialize_app(cred)

    st.write("✅ Firebase iniciado")

# ==================================================
# FIRESTORE
# ==================================================

try:

    db = firestore.client()

    st.write("✅ Firestore conectado")

except Exception as e:

    st.error(f"Erro Firestore: {e}")

    st.stop()

# ==================================================
# SESSION
# ==================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = None

# ==================================================
# LOGIN
# ==================================================

def login():

    try:

        st.write("🔍 Buscando documento direto...")

        doc_ref = db.collection(
            "usuarios"
        ).document(
            "teste123"
        )

        doc = doc_ref.get()

        st.write("✅ Documento encontrado")

        if not doc.exists:

            st.error("❌ Documento não existe")

            return False

        usuario = doc.to_dict()

        st.write(usuario)

        st.session_state.authenticated = True

        st.session_state.empresa_id = usuario.get(
            "empresa_id"
        )

        return True

    except Exception as e:

        st.error(f"❌ Erro login: {e}")

        return False

# ==================================================
# LOGIN SCREEN
# ==================================================

if not st.session_state.authenticated:

    st.title("🔐 Teste Login Firestore")

    if st.button("Entrar"):

        sucesso = login()

        st.write(st.session_state)

        if sucesso:

            st.success("✅ Login OK")

            st.rerun()

    st.stop()

# ==================================================
# DASHBOARD
# ==================================================

st.success("✅ DASHBOARD ABERTO")

st.write(
    f"Empresa: {st.session_state.empresa_id}"
)
