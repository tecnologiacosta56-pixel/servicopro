import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import mercadopago
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
# MERCADO PAGO
# ==================================================

sdk = mercadopago.SDK(
    st.secrets["mercadopago"]["MP_ACCESS_TOKEN"]
)

# ==================================================
# SESSION STATE
# ==================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "uid" not in st.session_state:
    st.session_state["uid"] = None

if "empresa_id" not in st.session_state:
    st.session_state["empresa_id"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

# ==================================================
# LOGIN
# ==================================================

def login(email):

    users = db.collection("usuarios").where(
        "email",
        "==",
        email
    ).stream()

    for u in users:

        data = u.to_dict()

        if "empresa_id" not in data:
            return False

        st.session_state["uid"] = u.id

        st.session_state["empresa_id"] = data[
            "empresa_id"
        ]

        st.session_state["role"] = data.get(
            "role",
            "member"
        )

        st.session_state["authenticated"] = True

        return True

    return False

# ==================================================
# LOGOUT
# ==================================================

def logout():

    st.session_state["authenticated"] = False
    st.session_state["uid"] = None
    st.session_state["empresa_id"] = None
    st.session_state["role"] = None

    st.rerun()

# ==================================================
# LOGIN SCREEN
# ==================================================

if not st.session_state["authenticated"]:

    st.title("🔐 Login ServiçoPro SaaS")

    email = st.text_input("Email")

    st.info(
        "Sistema em modo MVP. "
        "Digite o email cadastrado no Firestore."
    )

    if st.button("Entrar"):

        if login(email):

            st.success(
                "Login realizado com sucesso!"
            )

        else:

            st.error(
                "Usuário não encontrado."
            )

    st.stop()

# ==================================================
# CONTEXTO EMPRESA
# ==================================================

empresa_id = st.session_state["empresa_id"]

empresa_ref = db.collection(
    "empresas"
).document(
    empresa_id
)

clientes_ref = empresa_ref.collection(
    "clientes"
)

servicos_ref = empresa_ref.collection(
    "servicos"
)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("🚀 ServiçoPro")

st.sidebar.write(
    f"Empresa: {empresa_id}"
)

st.sidebar.write(
    f"Perfil: {st.session_state['role']}"
)

st.sidebar.button(
    "🚪 Logout",
    on_click=logout
)

menu = st.sidebar.selectbox(
    "📌 Menu",
    [
        "📊 Dashboard",
        "👤 Clientes",
        "🛠 Serviços",
        "💳 Plano"
    ]
)

# ==================================================
# DASHBOARD
# ==================================================

if menu == "📊 Dashboard":

    st.title("📊 Dashboard SaaS")

    clientes = list(
        clientes_ref.stream()
    )

    servicos = list(
        servicos_ref.stream()
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Empresa",
        empresa_id
    )

    col2.metric(
        "Clientes",
        len(clientes)
    )

    col3.metric(
        "Serviços",
        len(servicos)
    )

    chart_data = pd.DataFrame({
        "Categoria": [
            "Clientes",
            "Serviços"
        ],
        "Total": [
            len(clientes),
            len(servicos)
        ]
    })

    st.bar_chart(
        chart_data.set_index(
            "Categoria"
        )
    )

# ==================================================
# CLIENTES
# ==================================================

elif menu == "👤 Clientes":

    st.title("👤 Clientes")

    nome = st.text_input(
        "Nome do cliente"
    )

    if st.button(
        "➕ Adicionar Cliente"
    ):

        if nome:

            clientes_ref.add({
                "nome": nome
            })

            st.success(
                "Cliente adicionado!"
            )

            st.rerun()

    st.divider()

    clientes = clientes_ref.stream()

    for c in clientes:

        data = c.to_dict()

        col1, col2 = st.columns([8, 2])

        with col1:

            st.write(
                f"👤 {data['nome']}"
            )

        with col2:

            if st.button(
                "🗑 Excluir",
                key=c.id
            ):

                clientes_ref.document(
                    c.id
                ).delete()

                st.rerun()

# ==================================================
# SERVIÇOS
# ==================================================

elif menu == "🛠 Serviços":

    st.title("🛠 Serviços")

    cliente = st.text_input(
        "Cliente"
    )

    servico = st.text_input(
        "Serviço"
    )

    if st.button(
        "➕ Salvar Serviço"
    ):

        if cliente and servico:

            servicos_ref.add({
                "cliente": cliente,
                "servico": servico
            })

            st.success(
                "Serviço salvo!"
            )

            st.rerun()

    st.divider()

    servicos = servicos_ref.stream()

    for s in servicos:

        data = s.to_dict()

        col1, col2 = st.columns([8, 2])

        with col1:

            st.write(
                f"🛠 {data['cliente']} - {data['servico']}"
            )

        with col2:

            if st.button(
                "🗑 Excluir",
                key=s.id
            ):

                servicos_ref.document(
                    s.id
                ).delete()

                st.rerun()

# ==================================================
# PLANO
# ==================================================

elif menu == "💳 Plano":

    st.title("💳 Plano SaaS")

    st.success(
        "Sistema estabilizado 🚀"
    )

    st.info(
        "Próxima fase:\n"
        "- Firebase Auth real\n"
        "- Pagamentos Mercado Pago\n"
        "- Multiusuários\n"
        "- Automação SaaS"
    )
