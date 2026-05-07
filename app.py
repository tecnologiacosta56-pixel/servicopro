import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import mercadopago

# ==============================
# CONFIG
# ==============================

st.set_page_config(
    page_title="ServiçoPro SaaS",
    layout="wide"
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
# USUÁRIO (SIMULAÇÃO)
# ==============================

uid = "user_123"
email = "cliente@email.com"

# cria usuário se não existir
user_ref = db.collection("usuarios").document(uid)
user_doc = user_ref.get()

if not user_doc.exists:
    user_ref.set({
        "plano": "free",
        "email": email
    })

plano = user_ref.get().to_dict().get("plano")

# ==============================
# MENU LATERAL (DASHBOARD REAL)
# ==============================

menu = st.sidebar.selectbox(
    "📌 Menu ServiçoPro",
    [
        "📊 Dashboard",
        "👤 Clientes",
        "🛠 Serviços",
        "💳 Assinatura"
    ]
)

# ==============================
# FUNÇÃO PAGAMENTO
# ==============================

def criar_pagamento(uid, email):
    preference_data = {
        "items": [
            {
                "title": "Plano Pro ServiçoPro",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 49.90
            }
        ],
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
    st.title("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Plano Atual", plano.upper())
    col2.metric("Clientes", "0")
    col3.metric("Serviços", "0")

    st.info("Painel SaaS ativo e conectado ao Firebase.")

# ==============================
# CLIENTES
# ==============================

elif menu == "👤 Clientes":
    st.title("👤 Clientes")

    st.write("Lista de clientes (Firestore)")

    clientes = db.collection("clientes").stream()

    for c in clientes:
        st.write(c.to_dict())

# ==============================
# SERVIÇOS
# ==============================

elif menu == "🛠 Serviços":
    st.title("🛠 Serviços")

    st.write("Cadastro de ordens")

    cliente = st.text_input("Cliente")
    servico = st.text_input("Serviço")

    if st.button("Salvar serviço"):
        db.collection("servicos").add({
            "cliente": cliente,
            "servico": servico
        })
        st.success("Serviço salvo!")

# ==============================
# ASSINATURA
# ==============================

elif menu == "💳 Assinatura":
    st.title("💳 Plano")

    st.write(f"Plano atual: **{plano.upper()}**")

    if plano == "free":
        if st.button("🚀 Upgrade PRO"):
            link = criar_pagamento(uid, email)

            if link:
                st.success("Pagamento gerado!")
                st.markdown(f"[Pagar agora]({link})")
            else:
                st.error("Erro ao gerar pagamento.")
    else:
        st.success("Você já é PRO 🎉")
