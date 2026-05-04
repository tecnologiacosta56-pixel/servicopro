import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import uuid

# =========================
# FIREBASE INIT
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = None

# =========================
# LOGIN SIMPLIFICADO
# =========================
def login():
    st.title("🔐 ServiçoPro Login")

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        try:
            user = auth.get_user_by_email(email)

            st.session_state.user = {
                "uid": user.uid,
                "email": email
            }

            # 🔥 BUSCAR EMPRESA DO USUÁRIO
            empresas = db.collection("empresas") \
                .where("dono_uid", "==", user.uid) \
                .stream()

            empresa = None
            for e in empresas:
                empresa = e

            # 🔥 SE NÃO EXISTIR → CRIA AUTOMATICAMENTE
            if not empresa:
                empresa_id = str(uuid.uuid4())

                db.collection("empresas").document(empresa_id).set({
                    "nome": "Minha Empresa",
                    "dono_uid": user.uid
                })

                st.session_state.empresa_id = empresa_id

            else:
                st.session_state.empresa_id = empresa.id

            st.success("Login realizado com sucesso 🚀")
            st.rerun()

        except:
            st.error("Usuário inválido")

# =========================
# LOGOUT
# =========================
def logout():
    if st.sidebar.button("Sair"):
        st.session_state.user = None
        st.session_state.empresa_id = None
        st.rerun()

# =========================
# APP START
# =========================
if not st.session_state.user:
    login()
    st.stop()

user = st.session_state.user
empresa_id = st.session_state.empresa_id

st.sidebar.write(f"👤 {user['email']}")
st.sidebar.write(f"🏢 Empresa: {empresa_id}")
logout()

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Clientes", "OS"])

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.title("📊 Dashboard SaaS")

    clientes = db.collection("empresas").document(empresa_id)\
        .collection("clientes").stream()

    ordens = db.collection("empresas").document(empresa_id)\
        .collection("ordens").stream()

    total_clientes = len(list(clientes))
    total_os = len(list(ordens))

    st.metric("Clientes", total_clientes)
    st.metric("Ordens", total_os)

# =========================
# CLIENTES
# =========================
elif menu == "Clientes":
    st.title("👥 Clientes")

    nome = st.text_input("Nome")
    servico = st.text_input("Serviço")

    if st.button("Salvar"):
        db.collection("empresas").document(empresa_id)\
            .collection("clientes").add({
                "nome": nome,
                "servico": servico
            })
        st.success("Cliente criado")

# =========================
# ORDENS
# =========================
elif menu == "OS":
    st.title("📄 Ordens de Serviço")

    cliente = st.text_input("Cliente")
    servico = st.text_input("Serviço")
    valor = st.number_input("Valor", min_value=0.0)

    status = st.selectbox("Status", ["Novo", "Em andamento", "Finalizado"])

    if st.button("Criar OS"):
        db.collection("empresas").document(empresa_id)\
            .collection("ordens").add({
                "cliente": cliente,
                "servico": servico,
                "valor": valor,
                "status": status
            })
        st.success("OS criada")
