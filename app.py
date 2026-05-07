import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import mercadopago

# =========================================

# 🚀 CONFIGURAÇÃO DA PÁGINA

# =========================================

st.set_page_config(
page_title="ServiçoPro SaaS",
layout="wide"
)

# =========================================

# 🔐 FIREBASE

# =========================================

if not firebase_admin._apps:

```
firebase_dict = {
    "type": st.secrets["firebase"]["type"],
    "project_id": st.secrets["firebase"]["project_id"],
    "private_key_id": st.secrets["firebase"]["private_key_id"],
    "private_key": st.secrets["firebase"]["private_key"],
    "client_email": st.secrets["firebase"]["client_email"],
    "client_id": st.secrets["firebase"]["client_id"],
    "auth_uri": st.secrets["firebase"]["auth_uri"],
    "token_uri": st.secrets["firebase"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
    "universe_domain": st.secrets["firebase"]["universe_domain"]
}

cred = credentials.Certificate(firebase_dict)
firebase_admin.initialize_app(cred)
```

db = firestore.client()

# =========================================

# 💳 MERCADO PAGO

# =========================================

MP_ACCESS_TOKEN = st.secrets["MP_ACCESS_TOKEN"]

sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# =========================================

# 🎨 ESTILO VISUAL

# =========================================

st.markdown("""

<style>

.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

h1, h2, h3, p, div {
    color: white;
}

button {
    background: linear-gradient(90deg, #06b6d4, #22c55e);
    color: white !important;
    border-radius: 12px;
    border: none;
    padding: 12px;
    font-weight: bold;
    transition: 0.3s;
}

button:hover {
    transform: scale(1.02);
}

</style>

""", unsafe_allow_html=True)

# =========================================

# 🚀 TÍTULO

# =========================================

st.title("🚀 ServiçoPro SaaS")

st.write("Sistema inteligente com clientes, ordens e pagamentos")

# =========================================

# 👤 USUÁRIO TESTE

# =========================================

uid = "user_123"

email = "[cliente@email.com](mailto:cliente@email.com)"

# =========================================

# 📊 CONSULTA PLANO

# =========================================

user_ref = db.collection("usuarios").document(uid)

user = user_ref.get()

if user.exists:

```
plano = user.to_dict().get("plano", "free")
```

else:

```
plano = "free"

user_ref.set({
    "plano": "free"
})
```

# =========================================

# 📈 DASHBOARD

# =========================================

col1, col2, col3 = st.columns(3)

with col1:
st.metric("Clientes", "12")

with col2:
st.metric("Ordens", "27")

with col3:
st.metric("Plano", plano.upper())

st.divider()

# =========================================

# 💳 FUNÇÃO PAGAMENTO

# =========================================

def criar_pagamento(uid, email):

```
preference_data = {

    "items": [
        {
            "title": "Plano PRO ServiçoPro",
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

        return response["response"]["init_point"]

    return None

except Exception as e:

    st.error(f"Erro Mercado Pago: {e}")

    return None
```

# =========================================

# 💎 ÁREA PRO

# =========================================

if plano == "free":

```
st.warning("Seu plano atual é FREE")

if st.button("🚀 Fazer Upgrade para PRO"):

    link = criar_pagamento(uid, email)

    if link:

        st.success("Pagamento gerado com sucesso!")

        st.markdown(f"""
        ### ✅ Link de Pagamento
        
        [👉 Clique aqui para pagar]({link})
        """)

    else:

        st.error("Erro ao gerar pagamento.")
```

else:

```
st.success("🎉 Você já possui plano PRO")
```

# =========================================

# 📋 LISTA DE ORDENS

# =========================================

st.subheader("📋 Últimas Ordens")

ordens = [
{"cliente": "Carlos", "servico": "Instalação Elétrica"},
{"cliente": "Ana", "servico": "Automação Residencial"},
{"cliente": "João", "servico": "Rede Estruturada"}
]

for ordem in ordens:

```
st.container(border=True)

st.write(f"👤 Cliente: {ordem['cliente']}")
st.write(f"🛠 Serviço: {ordem['servico']}")

st.divider()
```

# =========================================

# ✅ RODAPÉ

# =========================================

st.caption("ServiçoPro SaaS © 2026")
