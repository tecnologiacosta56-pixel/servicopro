import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
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

# ==================================================
# FIRESTORE
# ==================================================

db = firestore.client()

# ==================================================
# SESSION STATE
# ==================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "empresa_id" not in st.session_state:
    st.session_state.empresa_id = None

if "uid" not in st.session_state:
    st.session_state.uid = None

if "role" not in st.session_state:
    st.session_state.role = None

# ==================================================
# LOGIN
# ==================================================

def login():

    try:

        doc_ref = db.collection(
            "usuarios"
        ).document(
            "user123"
        )

        doc = doc_ref.get()

        if not doc.exists:

            return False

        usuario = doc.to_dict()

        st.session_state.authenticated = True

        st.session_state.uid = doc.id

        st.session_state.empresa_id = usuario.get(
            "empresa_id"
        )

        st.session_state.role = usuario.get(
            "role",
            "member"
        )

        return True

    except Exception as e:

        st.error(
            f"Erro login: {e}"
        )

        return False

# ==================================================
# LOGOUT
# ==================================================

def logout():

    st.session_state.authenticated = False

    st.session_state.empresa_id = None

    st.session_state.uid = None

    st.session_state.role = None

    st.rerun()

# ==================================================
# LOGIN SCREEN
# ==================================================

if not st.session_state.authenticated:

    st.title("🔐 ServiçoPro SaaS")

    st.write(
        "Clique abaixo para acessar."
    )

    if st.button("Entrar"):

        sucesso = login()

        if sucesso:

            st.success(
                "Login realizado com sucesso!"
            )

            st.rerun()

        else:

            st.error(
                "Usuário não encontrado."
            )

    st.stop()

# ==================================================
# EMPRESA
# ==================================================

empresa_id = st.session_state.empresa_id

if not empresa_id:

    st.error(
        "Empresa inválida."
    )

    st.stop()

# ==================================================
# REFERÊNCIAS FIRESTORE
# ==================================================

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
    f"Perfil: {st.session_state.role}"
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

    clientes = clientes_ref.get()

    servicos = servicos_ref.get()

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

    telefone = st.text_input(
        "Telefone"
    )

    endereco = st.text_input(
        "Endereço"
    )

    if st.button(
        "➕ Adicionar Cliente"
    ):

        if nome:

            clientes_ref.add({

                "nome": nome,
                "telefone": telefone,
                "endereco": endereco

            })

            st.success(
                "Cliente adicionado!"
            )

            st.rerun()

    st.divider()

    clientes = clientes_ref.get()

    for c in clientes:

        data = c.to_dict()

        col1, col2 = st.columns([8, 2])

        with col1:

            st.write(
                f"""
👤 {data.get('nome', '')}

📞 {data.get('telefone', '')}

📍 {data.get('endereco', '')}
"""
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

    valor = st.text_input(
        "Valor"
    )

    status = st.selectbox(
        "Status",
        [
            "pendente",
            "em andamento",
            "concluido"
        ]
    )

    if st.button(
        "➕ Salvar Serviço"
    ):

        if cliente and servico:

            servicos_ref.add({

                "cliente": cliente,
                "servico": servico,
                "valor": valor,
                "status": status

            })

            st.success(
                "Serviço salvo!"
            )

            st.rerun()

    st.divider()

    servicos = servicos_ref.get()

    for s in servicos:

        data = s.to_dict()

        col1, col2 = st.columns([8, 2])

        with col1:

            st.write(
                f"""
🛠 {data.get('cliente', '')}

🔧 {data.get('servico', '')}

💰 R$ {data.get('valor', '')}

📌 {data.get('status', '')}
"""
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
        """
Próximas fases:

✅ Firebase Auth real
✅ Mercado Pago recorrente
✅ Multiusuários
✅ Painel Admin
✅ Multiempresa SaaS
✅ Automação inteligente
"""
    )
