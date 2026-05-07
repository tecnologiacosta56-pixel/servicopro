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
# USUÁRIO
# ==============================

uid = "user_123"
email = "cliente@email.com"

user_ref = db.collection("usuarios").document(uid)
if not user_ref.get().exists:
    user_ref.set({"plano": "free", "email": email})

plano = user_ref.get().to_dict()["plano"]

# ==============================
# ESTILO VISUAL PREMIUM (EVOLUÍDO)
# ==============================

st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: white;
}

/* LOGO */
.logo {
    font-size: 30px;
    font-weight: 800;
    color: #22c55e;
    margin-bottom: 5px;
}

/* CARDS */
.card {
    background: rgba(255,255,255,0.06);
    padding: 15px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 10px;
    transition: 0.3s;
}

.card:hover {
    transform: scale(1.01);
    border: 1px solid #22c55e;
}

/* BOTÕES */
div.stButton > button {
    background: linear-gradient(90deg, #06b6d4, #22c55e);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 16px;
    font-weight: 600;
    transition: 0.3s;
}

div.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 15px #22c55e;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# LOGO
# ==============================

from PIL import Image

st.sidebar.image("logo.png", use_container_width=True)
st.caption("Sistema inteligente de gestão, clientes e automação")

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
# DASHBOARD (EVOLUÍDO)
# ==============================

if menu == "📊 Dashboard":
    st.title("📊 Painel Inteligente")

    clientes = list(db.collection("clientes").stream())
    servicos = list(db.collection("servicos").stream())

    col1, col2, col3 = st.columns(3)

    col1.metric("Plano Atual", plano.upper())
    col2.metric("Clientes", len(clientes))
    col3.metric("Serviços", len(servicos))

    st.markdown("---")

    st.subheader("📈 Visão Geral do Sistema")

    df = pd.DataFrame({
        "Categoria": ["Clientes", "Serviços"],
        "Total": [len(clientes), len(servicos)]
    })

    st.bar_chart(df.set_index("Categoria"))

    st.markdown("---")

    st.subheader("⚡ Status do Sistema")

    st.success("Firebase conectado")
    st.success("Mercado Pago ativo")
    st.info("SaaS operacional")

# ==============================
# CLIENTES
# ==============================

# ==============================
# CLIENTES (CRUD PROFISSIONAL)
# ==============================

elif menu == "👤 Clientes":
    st.title("👤 Gestão de Clientes")

    nome = st.text_input("Novo cliente")

    if st.button("➕ Adicionar Cliente"):
        if nome:
            db.collection("clientes").add({"nome": nome})
            st.success("Cliente adicionado!")
        else:
            st.warning("Digite um nome.")

    st.markdown("### Lista de Clientes")

    for c in db.collection("clientes").stream():
        data = c.to_dict()

        col1, col2, col3 = st.columns([7, 1, 1])

        with col1:
            st.markdown(f"👤 **{data['nome']}**")

        # ================= EDITAR =================
        with col2:
            if st.button("✏️", key=f"edit_{c.id}"):
                novo_nome = st.text_input("Editar nome", value=data["nome"], key=f"input_{c.id}")

                if st.button("Salvar", key=f"save_{c.id}"):
                    db.collection("clientes").document(c.id).update({
                        "nome": novo_nome
                    })
                    st.success("Atualizado!")
                    st.rerun()

        # ================= EXCLUIR =================
        with col3:
            if st.button("🗑", key=f"del_{c.id}"):
                db.collection("clientes").document(c.id).delete()
                st.rerun()

# ==============================
# SERVIÇOS
# ==============================

elif menu == "🛠 Serviços":
    st.title("🛠 Gestão de Serviços")

    cliente = st.text_input("Cliente")
    servico = st.text_input("Serviço")

    if st.button("➕ Salvar Serviço"):
        db.collection("servicos").add({
            "cliente": cliente,
            "servico": servico
        })
        st.success("Serviço salvo!")

    st.markdown("### Lista de Serviços")

    for s in db.collection("servicos").stream():
        data = s.to_dict()

        col1, col2, col3 = st.columns([7, 1, 1])

        with col1:
            st.markdown(f"🛠 **{data['cliente']} - {data['servico']}**")

        with col2:
            if st.button("✏️", key=f"edit_s_{s.id}"):
                novo_servico = st.text_input(
                    "Editar serviço",
                    value=data["servico"],
                    key=f"input_s_{s.id}"
                )

                if st.button("Salvar S", key=f"save_s_{s.id}"):
                    db.collection("servicos").document(s.id).update({
                        "servico": novo_servico
                    })
                    st.success("Atualizado!")
                    st.rerun()

        with col3:
            if st.button("🗑", key=f"del_s_{s.id}"):
                db.collection("servicos").document(s.id).delete()
                st.rerun()
# ==============================
# PLANO (UPGRADE SAAS)
# ==============================

elif menu == "💳 Plano":
    st.title("💳 Planos")

    st.write(f"Plano atual: **{plano.upper()}**")

    if plano == "free":
        if st.button("🚀 Fazer Upgrade PRO"):
            link = criar_pagamento(uid, email)

            if link:
                st.success("Pagamento gerado com sucesso!")

                st.markdown(f"""
                <a href="{link}" target="_blank">
                    <button style="
                        background: linear-gradient(90deg, #06b6d4, #22c55e);
                        color: white;
                        padding: 12px;
                        border: none;
                        border-radius: 10px;
                        font-weight: bold;
                        cursor: pointer;
                        width: 100%;
                    ">
                    💳 Ir para Pagamento
                    </button>
                </a>
                """, unsafe_allow_html=True)

            else:
                st.error("Erro ao gerar pagamento.")
    else:
        st.success("Você já é PRO 🎉")
