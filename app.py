import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from streamlit_option_menu import option_menu
import plotly.express as px
import pandas as pd

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="ServiçoPro SaaS",
    layout="wide",
    page_icon="🚀"
)

# ==================================================
# CSS PREMIUM
# ==================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #050816 0%, #0B1026 50%, #111827 100%);
    color: white;
}

section[data-testid="stSidebar"] {
    background: #0B1026;
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.metric-card {
    background: linear-gradient(135deg, rgba(79,70,229,0.35), rgba(6,182,212,0.25));
    padding: 25px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 0 25px rgba(79,70,229,0.25);
}

.card {
    background: rgba(17,24,39,0.75);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
}

.main-title {
    font-size: 42px;
    font-weight: bold;
    color: white;
}

.subtitle {
    color: #94A3B8;
    margin-bottom: 25px;
}

div.stButton > button {
    background: linear-gradient(90deg, #7C3AED, #06B6D4);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# FIREBASE INIT
# ==================================================

try:
    firebase_admin.get_app()

except ValueError:

    firebase_config = st.secrets["firebase"]

    firebase_dict = dict(firebase_config)

    firebase_dict["private_key"] = firebase_dict[
        "private_key"
    ].replace("\\n", "\n")

    cred = credentials.Certificate(firebase_dict)

    firebase_admin.initialize_app(cred)

db = firestore.client()

# ==================================================
# SESSION STATE
# ==================================================

if "auth" not in st.session_state:
    st.session_state.auth = False

if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = None

# ==================================================
# LOGIN
# ==================================================

def login():

    doc = db.collection("usuarios").document("user123").get()

    if not doc.exists:
        return False

    user = doc.to_dict()

    empresa = user.get("empresa_id")

    if not empresa:
        return False

    st.session_state.auth = True
    st.session_state.empresa_id = empresa

    return True

# ==================================================
# LOGOUT
# ==================================================

def logout():
    st.session_state.auth = False
    st.session_state.empresa_id = None
    st.rerun()

# ==================================================
# LOGIN SCREEN
# ==================================================

if not st.session_state.auth:

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown("""
        <div class="card">
            <h1 style="text-align:center;">🚀 ServiçoPro SaaS</h1>
            <p style="text-align:center;color:#94A3B8;">
                Plataforma inteligente de gestão
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Entrar no Sistema", use_container_width=True):

            if login():
                st.rerun()

            else:
                st.error("Erro ao entrar")

    st.stop()

# ==================================================
# CONTEXTO EMPRESA
# ==================================================

empresa_id = st.session_state.empresa_id

empresa_ref = db.collection("empresas").document(empresa_id)

clientes_ref = empresa_ref.collection("clientes")
servicos_ref = empresa_ref.collection("servicos")

clientes = list(clientes_ref.get())
servicos = list(servicos_ref.get())

total_clientes = len(clientes)
total_servicos = len(servicos)

# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown("# 🚀 ServiçoPro")

    menu = option_menu(
        menu_title=None,
        options=[
            "Dashboard",
            "Clientes",
            "Serviços",
            "Financeiro"
        ],
        icons=[
            "speedometer2",
            "people",
            "tools",
            "cash-stack"
        ],
        default_index=0
    )

    st.markdown("---")

    st.write(f"Empresa: {empresa_id}")

    st.button(
        "🚪 Logout",
        on_click=logout,
        use_container_width=True
    )

# ==================================================
# DASHBOARD
# ==================================================

if menu == "Dashboard":

    st.markdown(
        "<div class='main-title'>Dashboard</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>Visão geral do sistema</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(f"""
        <div class="metric-card">
            <h3>👤 Clientes</h3>
            <h1>{total_clientes}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="metric-card">
            <h3>🛠 Serviços</h3>
            <h1>{total_servicos}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:

        faturamento = total_servicos * 150

        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Faturamento</h3>
            <h1>R$ {faturamento}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    dados = pd.DataFrame({
        "Mes": ["Jan", "Fev", "Mar", "Abr", "Mai"],
        "Serviços": [5, 9, 12, 18, total_servicos]
    })

    fig = px.line(
        dados,
        x="Mes",
        y="Serviços",
        markers=True,
        template="plotly_dark"
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# CLIENTES
# ==================================================

elif menu == "Clientes":

    st.markdown(
        "<div class='main-title'>Clientes</div>",
        unsafe_allow_html=True
    )

    nome = st.text_input("Nome do cliente")

    if st.button("➕ Adicionar Cliente") and nome:

        clientes_ref.add({
            "nome": nome
        })

        st.success("Cliente adicionado")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    for c in clientes:

        data = c.to_dict()

        col1, col2 = st.columns([8,1])

        with col1:

            st.markdown(f"""
            <div class="card">
                👤 {data.get('nome')}
            </div>
            """, unsafe_allow_html=True)

        with col2:

            if st.button("🗑", key=c.id):

                clientes_ref.document(c.id).delete()
                st.rerun()

# ==================================================
# SERVIÇOS
# ==================================================

elif menu == "Serviços":

    st.markdown(
        "<div class='main-title'>Serviços</div>",
        unsafe_allow_html=True
    )

    cliente = st.text_input("Cliente")
    servico = st.text_input("Serviço")

    if st.button("➕ Salvar Serviço") and cliente and servico:

        servicos_ref.add({
            "cliente": cliente,
            "servico": servico
        })

        st.success("Serviço salvo")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    for s in servicos:

        data = s.to_dict()

        col1, col2 = st.columns([8,1])

        with col1:

            st.markdown(f"""
            <div class="card">
                🛠 {data.get('cliente')} - {data.get('servico')}
            </div>
            """, unsafe_allow_html=True)

        with col2:

            if st.button("🗑", key=s.id):

                servicos_ref.document(s.id).delete()
                st.rerun()

# ==================================================
# FINANCEIRO
# ==================================================

elif menu == "Financeiro":

    st.markdown(
        "<div class='main-title'>Financeiro</div>",
        unsafe_allow_html=True
    )

    faturamento = total_servicos * 150

    st.markdown(f"""
    <div class="metric-card">
        <h1>💰 R$ {faturamento}</h1>
        <p>Faturamento estimado</p>
    </div>
    """, unsafe_allow_html=True)
