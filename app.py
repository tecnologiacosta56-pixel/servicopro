import streamlit as st
import mercadopago
import firebase_admin
from firebase_admin import credentials, firestore
import json

# =========================
# 🔥 FIREBASE INIT (SECRETS)
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
# 💰 CRIAR PAGAMENTO
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
        "payer": {
            "email": email
        },
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
# 🖥 STREAMLIT UI
# =========================
st.title("💳 ServiçoPro SaaS")

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

st.write("Plano atual:", user_data["plano"])

if user_data["plano"] == "free":
    if st.button("🚀 Fazer Upgrade PRO"):
        link = criar_pagamento(uid, email)
        st.markdown(f"[Pagar agora]({link})")
else:
    st.success("Você já é PRO 🔥")
