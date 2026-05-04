import streamlit as st
from google.cloud import firestore
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="ServicoPro SaaS", layout="wide")

db = firestore.Client.from_service_account_info(
    st.secrets["firebase"]
)

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# LOGIN CORRIGIDO (FUNCIONA COM admin@pro.com / 1234)
# =========================
def login(email, senha):
    try:
        users = db.collection("users").stream()

        for u in users:
            data = u.to_dict()

            if (
                data.get("email", "").strip().lower() == email.strip().lower()
                and data.get("password", "").strip() == senha.strip()
            ):
                return data

        return None

    except Exception:
        return None

# =========================
# TELA LOGIN
# =========================
if st.session_state.user is None:
    st.title("🔐 ServiçoPro SaaS")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        with st.spinner("Validando acesso..."):
            user = login(email, senha)

        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Login inválido")

    st.stop()

# =========================
# USUÁRIO LOGADO
# =========================
user = st.session_state.user

st.sidebar.success(f"Logado: {user.get('email')}")

if st.sidebar.button("Sair"):
    st.session_state.user = None
    st.rerun()

# =========================
# MENU
# =========================
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Clientes", "Serviços"])

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.title("📊 Dashboard SaaS")

    clientes = list(db.collection("clientes").stream())
    servicos = list(db.collection("servicos").stream())

    st.metric("Clientes", len(clientes))
    st.metric("Serviços", len(servicos))

# =========================
# CLIENTES
# =========================
elif menu == "Clientes":
    st.title("👤 Clientes")

    nome = st.text_input("Nome")
    servico = st.text_input("Serviço")

    if st.button("Salvar cliente"):
        if nome and servico:
            db.collection("clientes").add({
                "nome": nome,
                "servico": servico,
                "user": user["email"],
                "created_at": datetime.now()
            })

            st.success("Cliente salvo!")
            st.rerun()

    st.divider()

    clientes = db.collection("clientes").stream()

    for c in clientes:
        d = c.to_dict()

        if d.get("user") != user["email"]:
            continue

        st.write(f"👤 {d['nome']} | {d['servico']}")

# =========================
# SERVIÇOS
# =========================
elif menu == "Serviços":
    st.title("📋 Serviços")

    clientes = db.collection("clientes").stream()

    lista = {
        c.id: c.to_dict()["nome"]
        for c in clientes
        if c.to_dict().get("user") == user["email"]
    }

    if not lista:
        st.warning("Cadastre um cliente primeiro")
        st.stop()

    cliente_id = st.selectbox(
        "Cliente",
        list(lista.keys()),
        format_func=lambda x: lista[x]
    )

    descricao = st.text_area("Descrição")
    prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Urgente"])

    if st.button("Criar serviço"):
        if descricao:
            db.collection("servicos").add({
                "cliente_id": cliente_id,
                "cliente_nome": lista[cliente_id],
                "descricao": descricao,
                "prioridade": prioridade,
                "user": user["email"],
                "status": "Aberto",
                "created_at": datetime.now()
            })

            st.success("Serviço criado!")
            st.rerun()
        else:
            st.warning("Preencha a descrição")

    st.divider()

    servicos = db.collection("servicos").stream()

    for s in servicos:
        d = s.to_dict()

        if d.get("user") != user["email"]:
            continue

        st.write(
            f"👤 {d['cliente_nome']} | "
            f"📝 {d['descricao']} | "
            f"⚡ {d['prioridade']}"
        )
