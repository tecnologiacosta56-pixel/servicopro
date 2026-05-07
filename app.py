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
# USUÁRIO
# ==============================

uid = "user_123"
email = "cliente@email.com"

user_ref = db.collection("usuarios").document(uid)
if not user_ref.get().exists:
    user_ref.set({"plano": "free", "email": email})

plano = user_ref.get().to_dict()["plano"]

# ==============================
# ESTILO VISUAL PREMIUM
# ==============================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
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
    transition: 0.3s;
}

div.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 15px #22c55e;
}

/* CARD */
.card {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 10px;
}

.logo {
    font-size: 28px;
    font-weight: bold;
    color: #22c55e;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# LOGO
# ==============================

st.markdown("<div class='logo'>🚀 ServiçoPro SaaS</div>", unsafe_allow_html=True)
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
# DASHBOARD (COM GRÁFICO)
# ==============================

if menu == "📊 Dashboard":
    st.title("📊 Dashboard")

    clientes = list(db.collection("clientes").stream())
    servicos = list(db.collection("servicos").stream())

    col1, col2, col3 = st.columns(3)

    col1.metric("Plano", plano.upper())
    col2.metric("Clientes", len(clientes))
    col3.metric("Serviços", len(servicos))

    # GRÁFICO SIMPLES
    st.subheader("📈 Atividade do Sistema")

    df = pd.DataFrame({
        "Categoria": ["Clientes", "Serviços"],
        "Total": [len(clientes), len(servicos)]
    })

    st.bar_chart(df.set_index("Categoria"))

# ==============================
# CLIENTES
# ==============================

elif menu == "👤 Clientes":
    st.title("👤 Clientes")

    nome = st.text_input("Novo cliente")

    if st.button("➕ Adicionar Cliente"):
        db.collection("clientes").add({"nome": nome})
        st.success("Cliente adicionado!")

    st.markdown("### Lista de Clientes")

    for c in db.collection("clientes").stream():
        data = c.to_dict()

        col1, col2 = st.columns([8, 2])

        with col1:
            st.markdown(f"<div class='card'>👤 {data['nome']}</div>", unsafe_allow_html=True)

        with col2:
            if st.button("🗑", key=c.id):
                db.collection("clientes").document(c.id).delete()
                st.rerun()

# ==============================
# SERVIÇOS
# ==============================

elif menu == "🛠 Serviços":
    st.title("🛠 Serviços")

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

        col1, col2 = st.columns([8, 2])

        with col1:
            st.markdown(
                f"<div class='card'>🛠 {data['cliente']} - {data['servico']}</div>",
                unsafe_allow_html=True
            )

        with col2:
            if st.button("🗑", key=s.id):
                db.collection("servicos").document(s.id).delete()
                st.rerun()

# ==============================
# PLANO (BOTÃO BONITO)
# ==============================

elif menu == "💳 Plano":
    st.title("💳 Plano")

    st.write(f"Plano atual: **{plano.upper()}**")

    if plano == "free":
        if st.button("🚀 Fazer Upgrade PRO"):
            link = criar_pagamento(uid, email)

            if link:
                st.success("Pagamento gerado!")

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
                    ">
                    💳 Ir para Pagamento
                    </button>
                </a>
                """, unsafe_allow_html=True)

            else:
                st.error("Erro ao gerar pagamento.")
    else:
        st.success("Você já é PRO 🎉")
