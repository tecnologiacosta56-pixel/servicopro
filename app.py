import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import mercadopago

# ==============================
# 🔐 CONFIGURAÇÃO GERAL
# ==============================

st.set_page_config(
    page_title="ServiçoPro SaaS",
    layout="wide"
)

# ==============================
# 🔥 FIREBASE INIT (SEGURO)
# ==============================

if not firebase_admin._apps:
    firebase_dict = dict(st.secrets["firebase"])
    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ==============================
# 💳 MERCADO PAGO INIT
# ==============================

sdk = mercadopago.SDK(
    st.secrets["mercadopago"]["MP_ACCESS_TOKEN"]
)

# ==============================
# 🎨 ESTILO VISUAL
# ==============================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

div.stButton > button {
    background: linear-gradient(90deg, #06b6d4, #22c55e);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 👤 USUÁRIO (SIMULAÇÃO)
# ==============================

uid = "user_123"
email = "cliente@email.com"

# ==============================
# 💳 CRIAR PAGAMENTO
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
        "payer": {
            "email": email
        },
        "external_reference": uid
    }

    try:
        response = sdk.preference().create(preference_data)

        if "response" in response:
            return response["response"].get("init_point")

        return None

    except Exception as e:
        st.error(f"Erro Mercado Pago: {e}")
        return None

# ==============================
# 🚀 INTERFACE
# ==============================

st.title("🚀 ServiçoPro SaaS")
st.write("Sistema inteligente com clientes, ordens e pagamentos")

# ==============================
# 📊 FIRESTORE - PLANO
# ==============================

user_ref = db.collection("usuarios").document(uid)
user = user_ref.get()

if user.exists:
    plano = user.to_dict().get("plano", "free")
else:
    plano = "free"
    user_ref.set({"plano": "free"})

st.write(f"Plano atual: **{plano.upper()}**")

# ==============================
# 💳 UPGRADE
# ==============================

if plano == "free":
    if st.button("🚀 Fazer Upgrade PRO"):
        link = criar_pagamento(uid, email)

        if link:
            st.success("Pagamento gerado com sucesso!")
            st.markdown(f"[👉 Clique aqui para pagar]({link})")
        else:
            st.error("Falha ao gerar pagamento.")

else:
    st.success("Você já é PRO 🎉 acesso liberado!")
