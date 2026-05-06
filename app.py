import streamlit as st
import mercadopago
import firebase_admin
from firebase_admin import credentials, firestore
import json

# =========================
# ⚙️ CONFIG PÁGINA
# =========================
st.set_page_config(
    page_title="ServiçoPro",
    page_icon="⚡",
    layout="wide"
)

# =========================
# 🎨 ESTILO VISUAL PREMIUM
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a, #020617);
    color: white;
}

.big-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #22c55e, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    font-size: 18px;
    color: #cbd5f5;
}

.card {
    background: rgba(2,6,23,0.8);
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 0px 20px rgba(34,197,94,0.2);
}

.stButton>button {
    background: linear-gradient(90deg, #22c55e, #06b6d4);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🔐 FIREBASE (SECRETS)
# =========================
if not firebase_admin._apps:
    firebase_config = json.loads(st.secrets["firebase_config"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================
# 💳 MERCADO PAGO
# =========================
sdk = mercadopago.SDK(st.secrets["MP_ACCESS_TOKEN"])

# =========================
# 💰 FUNÇÃO PAGAMENTO
# =========================
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
        "external_reference": uid,
        "back_urls": {
            "success": "https://seusite.com/sucesso",
            "failure": "https://seusite.com/erro",
            "pending": "https://seusite.com/pendente"
        },
        "auto_return": "approved"
    }

    response = sdk.preference().create(preference_data)
    return response["response"]["init_point"]

# =========================
# 👤 USUÁRIO (SIMULAÇÃO)
# =========================
uid = "user123"
email = "user@email.com"

user_ref = db.collection("users").document(uid)
user_data = user_ref.get().to_dict()

if not user_data:
    user_ref.set({
        "email": email,
        "plano": "free",
        "status": "pendente"
    })
    user_data = {"plano": "free"}

# =========================
# 🚀 INTERFACE PRINCIPAL
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown('<div class="big-title">Automatize seu negócio</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Sistema inteligente com automação e pagamentos integrados</div>', unsafe_allow_html=True)

st.write("")
st.write(f"Plano atual: **{user_data['plano']}**")

# =========================
# 💳 BOTÃO DE PAGAMENTO
# =========================
if user_data["plano"] == "free":
    if st.button("🚀 Fazer Upgrade para PRO"):
        link = criar_pagamento(uid, email)
        st.markdown(f"[👉 Ir para pagamento]({link})")
else:
    st.success("🔥 Você já é PRO")

st.markdown('</div>', unsafe_allow_html=True)
