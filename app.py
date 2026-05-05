import streamlit as st
import mercadopago
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request
import threading

# =========================
# 🔥 FIREBASE INIT
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase.json")  # sua chave
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================
# 💳 MERCADO PAGO INIT
# =========================
sdk = mercadopago.SDK("SEU_ACCESS_TOKEN")

# =========================
# 🌐 FLASK WEBHOOK (rodando junto)
# =========================
app = Flask(__name__)

def atualizar_plano(uid, plano):
    db.collection("users").document(uid).update({
        "plano": plano,
        "status_pagamento": "ativo"
    })

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        payment_id = data["data"]["id"]

        payment = sdk.payment().get(payment_id)
        status = payment["response"]["status"]

        # você precisa ter salvo o uid no pagamento (ver melhoria abaixo)
        uid = payment["response"].get("external_reference")

        if status == "approved" and uid:
            atualizar_plano(uid, "pro")

        return "ok", 200

    except Exception as e:
        return str(e), 400

# roda Flask em paralelo com Streamlit
def run_flask():
    app.run(port=5000)

threading.Thread(target=run_flask, daemon=True).start()

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
        "external_reference": uid,  # 🔥 essencial para ligar pagamento ao usuário
        "back_urls": {
            "success": "https://seusistema.com/sucesso",
            "failure": "https://seusistema.com/erro",
            "pending": "https://seusistema.com/pendente"
        },
        "auto_return": "approved"
    }

    response = sdk.preference().create(preference_data)
    return response["response"]["init_point"]

# =========================
# 🖥 STREAMLIT UI
# =========================
st.title("💳 Assinatura ServiçoPro")

# simulação usuário logado
uid = "user123"
email = "user@email.com"

user_ref = db.collection("users").document(uid)
user_data = user_ref.get().to_dict()

if not user_data:
    user_ref.set({
        "email": email,
        "plano": "free",
        "status_pagamento": "pendente"
    })
    user_data = {"plano": "free"}

st.write(f"Plano atual: {user_data['plano']}")

if user_data["plano"] == "free":
    if st.button("🚀 Fazer Upgrade para PRO"):
        link = criar_pagamento(uid, email)
        st.markdown(f"[Clique aqui para pagar]({link})")
else:
    st.success("Você já é PRO 🔥")
