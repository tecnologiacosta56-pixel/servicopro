import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# 🔐 CONEXÃO FIREBASE
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 🎯 CONFIG
st.set_page_config(page_title="ServiçoPro 2", layout="wide")

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
    st.info("Em desenvolvimento...")

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
