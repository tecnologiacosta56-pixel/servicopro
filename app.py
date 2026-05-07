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
# FIREBASE
# ==============================

if not firebase_admin._apps:
    firebase_dict = dict(st.secrets["firebase"])
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
# EMPRESA ATIVA (FIXA AGORA)
# ==============================

empresa_id = "empresa_demo_001"

empresa_ref = db.collection("empresas").document(empresa_id)

clientes_ref = empresa_ref.collection("clientes")
servicos_ref = empresa_ref.collection("servicos")
usuarios_ref = empresa_ref.collection("usuarios")
plano_ref = empresa_ref.collection("plano")

# ==============================
# USUÁRIO (SIMPLIFICADO POR ENQUANTO)
# ==============================

uid = "user_123"
email = "cliente@email.com"

user_ref = usuarios_ref.document(uid)
if not user_ref.get().exists:
    user_ref.set({"plano": "free", "email": email})

plano = user_ref.get().to_dict().get("plano", "free")

# ==============================
# ESTILO
# ==============================

st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: white;
}

/* BOTÕES */
div.stButton > button {
    background: linear-gradient(90deg, #06b6d4, #22c55e);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 16px;
    font-weight: 600;
}

div.stButton > button:hover {
    transform: scale(1.05);
}

</style>
""", unsafe_allow_html=True)

# ==============================
# MENU
# ==============================

menu = st.sidebar.selectbox("📌 Menu", [
    "📊 Dashboard",
    "👤 Clientes",
    "🛠 Serviços",
    "💳 Plano"
])

# ==============================
# PAGAMENTO
# ==============================

def criar_pagamento(uid, email):
    preference_data = {
        "items": [{
            "title": "Plano Pro ServiçoPro",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": 49.90
        }],
        "payer": {"email": email},
        "external_reference": uid
    }

    try:
        response = sdk.preference().create(preference_data)
        return response["response"]["init_point"]
    except:
        return None

# ==============================
# DASHBOARD
# ==============================

if menu == "📊 Dashboard":
    st.title("📊 Painel Inteligente")

    clientes = list(clientes_ref.stream())
    servicos = list(servicos_ref.stream())

    col1, col2, col3 = st.columns(3)

    col1.metric("Plano", plano.upper())
    col2.metric("Clientes", len(clientes))
    col3.metric("Serviços", len(servicos))

    st.bar_chart(pd.DataFrame({
        "Categoria": ["Clientes", "Serviços"],
        "Total": [len(clientes), len(servicos)]
    }).set_index("Categoria"))

    st.success("Sistema SaaS ativo")

# ==============================
# CLIENTES
# ==============================

elif menu == "👤 Clientes":
    st.title("👤 Gestão de Clientes")

    nome = st.text_input("Novo cliente")

    if st.button("➕ Adicionar Cliente"):
        if nome:
            clientes_ref.add({"nome": nome})
            st.success("Cliente adicionado!")

    st.markdown("### Lista de Clientes")

    for c in clientes_ref.stream():
        data = c.to_dict()

        col1, col2 = st.columns([8, 2])

        with col1:
            st.markdown(f"👤 **{data['nome']}**")

        if st.session_state.get(f"edit_c_{c.id}"):

            novo_nome = st.text_input(
                "Editar nome",
                value=data["nome"],
                key=f"input_c_{c.id}"
            )

            colA, colB = st.columns(2)

            with colA:
                if st.button("💾 Salvar", key=f"save_c_{c.id}"):
                    clientes_ref.document(c.id).update({"nome": novo_nome})
                    st.session_state[f"edit_c_{c.id}"] = False
                    st.rerun()

            with colB:
                if st.button("❌ Cancelar", key=f"cancel_c_{c.id}"):
                    st.session_state[f"edit_c_{c.id}"] = False
                    st.rerun()

        else:
            if st.button("✏️ Editar", key=f"edit_btn_c_{c.id}"):
                st.session_state[f"edit_c_{c.id}"] = True
                st.rerun()

        if st.button("🗑 Excluir", key=f"del_c_{c.id}"):
            clientes_ref.document(c.id).delete()
            st.rerun()

# ==============================
# SERVIÇOS
# ==============================

elif menu == "🛠 Serviços":
    st.title("🛠 Gestão de Serviços")

    cliente = st.text_input("Cliente")
    servico = st.text_input("Serviço")

    if st.button("➕ Salvar Serviço"):
        if cliente and servico:
            servicos_ref.add({
                "cliente": cliente,
                "servico": servico
            })
            st.success("Serviço salvo!")

    st.markdown("### Lista de Serviços")

    for s in servicos_ref.stream():
        data = s.to_dict()

        col1, col2 = st.columns([8, 2])

        with col1:
            st.markdown(f"🛠 **{data['cliente']} - {data['servico']}**")

        if st.button("🗑 Excluir", key=f"del_s_{s.id}"):
            servicos_ref.document(s.id).delete()
            st.rerun()

# ==============================
# PLANO
# ==============================

elif menu == "💳 Plano":
    st.title("💳 Planos")

    st.write(f"Plano atual: **{plano.upper()}**")

    if plano == "free":
        if st.button("🚀 Fazer Upgrade PRO"):
            link = criar_pagamento(uid, email)

            if link:
                st.markdown(f"[Ir para pagamento]({link})")
            else:
                st.error("Erro ao gerar pagamento.")
    else:
        st.success("Você já é PRO 🎉")
