import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import mercadopago
import pandas as pd

# ==============================
# CONFIG
# ==============================

st.set_page_config(
    page_title="ServiçoPro SaaS",
    layout="wide",
    page_icon="🚀"
)

# ==============================
# FIREBASE INIT (BLINDADO)
# ==============================

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

# ==============================
# MERCADO PAGO
# ==============================

sdk = mercadopago.SDK(
    st.secrets["mercadopago"]["MP_ACCESS_TOKEN"]
)

# ==============================
# SESSION STATE PADRÃO
# ==============================

defaults = {
    "authenticated": False,
    "uid": None,
    "empresa_id": None,
    "role": None
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==============================
# LOGIN
# ==============================

def login(email, password):

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
        st.session_state["empresa_id"] = data["empresa_id"]
        st.session_state["role"] = data.get("role", "member")
        st.session_state["authenticated"] = True

        return True

    return False

# ==============================
# LOGOUT
# ==============================

def logout():

    for k in list(st.session_state.keys()):
        del st.session_state[k]

    st.rerun()

# ==============================
# LOGIN SCREEN
# ==============================

if not st.session_state["authenticated"]:

    st.title("🔐 Login ServiçoPro SaaS")

    email = st.text_input("Email")

    password = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        sucesso = login(email, password)

        if sucesso:

            st.session_state["authenticated"] = True

            st.success(
                "Login realizado com sucesso!"
            )

        else:

            st.error(
                "Credenciais inválidas"
            )

    st.stop()

# ==============================
# CONTEXTO MULTIEMPRESA
# ==============================

empresa_id = st.session_state["empresa_id"]

empresa_ref = db.collection("empresas").document(
    empresa_id
)

clientes_ref = empresa_ref.collection("clientes")

servicos_ref = empresa_ref.collection("servicos")

# ==============================
# SIDEBAR
# ==============================

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

# ==============================
# DASHBOARD
# ==============================

if menu == "📊 Dashboard":

    st.title("📊 Dashboard SaaS")

    clientes = list(clientes_ref.stream())

    servicos = list(servicos_ref.stream())

    col1, col2, col3 = st.columns(3)

    col1.metric("Empresa ID", empresa_id)

    col2.metric("Clientes", len(clientes))

    col3.metric("Serviços", len(servicos))

    st.bar_chart(
        pd.DataFrame({
            "Categoria": [
                "Clientes",
                "Serviços"
            ],
            "Total": [
                len(clientes),
                len(servicos)
            ]
        }).set_index("Categoria")
    )

# ==============================
# CLIENTES
# ==============================

elif menu == "👤 Clientes":

    st.title("👤 Clientes")

    nome = st.text_input("Novo cliente")

    if st.button("➕ Adicionar Cliente"):

        if nome:

            clientes_ref.add({
                "nome": nome
            })

            st.success("Cliente adicionado!")

    for c in clientes_ref.stream():

        data = c.to_dict()

        col1, col2, col3 = st.columns([7, 1, 1])

        with col1:
            st.markdown(f"👤 {data['nome']}")

        # EDITAR
        if st.session_state.get(f"edit_c_{c.id}"):

            novo_nome = st.text_input(
                "Editar nome",
                value=data["nome"],
                key=f"inp_c_{c.id}"
            )

            colA, colB = st.columns(2)

            with colA:

                if st.button(
                    "💾 Salvar",
                    key=f"save_c_{c.id}"
                ):

                    clientes_ref.document(c.id).update({
                        "nome": novo_nome
                    })

                    st.session_state[
                        f"edit_c_{c.id}"
                    ] = False

                    st.rerun()

            with colB:

                if st.button(
                    "❌ Cancelar",
                    key=f"cancel_c_{c.id}"
                ):

                    st.session_state[
                        f"edit_c_{c.id}"
                    ] = False

                    st.rerun()

        else:

            if st.button(
                "✏️ Editar",
                key=f"edit_btn_c_{c.id}"
            ):

                st.session_state[
                    f"edit_c_{c.id}"
                ] = True

                st.rerun()

        # EXCLUIR
        if st.session_state.get(f"del_c_{c.id}"):

            st.warning(
                f"Excluir {data['nome']}?"
            )

            colA, colB = st.columns(2)

            with colA:

                if st.button(
                    "❌ Cancelar",
                    key=f"cancel_del_c_{c.id}"
                ):

                    st.session_state[
                        f"del_c_{c.id}"
                    ] = False

                    st.rerun()

            with colB:

                if st.button(
                    "🗑 Confirmar",
                    key=f"confirm_del_c_{c.id}"
                ):

                    clientes_ref.document(
                        c.id
                    ).delete()

                    st.session_state[
                        f"del_c_{c.id}"
                    ] = False

                    st.rerun()

        else:

            if st.button(
                "🗑 Excluir",
                key=f"del_btn_c_{c.id}"
            ):

                st.session_state[
                    f"del_c_{c.id}"
                ] = True

                st.rerun()

# ==============================
# SERVIÇOS
# ==============================

elif menu == "🛠 Serviços":

    st.title("🛠 Serviços")

    cliente = st.text_input("Cliente")

    servico = st.text_input("Serviço")

    if st.button("➕ Salvar Serviço"):

        if cliente and servico:

            servicos_ref.add({
                "cliente": cliente,
                "servico": servico
            })

            st.success("Serviço salvo!")

    for s in servicos_ref.stream():

        data = s.to_dict()

        col1, col2, col3 = st.columns([7, 1, 1])

        with col1:
            st.markdown(
                f"🛠 {data['cliente']} - {data['servico']}"
            )

        # EDITAR
        if st.session_state.get(f"edit_s_{s.id}"):

            novo_servico = st.text_input(
                "Editar serviço",
                value=data["servico"],
                key=f"inp_s_{s.id}"
            )

            colA, colB = st.columns(2)

            with colA:

                if st.button(
                    "💾 Salvar",
                    key=f"save_s_{s.id}"
                ):

                    servicos_ref.document(s.id).update({
                        "servico": novo_servico
                    })

                    st.session_state[
                        f"edit_s_{s.id}"
                    ] = False

                    st.rerun()

            with colB:

                if st.button(
                    "❌ Cancelar",
                    key=f"cancel_s_{s.id}"
                ):

                    st.session_state[
                        f"edit_s_{s.id}"
                    ] = False

                    st.rerun()

        else:

            if st.button(
                "✏️ Editar",
                key=f"edit_btn_s_{s.id}"
            ):

                st.session_state[
                    f"edit_s_{s.id}"
                ] = True

                st.rerun()

        # EXCLUIR
        if st.session_state.get(f"del_s_{s.id}"):

            st.warning("Excluir serviço?")

            colA, colB = st.columns(2)

            with colA:

                if st.button(
                    "❌ Cancelar",
                    key=f"cancel_del_s_{s.id}"
                ):

                    st.session_state[
                        f"del_s_{s.id}"
                    ] = False

                    st.rerun()

            with colB:

                if st.button(
                    "🗑 Confirmar",
                    key=f"confirm_del_s_{s.id}"
                ):

                    servicos_ref.document(
                        s.id
                    ).delete()

                    st.session_state[
                        f"del_s_{s.id}"
                    ] = False

                    st.rerun()

        else:

            if st.button(
                "🗑 Excluir",
                key=f"del_btn_s_{s.id}"
            ):

                st.session_state[
                    f"del_s_{s.id}"
                ] = True

                st.rerun()

# ==============================
# PLANO
# ==============================

elif menu == "💳 Plano":

    st.title("💳 Plano SaaS")

    st.info(
        "Sistema estabilizado + pronto para Firebase Auth real + escala multiempresa 🚀"
    )
