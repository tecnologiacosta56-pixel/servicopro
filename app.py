import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# 🔐 FIREBASE
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ⚙ CONFIG
st.set_page_config(
    page_title="ServiçoPro",
    layout="wide",
    page_icon="logo.png"
)

# 🎨 ESTILO PREMIUM
st.markdown("""
<style>

/* FUNDO */
body {
    background-color: #0E1117;
}

/* TITULOS */
h1, h2, h3 {
    color: #FFFFFF;
}

/* BOTÕES */
.stButton>button {
    background: linear-gradient(90deg, #2196F3, #00C853);
    color: white;
    border-radius: 10px;
    height: 3em;
    font-weight: bold;
}

/* INPUTS */
.stTextInput>div>div>input,
.stNumberInput>div>div>input {
    border-radius: 10px;
}

/* CARDS */
.card {
    padding: 15px;
    border-radius: 12px;
    background: #1E1E1E;
    border: 1px solid #2A2A2A;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
    margin-bottom: 10px;
}

/* LOGO ARREDONDADA */
section[data-testid="stSidebar"] img {
    border-radius: 50%;
    display: block;
    margin: 10px auto;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

</style>
""", unsafe_allow_html=True)

# 🧠 SIDEBAR (LOGO + MENU)
st.sidebar.image("logo.png", width=120)
st.sidebar.markdown("## ⚡ ServiçoPro")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Clientes", "Serviços", "OS"])

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.title("📊 Dashboard")

    ordens = list(db.collection("ordens").stream())
    clientes = list(db.collection("clientes").stream())

    total_os = len(ordens)
    total_clientes = len(clientes)
    faturamento = sum([o.to_dict().get("valor", 0) for o in ordens])

    col1, col2, col3 = st.columns(3)

    col1.metric("📋 Ordens", total_os)
    col2.metric("👤 Clientes", total_clientes)
    col3.metric("💰 Faturamento", f"R$ {faturamento:.2f}")

# =========================
# CLIENTES
# =========================
elif menu == "Clientes":
    st.title("👤 Clientes")

    aba = st.radio("Opção", ["Cadastrar", "Listar"], horizontal=True)

    if aba == "Cadastrar":
        nome = st.text_input("Nome")
        contato = st.text_input("Contato")

        if st.button("Salvar cliente"):
            if nome:
                db.collection("clientes").add({
                    "nome": nome,
                    "contato": contato
                })
                st.success("Cliente salvo")
            else:
                st.warning("Digite o nome")

    elif aba == "Listar":
        clientes = db.collection("clientes").stream()

        encontrou = False

        for c in clientes:
            encontrou = True
            d = c.to_dict()

            st.markdown(f"""
            <div class="card">
                <b>👤 {d.get('nome')}</b><br>
                📞 {d.get('contato')}
            </div>
            """, unsafe_allow_html=True)

        if not encontrou:
            st.warning("Nenhum cliente")

# =========================
# SERVIÇOS
# =========================
elif menu == "Serviços":
    st.title("🔧 Serviços")
    st.info("Em desenvolvimento...")

# =========================
# OS
# =========================
elif menu == "OS":
    st.title("📋 Ordens de Serviço")

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
                st.success("OS salva")
            else:
                st.warning("Preencha os campos")

    # LISTAR
    elif aba == "Listar OS":
        ordens = db.collection("ordens").stream()

        encontrou = False

        for o in ordens:
            encontrou = True
            d = o.to_dict()

            status = d.get("status")

            if status == "Novo":
                cor = "#2196F3"
            elif status == "Em andamento":
                cor = "#FF9800"
            else:
                cor = "#00C853"

            st.markdown(f"""
            <div class="card">
                <b>👤 Cliente:</b> {d.get('cliente')}<br>
                <b>🔧 Serviço:</b> {d.get('servico')}<br>
                <b>💰 Valor:</b> R$ {d.get('valor')}<br>
                <b style="color:{cor}">📌 Status: {status}</b>
            </div>
            """, unsafe_allow_html=True)

        if not encontrou:
            st.warning("Nenhuma OS encontrada")
