import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import plotly.express as px
import pandas as pd

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
# STYLE
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

</style>
""", unsafe_allow_html=True)

# =========================
# EMPRESA TEMP (SEM LOGIN AINDA)
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
# DASHBOARD (COM GRÁFICOS)
# =========================
if menu == "Dashboard":
    st.title("📊 Painel Executivo SaaS")

    ordens = list(db.collection("empresas")
                  .document(empresa_id)
                  .collection("ordens").stream())

    clientes = list(db.collection("empresas")
                    .document(empresa_id)
                    .collection("clientes").stream())

    total_os = len(ordens)
    total_clientes = len(clientes)

    faturamento = 0

    status_count = {
        "Novo": 0,
        "Em andamento": 0,
        "Finalizado": 0
    }

    dados = []

    for o in ordens:
        d = o.to_dict()

        valor = float(d.get("valor", 0))
        faturamento += valor

        status = d.get("status", "Novo")
        if status in status_count:
            status_count[status] += 1

        dados.append({
            "Cliente": d.get("cliente"),
            "Valor": valor
        })

    # =========================
    # MÉTRICAS
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("📦 OS", total_os)
    col2.metric("👥 Clientes", total_clientes)
    col3.metric("💰 Faturamento", f"R$ {faturamento:.2f}")

    st.divider()

    # =========================
    # GRÁFICO STATUS
    # =========================
    st.subheader("📌 Status das Ordens")

    df_status = pd.DataFrame({
        "Status": list(status_count.keys()),
        "Quantidade": list(status_count.values())
    })

    fig1 = px.bar(
        df_status,
        x="Status",
        y="Quantidade",
        text="Quantidade"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # =========================
    # GRÁFICO FATURAMENTO
    # =========================
    st.subheader("💰 Faturamento por Cliente")

    df = pd.DataFrame(dados)

    if not df.empty:
        fig2 = px.line(
            df,
            x="Cliente",
            y="Valor",
            markers=True
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados ainda")

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
        st.success("Cliente criado")

    st.divider()

    clientes = db.collection("empresas").document(empresa_id)\
        .collection("clientes").stream()

    for c in clientes:
        d = c.to_dict()
        st.markdown(f"""
        <div class="card">
            👤 {d.get('nome')}<br>
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

    ordens = db.collection("empresas").document(empresa_id)\
        .collection("ordens").stream()

    for o in ordens:
        d = o.to_dict()

        cor = {
            "Novo": "🔵",
            "Em andamento": "🟠",
            "Finalizado": "🟢"
        }.get(d.get("status"), "⚪")

        st.markdown(f"""
        <div class="card">
            👤 {d.get('cliente')}<br>
            🔧 {d.get('servico')}<br>
            💰 R$ {d.get('valor')}<br>
            {cor} {d.get('status')}
        </div>
        """, unsafe_allow_html=True)
