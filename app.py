import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# 🔐 FIREBASE
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ⚙ CONFIG + FAVICON
st.set_page_config(
    page_title="ServiçoPro 2",
    layout="wide",
    page_icon="logo.png"
)

# 🎨 ESTILO GLOBAL (IDENTIDADE VISUAL)
st.markdown("""
<style>

body {
    background-color: #0E1117;
}

h1, h2, h3 {
    color: #FFFFFF;
}

.stButton>button {
    background: linear-gradient(90deg, #2196F3, #00C853);
    color: white;
    border-radius: 10px;
    height: 3em;
    font-weight: bold;
}

.card {
    padding: 15px;
    border-radius: 12px;
    background: #1E1E1E;
    border: 1px solid #2A2A2A;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# 🧠 HEADER COM LOGO
col1, col2 = st.columns([1, 4])

with col1:
    st.image("logo.png", width=90)

with col2:
    st.title("ServiçoPro 2")

# 📌 MENU
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Clientes", "Serviços", "OS"])

st.sidebar.image("logo.png", width=150)

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.subheader("📊 Visão Geral")
    st.success("Sistema online e funcionando ✔️")

# =========================
# CLIENTES
# =========================
elif menu == "Clientes":
    st.subheader("👤 Clientes")

    aba = st.radio("Opção", ["Cadastrar", "Listar"], horizontal=True)

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
                st.warning("Digite o nome")

    elif aba == "Listar":
        clientes = db.collection("clientes").stream()

        encontrou = False

        for c in clientes:
            encontrou = True
            dados = c.to_dict()

            st.markdown(f"""
            <div class="card">
                <b>👤 Nome:</b> {dados.get('nome')}<br>
                <b>📞 Contato:</b> {dados.get('contato')}
            </div>
            """, unsafe_allow_html=True)

        if not encontrou:
            st.warning("Nenhum cliente cadastrado")

# =========================
# SERVIÇOS
# =========================
elif menu == "Serviços":
    st.subheader("🔧 Serviços")
    st.info("Em desenvolvimento...")

# =========================
# OS
# =========================
elif menu == "OS":
    st.subheader("📋 Ordens de Serviço")

    aba = st.radio("Escolha", ["Cadastrar OS", "Listar OS"], horizontal=True)

    # CADASTRAR
    if aba == "Cadastrar OS":
        cliente = st.text_input("Cliente")
        servico = st.text_input("Serviço")
        valor = st.number_input("Valor", min_value=0.0)
        status = st.selectbox("Status", ["Novo", "Em andamento", "Finalizado"])

        if st.button("Salvar OS"):
            if cliente and servico:
                db.collection("ordens").add({
                    "cliente": cliente,
                    "servico": servico,
                    "valor": valor,
                    "status": status
                })
                st.success("OS salva com sucesso")
            else:
                st.warning("Preencha os campos")

    # LISTAR
    elif aba == "Listar OS":
        ordens = db.collection("ordens").stream()

        encontrou = False

        for os in ordens:
            encontrou = True
            dados = os.to_dict()

            status = dados.get("status")

            if status == "Novo":
                cor = "#2196F3"
            elif status == "Em andamento":
                cor = "#FF9800"
            else:
                cor = "#00C853"

            st.markdown(f"""
            <div class="card">
                <b>👤 Cliente:</b> {dados.get('cliente')}<br>
                <b>🔧 Serviço:</b> {dados.get('servico')}<br>
                <b>💰 Valor:</b> R$ {dados.get('valor')}<br>
                <b style="color:{cor}">📌 Status: {status}</b>
            </div>
            """, unsafe_allow_html=True)

        if not encontrou:
            st.warning("Nenhuma OS encontrada")
