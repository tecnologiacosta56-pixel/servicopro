import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth

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
    st.session_state.empresa_id = "empresa_demo_001"

# =========================
# LOGIN SIMPLIFICADO
# =========================
def login():
    st.title("🔐 Login ServiçoPro")

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        try:
            user = auth.get_user_by_email(email)

            st.session_state.user = {
                "uid": user.uid,
                "email": email
            }

            st.success("Login realizado")
            st.rerun()

        except:
            st.error("Usuário inválido")

# =========================
# LOGOUT
# =========================
def logout():
    if st.sidebar.button("Sair"):
        st.session_state.user = None
        st.rerun()

# =========================
# APP
# =========================
if not st.session_state.user:
    login()
    st.stop()

user = st.session_state.user
empresa_id = st.session_state.empresa_id

st.sidebar.write(f"👤 {user['email']}")
logout()

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Clientes", "OS"])

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.title("📊 Dashboard")

    clientes = list(db.collection("empresas")
                    .document(empresa_id)
                    .collection("clientes")
                    .stream())

    ordens = list(db.collection("empresas")
                  .document(empresa_id)
                  .collection("ordens")
                  .stream())

    total_clientes = len(clientes)
    total_os = len(ordens)

    faturamento = 0
    for o in ordens:
        try:
            faturamento += float(o.to_dict().get("valor", 0))
        except:
            pass

    st.metric("Clientes", total_clientes)
    st.metric("OS", total_os)
    st.metric("Faturamento", f"R$ {faturamento:.2f}")

# =========================
# CLIENTES
# =========================
elif menu == "Clientes":
    st.title("👥 Clientes")

    nome = st.text_input("Nome")
    servico = st.text_input("Serviço")

    if st.button("Salvar Cliente"):
        db.collection("empresas").document(empresa_id)\
          .collection("clientes").add({
            "nome": nome,
            "servico": servico
          })
        st.success("Cliente salvo")

    st.subheader("Lista")

    clientes = db.collection("empresas").document(empresa_id)\
        .collection("clientes").stream()

    for c in clientes:
        d = c.to_dict()
        st.write(f"👤 {d.get('nome')} - {d.get('servico')}")

# =========================
# ORDENS DE SERVIÇO
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

    st.subheader("Lista de OS")

    ordens = db.collection("empresas").document(empresa_id)\
        .collection("ordens").stream()

    for o in ordens:
        d = o.to_dict()

        st.write(f"""
        👤 {d.get('cliente')}
        🔧 {d.get('servico')}
        💰 {d.get('valor')}
        📌 {d.get('status')}
        """)
