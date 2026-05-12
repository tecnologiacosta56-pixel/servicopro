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
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# ==================================================
# CSS PREMIUM
# ==================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.stApp {
    background:
    radial-gradient(circle at top left, rgba(124,58,237,0.25), transparent 25%),
    radial-gradient(circle at bottom right, rgba(6,182,212,0.18), transparent 25%),
    linear-gradient(135deg, #050816 0%, #0B1026 50%, #111827 100%);
    color: white;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: rgba(11,16,38,0.95);
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* TITLES */

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: white;
    margin-bottom: 5px;
}

.subtitle {
    color: #94A3B8;
    margin-bottom: 25px;
}

/* CARDS */

.metric-card {
    background: linear-gradient(
        135deg,
        rgba(124,58,237,0.35),
        rgba(6,182,212,0.22)
    );

    padding: 25px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.08);

    backdrop-filter: blur(14px);

    box-shadow:
        0 0 25px rgba(124,58,237,0.25),
        inset 0 0 1px rgba(255,255,255,0.2);

    transition: 0.3s;
}

.metric-card:hover {
    transform: translateY(-4px);
}

.card {
    background: rgba(17,24,39,0.72);

    padding: 20px;

    border-radius: 18px;

    border: 1px solid rgba(255,255,255,0.08);

    backdrop-filter: blur(14px);

    margin-bottom: 12px;
}

/* BUTTONS */

div.stButton > button {
    background: linear-gradient(
        90deg,
        #7C3AED,
        #06B6D4
    );

    color: white;

    border: none;

    border-radius: 12px;

    font-weight: 700;

    padding: 0.7rem 1rem;

    transition: 0.3s;
}

div.stButton > button:hover {
    transform: scale(1.02);
    opacity: 0.92;
}

/* INPUTS */

.stTextInput input {
    background-color: rgba(255,255,255,0.06);
    color: white;
    border-radius: 10px;
}

/* SUCCESS */

.stSuccess {
    border-radius: 12px;
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
# SESSION
# ==================================================

if "auth" not in st.session_state:
    st.session_state.auth = False

if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = None

if "editando_cliente" not in st.session_state:
    st.session_state.editando_cliente = None

if "editando_servico" not in st.session_state:
    st.session_state.editando_servico = None

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
            <h1 style="text-align:center;">
                🚀 ServiçoPro SaaS
            </h1>

            <p style="text-align:center;color:#94A3B8;">
                Plataforma inteligente de gestão empresarial
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "Entrar no Sistema",
            width="stretch"
        ):

            if login():
                st.rerun()

            else:
                st.error("Erro ao entrar")

    st.stop()

# ==================================================
# FIRESTORE
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

# ==================================================
# SIDEBAR PREMIUM
# ==================================================

with st.sidebar:

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================================================
    # LOGO
    # ==================================================

    col_logo, col_texto = st.columns([1,2])

    with col_logo:

        st.image(
            "assets/logo.png",
            width=55
        )

    with col_texto:

        st.markdown("""
        <h2 style="
            color:white;
            margin-bottom:-8px;
        ">
            ServiçoPro
        </h2>

        <p style="
            color:#A78BFA;
            font-size:13px;
        ">
            SaaS Enterprise
        </p>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================================================
    # MENU
    # ==================================================

    menu = option_menu(
        menu_title=None,

        options=[
            "Dashboard",
            "Clientes",
            "Serviços",
            "Agenda",
            "Financeiro",
            "Relatórios",
            "Configurações"
        ],

        icons=[
            "grid",
            "people",
            "tools",
            "calendar-event",
            "cash-stack",
            "bar-chart",
            "gear"
        ],

        default_index=0,

        styles={

            "container": {
                "padding": "0!important",
                "background-color": "transparent",
            },

            "icon": {
                "color": "#A78BFA",
                "font-size": "18px",
            },

            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "8px 0",
                "padding": "14px",
                "border-radius": "14px",
                "background-color": "rgba(255,255,255,0.02)",
                "color": "white",
            },

            "nav-link-selected": {
                "background":
                "linear-gradient(90deg,#7C3AED,#06B6D4)",

                "box-shadow":
                "0 0 18px rgba(124,58,237,0.45)",

                "color": "white",
            },
        }
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================================================
    # CARD PRO
    # ==================================================

    st.markdown("""
    <div style="
        background:
        linear-gradient(
            135deg,
            rgba(124,58,237,0.25),
            rgba(6,182,212,0.15)
        );

        padding:22px;

        border-radius:22px;

        border:1px solid rgba(255,255,255,0.08);

        box-shadow:
            0 0 22px rgba(124,58,237,0.18);

        margin-bottom:25px;
    ">

    <h3 style="
        color:white;
    ">
        🚀 Plano PRO
    </h3>

    <p style="
        color:#CBD5E1;
        font-size:14px;
    ">
        Recursos premium ativos no seu sistema.
    </p>

    <div style="
        margin-top:15px;

        background:
        linear-gradient(
            90deg,
            #7C3AED,
            #06B6D4
        );

        padding:10px;

        border-radius:12px;

        text-align:center;

        color:white;

        font-weight:bold;
    ">
        Plano Ativo
    </div>

    </div>
    """, unsafe_allow_html=True)

    # ==================================================
    # STATUS
    # ==================================================

    st.markdown("""
    <div style="
        background:rgba(255,255,255,0.03);

        padding:18px;

        border-radius:18px;

        border:1px solid rgba(255,255,255,0.06);

        margin-bottom:20px;
    ">

    <p style="color:#4ADE80;">
        ● Sistema Online
    </p>

    <p style="color:#38BDF8;">
        ● Firebase Conectado
    </p>

    <p style="color:#A78BFA;">
        ● Dashboard Enterprise
    </p>

    </div>
    """, unsafe_allow_html=True)

    # ==================================================
    # EMPRESA
    # ==================================================

    st.markdown(f"""
    <div style="
        background:rgba(255,255,255,0.03);

        padding:18px;

        border-radius:18px;

        border:1px solid rgba(255,255,255,0.06);

        margin-bottom:20px;
    ">

    <h4 style="
        color:white;
    ">
        🏢 Empresa
    </h4>

    <p style="
        color:#CBD5E1;
    ">
        {empresa_id}
    </p>

    </div>
    """, unsafe_allow_html=True)

    # ==================================================
    # LOGOUT
    # ==================================================

    st.button(
        "🚪 Sair do Sistema",
        on_click=logout,
        width="stretch"
    )
# ==================================================
# DASHBOARD
# ==================================================

# ==================================================
# DASHBOARD PREMIUM
# ==================================================

# ==================================================
# DASHBOARD ENTERPRISE
# ==================================================

if menu == "Dashboard":

    faturamento = total_servicos * 150

    # ==================================================
    # HERO SECTION
    # ==================================================

    st.markdown(f"""
    <div style="
        background:
        linear-gradient(
            135deg,
            rgba(124,58,237,0.28),
            rgba(6,182,212,0.18)
        );

        padding:35px;

        border-radius:28px;

        border:1px solid rgba(255,255,255,0.08);

        backdrop-filter:blur(20px);

        box-shadow:
            0 0 40px rgba(124,58,237,0.22);

        margin-bottom:30px;
    ">

    <h1 style="
        color:white;
        font-size:48px;
        margin-bottom:10px;
    ">
        🚀 ServiçoPro Enterprise
    </h1>

    <p style="
        color:#CBD5E1;
        font-size:18px;
        margin-bottom:0;
    ">
        Plataforma inteligente de gestão empresarial premium
    </p>

    </div>
    """, unsafe_allow_html=True)

    # ==================================================
    # METRICS
    # ==================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(f"""
        <div class="metric-card">

        <p style="
            color:#94A3B8;
            margin-bottom:8px;
        ">
            👥 Clientes
        </p>

        <h1 style="color:white;">
            {total_clientes}
        </h1>

        <p style="color:#4ADE80;">
            +12% crescimento
        </p>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="metric-card">

        <p style="
            color:#94A3B8;
            margin-bottom:8px;
        ">
            🛠 Serviços
        </p>

        <h1 style="color:white;">
            {total_servicos}
        </h1>

        <p style="color:#38BDF8;">
            +18% performance
        </p>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="metric-card">

        <p style="
            color:#94A3B8;
            margin-bottom:8px;
        ">
            💰 Receita
        </p>

        <h1 style="color:white;">
            R$ {faturamento}
        </h1>

        <p style="color:#4ADE80;">
            +25% este mês
        </p>

        </div>
        """, unsafe_allow_html=True)

    with col4:

        st.markdown(f"""
        <div class="metric-card">

        <p style="
            color:#94A3B8;
            margin-bottom:8px;
        ">
            ⚡ Eficiência
        </p>

        <h1 style="color:white;">
            92%
        </h1>

        <p style="color:#A78BFA;">
            Operação saudável
        </p>

        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================================================
    # GRID
    # ==================================================

    left, right = st.columns([2,1])

    # ==================================================
    # LEFT
    # ==================================================

    with left:

        st.markdown("""
        <div class="card">

        <h3 style="
            color:white;
            margin-bottom:15px;
        ">
            📈 Crescimento Operacional
        </h3>

        </div>
        """, unsafe_allow_html=True)

        dados = pd.DataFrame({
            "Mes": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
            "Receita": [1500, 3200, 5800, 7200, 9800, faturamento]
        })

        fig = px.area(
            dados,
            x="Mes",
            y="Receita",
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            margin=dict(l=0,r=0,t=10,b=0)
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background:
            linear-gradient(
                135deg,
                rgba(124,58,237,0.22),
                rgba(6,182,212,0.15)
            );

            padding:28px;

            border-radius:24px;

            border:1px solid rgba(255,255,255,0.08);

            box-shadow:
                0 0 30px rgba(124,58,237,0.18);
        ">

        <h2 style="color:white;">
            🧠 Inteligência Operacional
        </h2>

        <p style="
            color:#CBD5E1;
            font-size:15px;
        ">
            Seu sistema está operando com alta performance.
        </p>

        <h1 style="
            color:#4ADE80;
            font-size:58px;
        ">
            98%
        </h1>

        <p style="
            color:#94A3B8;
        ">
            Estabilidade da plataforma
        </p>

        </div>
        """, unsafe_allow_html=True)

    # ==================================================
    # RIGHT
    # ==================================================

    with right:

        st.markdown("""
        <div class="card">

        <h3 style="color:white;">
            ⚡ Atividades Recentes
        </h3>

        <hr style="
            border:1px solid rgba(255,255,255,0.08);
        ">

        <p style="color:#E2E8F0;">
            👤 Novo cliente cadastrado
        </p>

        <p style="
            color:#94A3B8;
            margin-top:-10px;
        ">
            há 2 minutos
        </p>

        <p style="color:#E2E8F0;">
            🛠 Serviço concluído
        </p>

        <p style="
            color:#94A3B8;
            margin-top:-10px;
        ">
            há 15 minutos
        </p>

        <p style="color:#E2E8F0;">
            💰 Pagamento recebido
        </p>

        <p style="
            color:#94A3B8;
            margin-top:-10px;
        ">
            há 1 hora
        </p>

        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="card">

        <h3 style="color:white;">
            🌐 Infraestrutura
        </h3>

        <hr style="
            border:1px solid rgba(255,255,255,0.08);
        ">

        <p style="color:#4ADE80;">
            ● Firebase Online
        </p>

        <p style="color:#38BDF8;">
            ● Streamlit Estável
        </p>

        <p style="color:#A78BFA;">
            ● Plano Enterprise
        </p>

        <p style="color:#F472B6;">
            ● Segurança Ativa
        </p>

        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="card">

        <h3 style="color:white;">
            ⚙ Ações Rápidas
        </h3>

        <hr style="
            border:1px solid rgba(255,255,255,0.08);
        ">

        <p style="color:#E2E8F0;">
            ➕ Novo Cliente
        </p>

        <p style="color:#E2E8F0;">
            🛠 Novo Serviço
        </p>

        <p style="color:#E2E8F0;">
            💰 Financeiro
        </p>

        <p style="color:#E2E8F0;">
            📊 Relatórios
        </p>

        </div>
        """, unsafe_allow_html=True)
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

        col1, col2, col3 = st.columns([8,1,2])

        with col1:

            st.markdown(f"""
            <div class="card">
                👤 {data.get('nome')}
            </div>
            """, unsafe_allow_html=True)

        with col2:

            if st.button(
                "✏️",
                key=f"edit_cliente_{c.id}"
            ):

                st.session_state.editando_cliente = c.id

        with col3:

            if st.button(
                "🗑 Excluir",
                key=f"ask_delete_cliente_{c.id}"
            ):

                st.session_state[f"confirm_delete_cliente_{c.id}"] = True

        # CONFIRMAÇÃO DELETE

        if st.session_state.get(f"confirm_delete_cliente_{c.id}"):

            st.warning("Tem certeza que deseja excluir?")

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "✅ Sim",
                    key=f"confirm_yes_cliente_{c.id}"
                ):

                    clientes_ref.document(c.id).delete()

                    st.success("Cliente removido")

                    st.rerun()

            with c2:

                if st.button(
                    "❌ Cancelar",
                    key=f"cancel_cliente_{c.id}"
                ):

                    st.session_state[
                        f"confirm_delete_cliente_{c.id}"
                    ] = False

                    st.rerun()

        # EDITAR

        if st.session_state.editando_cliente == c.id:

            novo_nome = st.text_input(
                "Editar nome",
                value=data.get("nome"),
                key=f"novo_nome_{c.id}"
            )

            salvar = st.button(
                "Salvar Alterações",
                key=f"save_cliente_{c.id}"
            )

            if salvar:

                clientes_ref.document(c.id).update({
                    "nome": novo_nome
                })

                st.session_state.editando_cliente = None

                st.success("Cliente atualizado")

                st.rerun()
# ==================================================
# SERVIÇOS
# ==================================================

# ==================================================
# SERVIÇOS
# ==================================================

elif menu == "Serviços":
    st.markdown(
        "<div class='main-title'>Serviços</div>",
        unsafe_allow_html=True
    )
# ==================================================
# AGENDA
# ==================================================

elif menu == "Agenda":

    st.markdown("""
    <div style="
        background:
        linear-gradient(
            135deg,
            rgba(124,58,237,0.25),
            rgba(6,182,212,0.15)
        );

        padding:30px;

        border-radius:26px;

        border:1px solid rgba(255,255,255,0.08);

        box-shadow:
            0 0 30px rgba(124,58,237,0.18);

        margin-bottom:25px;
    ">

    <h1 style="
        color:white;
        margin-bottom:10px;
    ">
        📅 Agenda Inteligente
    </h1>

    <p style="
        color:#CBD5E1;
        font-size:16px;
    ">
        Gerencie seus atendimentos e serviços em tempo real
    </p>

    </div>
    """, unsafe_allow_html=True)

    # ==================================================
    # KPIS
    # ==================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("""
        <div class="metric-card">

        <h3>📌 Agendamentos</h3>

        <h1>12</h1>

        <p style="color:#4ADE80;">
            +4 hoje
        </p>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="metric-card">

        <h3>🛠 Serviços Hoje</h3>

        <h1>8</h1>

        <p style="color:#38BDF8;">
            agenda ativa
        </p>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown("""
        <div class="metric-card">

        <h3>⚡ Eficiência</h3>

        <h1>94%</h1>

        <p style="color:#A78BFA;">
            alta performance
        </p>

        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================================================
    # AGENDA GRID
    # ==================================================

    left, right = st.columns([2,1])

    # ==================================================
    # LEFT
    # ==================================================

    with left:

        st.markdown("""
        <div class="card">

        <h3 style="color:white;">
            📅 Agenda do Dia
        </h3>

        <hr style="
            border:1px solid rgba(255,255,255,0.08);
        ">

        <div style="
            background:rgba(255,255,255,0.03);
            padding:18px;
            border-radius:16px;
            margin-bottom:15px;
        ">
            <h4 style="color:white;">
                08:00 - Instalação Elétrica
            </h4>

            <p style="color:#CBD5E1;">
                Cliente: João Silva
            </p>

            <p style="color:#4ADE80;">
                ● Confirmado
            </p>
        </div>

        <div style="
            background:rgba(255,255,255,0.03);
            padding:18px;
            border-radius:16px;
            margin-bottom:15px;
        ">
            <h4 style="color:white;">
                11:30 - Automação Residencial
            </h4>

            <p style="color:#CBD5E1;">
                Cliente: Carlos Tech
            </p>

            <p style="color:#38BDF8;">
                ● Em andamento
            </p>
        </div>

        <div style="
            background:rgba(255,255,255,0.03);
            padding:18px;
            border-radius:16px;
        ">
            <h4 style="color:white;">
                15:00 - Manutenção Industrial
            </h4>

            <p style="color:#CBD5E1;">
                Cliente: Empresa Alpha
            </p>

            <p style="color:#F59E0B;">
                ● Pendente
            </p>
        </div>

        </div>
        """, unsafe_allow_html=True)

    # ==================================================
    # RIGHT
    # ==================================================

    with right:

        st.markdown("""
        <div class="card">

        <h3 style="color:white;">
            ⚡ Resumo
        </h3>

        <hr style="
            border:1px solid rgba(255,255,255,0.08);
        ">

        <p style="color:#E2E8F0;">
            📌 12 agendamentos
        </p>

        <p style="color:#E2E8F0;">
            🛠 8 serviços ativos
        </p>

        <p style="color:#E2E8F0;">
            👥 5 clientes hoje
        </p>

        <p style="color:#E2E8F0;">
            💰 Receita prevista: R$ 3.200
        </p>

        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="card">

        <h3 style="color:white;">
            🚀 Produtividade
        </h3>

        <hr style="
            border:1px solid rgba(255,255,255,0.08);
        ">

        <h1 style="
            color:#4ADE80;
            font-size:52px;
        ">
            94%
        </h1>

        <p style="color:#94A3B8;">
            taxa operacional do dia
        </p>

        </div>
        """, unsafe_allow_html=True)
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
