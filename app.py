import streamlit as st

    st.markdown("<br>", unsafe_allow_html=True)

    for s in servicos:

        data = s.to_dict()

        col1, col2 = st.columns([8,1])

        with col1:
            st.markdown(f"""
            <div class='card'>
                🛠 {data.get('cliente')} - {data.get('servico')}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("🗑", key=s.id):
                servicos_ref.document(s.id).delete()
                st.rerun()

# ==================================================
# FINANCEIRO
# ==================================================

elif menu == "Financeiro":

    st.markdown("<div class='main-title'>Financeiro</div>", unsafe_allow_html=True)

    faturamento = total_servicos * 150

    st.markdown(f"""
    <div class='metric-card'>
        <h1>💰 R$ {faturamento}</h1>
        <p>Faturamento estimado</p>
    </div>
    """, unsafe_allow_html=True)

# ==================================================
# RELATÓRIOS
# ==================================================

elif menu == "Relatórios":

    st.markdown("<div class='main-title'>Relatórios</div>", unsafe_allow_html=True)

    dados = {
        "Clientes": total_clientes,
        "Serviços": total_servicos
    }

    st.json(dados)
