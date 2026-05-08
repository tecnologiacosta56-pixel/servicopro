import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import os

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="ServiçoPro SaaS",
    layout="wide",
    page_icon="🚀"
)

# ==================================================
# CSS PREMIUM / DASHBOARD IMPACTANTE
# ==================================================

st.markdown("""
<style>
:root {
    --bg-1: #020617;
    --bg-2: #0b1120;
    --panel: rgba(15, 23, 42, 0.72);
    --panel-border: rgba(255,255,255,0.08);
    --text: #E5EEF8;
    --muted: #94A3B8;
    --primary: #7C3AED;
    --secondary: #06B6D4;
    --success: #22C55E;
    --danger: #ef4444;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(124, 58, 237, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(6, 182, 212, 0.12), transparent 25%),
        linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 48%, #07111f 100%);
    color: var(--text);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1320px;
}

/* Sidebar */
section[data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, #081120 0%, #0f172a 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}

section[data-testid="stSidebar"] * {
    color: #E5EEF8 !important;
}

/* Botões */
div.stButton > button {
    background: linear-gradient(90deg, #7C3AED, #06B6D4);
    color: white;
    border-radius: 12px;
    font-weight: 600;
    border: none;
    padding: 0.6rem 1rem;
    transition: all 0.2s ease;
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.22);
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 14px 36px rgba(6, 182, 212, 0.20);
}

/* Inputs */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background: rgba(15, 23, 42, 0.72) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: white !important;
}

/* Hero */
.hero {
    background:
        linear-gradient(135deg, rgba(124,58,237,0.22), rgba(6,182,212,0.10)),
        rgba(15,23,42,0.70);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 24px 80px rgba(0,0,0,0.28);
    backdrop-filter: blur(12px);
    margin-bottom: 22px;
}

.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    color: #C7D2FE;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    margin-bottom: 14px;
}

.hero h1 {
    color: #F8FAFC;
    font-size: 2rem;
    line-height: 1.1;
    margin: 0;
}

.hero p {
    color: var(--muted);
    font-size: 1rem;
    margin-top: 10px;
    margin-bottom: 0;
}

.hero-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0,1fr));
    gap: 14px;
    margin-top: 22px;
}

/* Cards */
.mini-stat,
.kpi-card,
.progress-card,
.insight-card,
.list-card,
.form-card {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 20px;
    padding: 18px;
    backdrop-filter: blur(10px);
}

.mini-stat span,
.kpi-value {
    display: block;
    color: #F8FAFC;
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1;
}

.mini-stat small,
.kpi-label,
.kpi-foot {
    color: var(--muted);
}

.kpi-label {
    font-size: 0.92rem;
    margin-bottom: 8px;
    display: block;
}

.kpi-foot {
    font-size: 0.85rem;
    margin-top: 10px;
    display: block;
}

.progress-track {
    width: 100%;
    height: 10px;
    border-radius: 999px;
    background: rgba(255,255,255,0.06);
    overflow: hidden;
    margin-top: 14px;
}

.progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #7C3AED, #06B6D4);
}

.insight-title {
    color: #F8FAFC;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 6px;
}

.insight-text {
    color: var(--muted);
    font-size: 0.95rem;
}

/* Títulos de seção */
.section-title {
    color: #F8FAFC;
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 10px;
}

/* Lista */
.list-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
}

/* Login */
.login-wrap {
    max-width: 760px;
    margin: 3rem auto 0 auto;
}

.login-card {
    background:
        linear-gradient(135deg, rgba(124,58,237,0.18), rgba(6,182,212,0.08)),
        rgba(15,23,42,0.72);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 26px;
    padding: 34px;
    box-shadow: 0 24px 80px rgba(0,0,0,0.30);
    text-align: center;
}

.login-card h1 {
    color: #F8FAFC;
    margin-bottom: 8px;
}

.login-card p {
    color: var(--muted);
    margin-bottom: 20px;
}

@media (max-width: 900px) {
    .hero-grid {
        grid-template-columns: 1fr;
    }
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
    firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
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
# LOGIN FIXO (user123)
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
    st.markdown("""
    <div class="login-wrap">
        <div class="login-card">
            <div class="badge">SERVIÇOPRO • SaaS</div>
            <h1>Gestão técnica com presença profissional</h1>
            <p>
                Centralize clientes, serviços e atendimentos em uma plataforma
                limpa, moderna e pronta para operação técnica.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("Entrar"):
            if login():
                st.rerun()
            else:
                st.error("Erro login")

    st.stop()

# ==================================================
# CONTEXTO EMPRESA
# ==================================================

empresa_id = st.session_state.empresa_id

empresa_ref = db.collection("empresas").document(empresa_id)
clientes_ref = empresa_ref.collection("clientes")
servicos_ref = empresa_ref.collection("servicos")

# ==================================================
# SIDEBAR
# ==================================================

if os.path.exists("assets/logo.png"):
    st.sidebar.image("assets/logo.png", width=160)
else:
    st.sidebar.markdown("## 🚀 ServiçoPro")

st.sidebar.markdown("## ServiçoPro")
st.sidebar.write(f"**Empresa:** {empresa_id}")
st.sidebar.button("🚪 Logout", on_click=logout)

menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Clientes", "Serviços"]
)

# ==================================================
# DASHBOARD PREMIUM
# ==================================================

if menu == "Dashboard":

    clientes = list(clientes_ref.get())
    servicos = list(servicos_ref.get())

    total_clientes = len(clientes)
    total_servicos = len(servicos)
    total_registros = total_clientes + total_servicos

    meta_clientes = 10
    meta_servicos = 20

    pct_clientes = min(int((total_clientes / meta_clientes) * 100), 100) if meta_clientes else 0
    pct_servicos = min(int((total_servicos / meta_servicos) * 100), 100) if meta_servicos else 0

    st.markdown(f"""
    <div class="hero">
        <div class="badge">SERVIÇOPRO • PAINEL OPERACIONAL</div>
        <h1>Gestão técnica com visual premium e operação sob controle</h1>
        <p>
            Centralize clientes, ordens de serviço e atendimentos em um dashboard limpo,
            elegante e pensado para profissionais e empresas da área técnica.
        </p>

        <div class="hero-grid">
            <div class="mini-stat">
                <span>{total_clientes}</span>
                <small>Clientes cadastrados</small>
            </div>
            <div class="mini-stat">
                <span>{total_servicos}</span>
                <small>Serviços registrados</small>
            </div>
            <div class="mini-stat">
                <span>Ativo</span>
                <small>Ambiente da empresa</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-label">Clientes</span>
            <span class="kpi-value">{total_clientes}</span>
            <span class="kpi-foot">Base atual cadastrada</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-label">Serviços</span>
            <span class="kpi-value">{total_servicos}</span>
            <span class="kpi-foot">Operações registradas</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-label">Registros totais</span>
            <span class="kpi-value">{total_registros}</span>
            <span class="kpi-foot">Clientes + serviços</span>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-title">Metas operacionais</div>', unsafe_allow_html=True)

    colA, colB = st.columns(2)

    with colA:
        st.markdown(f"""
        <div class="progress-card">
            <span class="kpi-label">Meta de clientes</span>
            <span class="kpi-value">{pct_clientes}%</span>
            <div class="progress-track">
                <div class="progress-fill" style="width:{pct_clientes}%;"></div>
            </div>
            <span class="kpi-foot">{total_clientes} de {meta_clientes} clientes</span>
        </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown(f"""
        <div class="progress-card">
            <span class="kpi-label">Meta de serviços</span>
            <span class="kpi-value">{pct_servicos}%</span>
            <div class="progress-track">
                <div class="progress-fill" style="width:{pct_servicos}%;"></div>
            </div>
            <span class="kpi-foot">{total_servicos} de {meta_servicos} serviços</span>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-title">Insights</div>', unsafe_allow_html=True)

    if total_clientes == 0 and total_servicos == 0:
        insight_title = "Começo limpo"
        insight_text = "Seu painel está pronto para iniciar a operação. Cadastre os primeiros clientes e serviços para ganhar tração."
    elif total_clientes < 5:
        insight_title = "Base em formação"
        insight_text = "Você já começou bem. O próximo passo é aumentar a base de clientes e transformar o painel em rotina operacional."
    elif total_servicos < total_clientes:
        insight_title = "Oportunidade de ativação"
        insight_text = "Você tem mais clientes do que serviços registrados. Pode haver atendimentos acontecendo fora do sistema."
    else:
        insight_title = "Operação ganhando ritmo"
        insight_text = "Seu uso já demonstra atividade consistente. Agora vale evoluir para status, filtros e acompanhamento por etapa."

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">{insight_title}</div>
        <div class="insight-text">{insight_text}</div>
    </div>
    """, unsafe_allow_html=True)

# ==================================================
# CLIENTES
# ==================================================

elif menu == "Clientes":

    st.markdown("""
    <div class="hero">
        <div class="badge">GESTÃO DE CLIENTES</div>
        <h1>Cadastre e mantenha sua base organizada</h1>
        <p>
            Tenha uma visão mais profissional da sua carteira de clientes e mantenha
            seu atendimento técnico centralizado.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Novo cliente</div>', unsafe_allow_html=True)

    with st.container():
        nome = st.text_input("Nome do cliente")

        if st.button("➕ Adicionar cliente") and nome:
            clientes_ref.add({"nome": nome})
            st.rerun()

    st.write("")
    st.markdown('<div class="section-title">Clientes cadastrados</div>', unsafe_allow_html=True)

    clientes_lista = list(clientes_ref.get())

    if not clientes_lista:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        for c in clientes_lista:
            data = c.to_dict()

            col1, col2 = st.columns([8, 2])

            with col1:
                st.markdown(f"""
                <div class="list-item">
                    👤 {data.get('nome', 'Sem nome')}
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button("🗑 Excluir", key=f"del_cliente_{c.id}"):
                    clientes_ref.document(c.id).delete()
                    st.rerun()

# ==================================================
# SERVIÇOS
# ==================================================

elif menu == "Serviços":

    st.markdown("""
    <div class="hero">
        <div class="badge">GESTÃO DE SERVIÇOS</div>
        <h1>Registre atendimentos e serviços com clareza</h1>
        <p>
            Organize sua operação técnica com mais controle sobre clientes,
            atividades executadas e histórico de atendimento.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Novo serviço</div>', unsafe_allow_html=True)

    cliente = st.text_input("Cliente")
    servico = st.text_input("Serviço")

    if st.button("➕ Salvar serviço") and cliente and servico:
        servicos_ref.add({
            "cliente": cliente,
            "servico": servico
        })
        st.rerun()

    st.write("")
    st.markdown('<div class="section-title">Serviços registrados</div>', unsafe_allow_html=True)

    servicos_lista = list(servicos_ref.get())

    if not servicos_lista:
        st.info("Nenhum serviço registrado ainda.")
    else:
        for s in servicos_lista:
            data = s.to_dict()

            col1, col2 = st.columns([8, 2])

            with col1:
                st.markdown(f"""
                <div class="list-item">
                    🛠 {data.get('cliente', 'Sem cliente')} — {data.get('servico', 'Sem serviço')}
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button("🗑 Excluir", key=f"del_servico_{s.id}"):
                    servicos_ref.document(s.id).delete()
                    st.rerun()
