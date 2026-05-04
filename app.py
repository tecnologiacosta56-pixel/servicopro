import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# 🔐 CONEXÃO FIREBASE
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 🎯 CONFIG
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}

.stButton>button {
    background-color: #00C853;
    color: white;
    border-radius: 8px;
    height: 3em;
    width: 100%;
}

.stTextInput>div>div>input {
    border-radius: 8px;
}

.stSelectbox>div>div {
    border-radius: 8px;
}

.card {
    padding: 15px;
    border-radius: 10px;
    background-color: #1E1E1E;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)(page_title="ServiçoPro 2", layout="wide")

st.title("🚀 ServiçoPro 2")

# 📌 MENU LATERAL
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Clientes", "Serviços", "OS"])

# =========================
# 📊 DASHBOARD
# =========================
if menu == "Dashboard":
    st.subheader("📊 Visão Geral")
    st.write("Sistema em funcionamento ✔️")

# =========================
# 👤 CLIENTES
# =========================
elif menu == "Clientes":
    st.subheader("👤 Clientes")

    aba = st.radio("Opção", ["Cadastrar", "Listar"], horizontal=True)

    # CADASTRAR CLIENTE
    if aba == "Cadastrar":
        nome = st.text_input("Nome do cliente")
        contato = st.text_input("Contato")

        if st.button("Salvar cliente"):
            if nome:
                db.collection("clientes").add({
                    "nome": nome,
                    "contato": contato
                })
                st.success("Cliente salvo com sucesso!")
            else:
                st.warning("Digite o nome do cliente")

    # LISTAR CLIENTES
    elif aba == "Listar":
        clientes = db.collection("clientes").stream()

        encontrou = False

        for c in clientes:
            encontrou = True
            dados = c.to_dict()

            st.markdown("---")
            st.write(f"👤 Nome: {dados.get('nome')}")
            st.write(f"📞 Contato: {dados.get('contato')}")

        if not encontrou:
            st.warning("Nenhum cliente cadastrado")

# =========================
# 🔧 SERVIÇOS
# =========================
elif menu == "Serviços":
    st.subheader("🔧 Serviços")
    st.info("Em desenvolvimento...")

# =========================
# 📋 ORDENS DE SERVIÇO (OS)
# =========================
elif menu == "OS":
    st.title("📋 Ordens de Serviço")

    aba = st.radio("Escolha uma opção", ["Cadastrar OS", "Listar OS"], horizontal=True)

    # -------- CADASTRAR OS --------
    if aba == "Cadastrar OS":
        st.subheader("📝 Nova Ordem de Serviço")

        cliente = st.text_input("Cliente")
        servico = st.text_input("Serviço")
        valor = st.number_input("Valor (R$)", min_value=0.0)
        status = st.selectbox("Status", ["Novo", "Em andamento", "Finalizado"])

        if st.button("Salvar OS"):
            if cliente and servico:
                db.collection("ordens").add({
                    "cliente": cliente,
                    "servico": servico,
                    "valor": valor,
                    "status": status
                })
                st.success("✅ Ordem de serviço salva com sucesso!")
            else:
                st.warning("⚠️ Preencha os campos obrigatórios.")

    # -------- LISTAR OS --------
    elif aba == "Listar OS":
        st.subheader("📂 Lista de Ordens")

        ordens = db.collection("ordens").stream()

        encontrou = False

        for os in ordens:
            encontrou = True
            dados = os.to_dict()

            st.markdown("---")
            st.write(f"👤 Cliente: {dados.get('cliente')}")
            st.write(f"🔧 Serviço: {dados.get('servico')}")
            st.write(f"💰 Valor: R$ {dados.get('valor')}")
            st.write(f"📌 Status: {dados.get('status')}")

        if not encontrou:
            st.warning("Nenhuma ordem encontrada.")
