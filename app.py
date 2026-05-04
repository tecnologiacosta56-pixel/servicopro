import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# =========================
# FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate("servico-pro-firebase-adminsdk-fbsvc-02c8b2d43b.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================
# SESSION
# =========================
if "logged" not in st.session_state:
    st.session_state.logged = False

# =========================
# LOGIN
# =========================
if not st.session_state.logged:
    st.title("🔐 Sistema ServiçoPro")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        users = db.collection("users").stream()

        for u in users:
            data = u.to_dict()

            if (
                data.get("email", "").strip() == email.strip()
                and data.get("password", "").strip() == senha.strip()
            ):
                st.session_state.logged = True
                st.rerun()

        st.error("Login inválido")

    st.stop()

# =========================
# MENU
# =========================
pagina = st.sidebar.selectbox(
    "Navegação",
    ["Dashboard", "Clientes", "Serviços"]
)

if st.sidebar.button("Sair"):
    st.session_state.logged = False
    st.rerun()

# =========================
# DASHBOARD
# =========================
if pagina == "Dashboard":
    st.title("📊 Dashboard")

    total_clientes = len(list(db.collection("clientes").stream()))
    total_servicos = len(list(db.collection("servicos").stream()))

    col1, col2 = st.columns(2)

    col1.metric("Clientes", total_clientes)
    col2.metric("Serviços", total_servicos)

# =========================
# CLIENTES
# =========================
elif pagina == "Clientes":
    st.title("👤 Clientes")

    nome = st.text_input("Nome do cliente")
    servico = st.text_input("Serviço")

    if st.button("Salvar cliente"):
        if nome and servico:
            db.collection("clientes").add({
                "nome": nome,
                "servico": servico,
                "created_at": datetime.now()
            })
            st.success("Cliente salvo!")
            st.rerun()
        else:
            st.warning("Preencha todos os campos")

    st.divider()
    st.subheader("Lista de clientes")

    if "editando" not in st.session_state:
        st.session_state.editando = None

    clientes = db.collection("clientes").stream()

    for c in clientes:
        d = c.to_dict()
        cid = c.id

        col1, col2, col3 = st.columns([4,1,1])

        col1.write(f"👤 {d.get('nome')} - {d.get('servico')}")

        # EDITAR
        if col2.button("✏️", key=f"edit_{cid}"):
            st.session_state.editando = cid

        # EXCLUIR
        if col3.button("🗑️", key=f"del_{cid}"):
            st.session_state[f"confirm_{cid}"] = True

        # CONFIRMAÇÃO
        if st.session_state.get(f"confirm_{cid}"):
            st.warning("Tem certeza que deseja excluir?")

            c1, c2 = st.columns(2)

            if c1.button("Cancelar", key=f"cancel_{cid}"):
                st.session_state[f"confirm_{cid}"] = False

            if c2.button("Confirmar", key=f"ok_{cid}"):
                db.collection("clientes").document(cid).delete()
                st.success("Excluído!")
                st.rerun()

        # EDIÇÃO
        if st.session_state.editando == cid:
            novo_nome = st.text_input("Novo nome", value=d.get("nome"), key=f"n_{cid}")
            novo_servico = st.text_input("Novo serviço", value=d.get("servico"), key=f"s_{cid}")

            if st.button("Salvar", key=f"save_{cid}"):
                db.collection("clientes").document(cid).update({
                    "nome": novo_nome,
                    "servico": novo_servico,
                    "updated_at": datetime.now()
                })
                st.session_state.editando = None
                st.success("Atualizado!")
                st.rerun()

# =========================
# SERVIÇOS
# =========================
elif pagina == "Serviços":
    st.title("📋 Serviços")

    # carregar clientes
    clientes_ref = list(db.collection("clientes").stream())
    lista_clientes = {c.id: c.to_dict().get("nome") for c in clientes_ref}

    if not lista_clientes:
        st.warning("Cadastre um cliente primeiro!")
        st.stop()

    cliente_id = st.selectbox(
        "Selecionar cliente",
        options=list(lista_clientes.keys()),
        format_func=lambda x: lista_clientes[x]
    )

    descricao = st.text_area("Descrição")
    prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Urgente"])

    if st.button("Criar serviço"):
        if cliente_id and descricao:

            cliente_nome = lista_clientes.get(cliente_id)

            # evitar duplicado
            servicos_existentes = db.collection("servicos").stream()
            duplicado = False

            for s in servicos_existentes:
                d = s.to_dict()
                if d.get("cliente_id") == cliente_id and d.get("descricao") == descricao:
                    duplicado = True
                    break

            if duplicado:
                st.warning("Serviço já existe!")

            else:
                db.collection("servicos").add({
                    "cliente_id": cliente_id,
                    "cliente_nome": cliente_nome,
                    "descricao": descricao,
                    "status": "Aberto",
                    "prioridade": prioridade,
                    "created_at": datetime.now()
                })

                st.success("Serviço criado com sucesso!")
                st.rerun()

        else:
            st.warning("Preencha todos os campos")

    st.divider()

    servicos = db.collection("servicos").stream()

    for s in servicos:
        d = s.to_dict()

        st.write(
            f"👤 {d.get('cliente_nome')} | "
            f"📝 {d.get('descricao')} | "
            f"⚡ {d.get('prioridade')} | "
            f"🔄 {d.get('status')}"
        )