import streamlit as st
import asyncio


async def main():
    st.set_page_config(
        page_title='Главная страница',
        page_icon=":space_invader:",
        layout='wide'
    )

    st.markdown(
        f'<h1 style="color:#1B4E2F;font-size:50px;font-family: Century Gothic">{"AQMOL-project"}</h1>',
        unsafe_allow_html=True
    )

    st.markdown('''
        ### Добро пожаловать на портал компании
        Для перехода на необходимую страницу воспользуйтесь панелью слева
    ''')

asyncio.run(main())
