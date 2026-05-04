import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# =========================
# FIREBASE INIT
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="ServiçoPro SaaS",
    layout="wide",
    page_icon="⚡"
)

# =========================
# STYLE (PRODUTO VISUAL)
# =========================
st.markdown("""
<style>

body {
    background-color: #0E1117;
}

h1, h2, h3 {
    color: #FFFFFF;
}

.card {
    padding: 15px;
    border-radius: 12px;
    background: #1E1E1E;
    border: 1px solid #2A2A2A;
    margin-bottom: 10px;
}

.metric-box {
    background: #161B22;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TEMP EMPRESA (SEM LOGIN AINDA)
# =========================
empresa_id = "empresa_demo_001"

# =========================
# MENU
# =========================
menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Clientes", "Ordens"]
)

# =========================
# DASHBOARD (UPGRADE REAL)
# =========================
if menu == "Dashboard":
    st.title("📊 Painel de Controle SaaS")

    ordens = list(db.collection("empresas")
                  .document(empresa_id)
                  .collection("ordens").stream())

    clientes = list(db.collection("empresas")
                    .document(empresa_id)
                    .collection("clientes").stream())

    total_os = len(ordens)
    total_clientes = len(clientes)

    faturamento = 0
    abertas = 0
    concluidas = 0

    for o in ordens:
        d = o.to_dict()
        faturamento += float(d.get("valor", 0))

        if d.get("status") == "Novo":
            abertas += 1
        if d.get("status") == "Finalizado":
            concluidas += 1

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📦 OS Total", total_os)
    col2.metric("👥 Clientes", total_clientes)
    col3.metric("💰 Faturamento", f"R$ {faturamento:.2f}")
    col4.metric("✅ Concluídas", concluidas)

    st.divider()

    st.subheader("📌 Visão rápida do sistema")

    st.write(f"🔵 OS em aberto: {abertas}")
    st.write(f"🟢 OS finalizadas: {concluidas}")

# =========================
# CLIENTES
# =========================
elif menu == "Clientes":
    st.title("👥 Gestão de Clientes")

    nome = st.text_input("Nome do cliente")
    servico = st.text_input("Serviço")

    if st.button("Salvar Cliente"):
        db.collection("empresas").document(empresa_id)\
            .collection("clientes").add({
                "nome": nome,
                "servico": servico
            })
        st.success("Cliente criado com sucesso")

    st.divider()

    st.subheader("Lista de Clientes")

    clientes = db.collection("empresas").document(empresa_id)\
        .collection("clientes").stream()

    for c in clientes:
        d = c.to_dict()

        st.markdown(f"""
        <div class="card">
            👤 <b>{d.get('nome')}</b><br>
            🔧 {d.get('servico')}
        </div>
        """, unsafe_allow_html=True)

# =========================
# ORDENS
# =========================
elif menu == "Ordens":
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

    st.divider()

    st.subheader("Ordens Registradas")

    ordens = db.collection("empresas").document(empresa_id)\
        .collection("ordens").stream()

    for o in ordens:
        d = o.to_dict()

        status = d.get("status")

        cor = {
            "Novo": "🔵",
            "Em andamento": "🟠",
            "Finalizado": "🟢"
        }.get(status, "⚪")

        st.markdown(f"""
        <div class="card">
            👤 {d.get('cliente')}<br>
            🔧 {d.get('servico')}<br>
            💰 R$ {d.get('valor')}<br>
            {cor} {status}
        </div>
        """, unsafe_allow_html=True)
