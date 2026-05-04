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
# EMPRESA DEMO (SEM LOGIN AINDA)
# =========================
empresa_id = "empresa_demo_001"

# =========================
# PLANOS
# =========================
PLANOS = {
    "free": {
        "limite_clientes": 10,
        "limite_os": 20
    },
    "pro": {
        "limite_clientes": 200,
        "limite_os": 999999
    },
    "premium": {
        "limite_clientes": 999999,
        "limite_os": 999999
    }
}

def get_plano():
    empresa = db.collection("empresas").document(empresa_id).get()
    if empresa.exists:
        return empresa.to_dict().get("plano", "free")
    return "free"

def limite_ok(tipo):
    plano = get_plano()

    total = len(list(db.collection("empresas")
                     .document(empresa_id)
                     .collection(tipo).stream()))

    return total < PLANOS[plano][f"limite_{tipo}"]

# =========================
# MENU
# =========================
menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Clientes", "Ordens", "Planos"]
)

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.title("📊 Painel SaaS")

    ordens = list(db.collection("empresas")
                  .document(empresa_id)
                  .collection("ordens").stream())

    clientes = list(db.collection("empresas")
                    .document(empresa_id)
                    .collection("clientes").stream())

    plano = get_plano()

    total_os = len(ordens)
    total_clientes = len(clientes)

    faturamento = 0
    status = {"Novo": 0, "Em andamento": 0, "Finalizado": 0}

    dados = []

    for o in ordens:
        d = o.to_dict()
        valor = float(d.get("valor", 0))
        faturamento += valor

        stt = d.get("status", "Novo")
        if stt in status:
            status[stt] += 1

        dados.append({
            "Cliente": d.get("cliente"),
            "Valor": valor
        })

    st.success(f"Plano ativo: {plano.upper()}")

    col1, col2, col3 = st.columns(3)
    col1.metric("OS", total_os)
    col2.metric("Clientes", total_clientes)
    col3.metric("Faturamento", f"R$ {faturamento:.2f}")

    st.divider()

    df = pd.DataFrame({
        "Status": list(status.keys()),
        "Quantidade": list(status.values())
    })

    fig = px.bar(df, x="Status", y="Quantidade", text="Quantidade")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# CLIENTES
# =========================
elif menu == "Clientes":
    st.title("👥 Clientes")

    nome = st.text_input("Nome")
    servico = st.text_input("Serviço")

    if st.button("Salvar Cliente"):
        if limite_ok("clientes"):
            db.collection("empresas").document(empresa_id)\
                .collection("clientes").add({
                    "nome": nome,
                    "servico": servico
                })
            st.success("Cliente criado")
        else:
            st.error("Limite do plano atingido")

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
        if limite_ok("ordens"):
            db.collection("empresas").document(empresa_id)\
                .collection("ordens").add({
                    "cliente": cliente,
                    "servico": servico,
                    "valor": valor,
                    "status": status
                })
            st.success("OS criada")
        else:
            st.error("Limite do plano atingido")

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

# =========================
# PLANOS
# =========================
elif menu == "Planos":
    st.title("💰 Planos do Sistema")

    plano_atual = get_plano()

    st.info(f"Plano atual: {plano_atual.upper()}")

    st.write("""
    - FREE: limitado
    - PRO: uso profissional
    - PREMIUM: completo + escalável
    """)

    if st.button("Upgrade simulado para PRO"):
        db.collection("empresas").document(empresa_id).update({
            "plano": "pro"
        })
        st.success("Plano atualizado para PRO")
        st.rerun()

    if st.button("Upgrade simulado para PREMIUM"):
        db.collection("empresas").document(empresa_id).update({
            "plano": "premium"
        })
        st.success("Plano atualizado para PREMIUM")
        st.rerun()
