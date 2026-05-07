# ==============================
# LOGIN SCREEN
# ==============================

if st.session_state["authenticated"] == False:

    st.title("🔐 Login ServiçoPro SaaS")

    email = st.text_input("Email")

    password = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        sucesso = login(email, password)

        if sucesso:

            st.session_state["authenticated"] = True

            st.success(
                "Login realizado com sucesso!"
            )

            st.rerun()

        else:

            st.error(
                "Credenciais inválidas"
            )

    st.stop()
