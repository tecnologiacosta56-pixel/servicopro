import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import mercadopago

# ==============================
# 🔐 FIREBASE (SEGURO)
# ==============================

if not firebase_admin._apps:
    firebase_dict = dict(st.secrets["firebase"])
    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ==============================
# 💳 MERCADO PAGO
# ==============================

st.write(st.secrets)
st.write("TOKEN:", st.secrets.get("MP_ACCESS_TOKEN"))
# ==============================
# 🎯 FUNÇÃO DE PAGAMENTO
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

        print("RESPOSTA MP:", response)

        if "response" in response:
            return response["response"].get("init_point")
        else:
            return None

    except Exception as e:
        print("ERRO MP:", e)
        return None

# ==============================
# 👤 USUÁRIO (SIMULAÇÃO)
# ==============================

uid = "user_123"
email = "cliente@email.com"

# ==============================
# 🎨 INTERFACE + ESTILO
# ==============================

st.set_page_config(page_title="ServiçoPro", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

button {
    background: linear-gradient(90deg, #06b6d4, #22c55e);
    color: white !important;
    border-radius: 10px;
    border: none;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 ServiçoPro SaaS")
st.write("Sistema inteligente com clientes, ordens e pagamentos")

# ==============================
# 📊 CONSULTA PLANO
# ==============================

user_ref = db.collection("usuarios").document(uid)
user = user_ref.get()

if user.exists:
    plano = user.to_dict().get("plano", "free")
else:
    plano = "free"
    user_ref.set({"plano": "free"})

st.write(f"Plano atual: **{plano}**")

# ==============================
# 💳 BOTÃO DE PAGAMENTO
# ==============================

if plano == "free":
    if st.button("🚀 Fazer Upgrade para PRO"):
        link = criar_pagamento(uid, email)

        if link:
            st.success("Pagamento gerado com sucesso!")
            st.markdown(f"[👉 Clique aqui para pagar]({link})")
        else:
            st.error("Erro ao gerar pagamento. Verifique o token do Mercado Pago.")

else:
    st.success("Você já é PRO 🎉")
