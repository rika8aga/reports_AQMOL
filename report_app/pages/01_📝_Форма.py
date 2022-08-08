import streamlit as st
from report_app.export import ReportFormHead, ReportFormBody
from report_app.settings import user
import asyncio


async def form():
    st.set_page_config(
        page_title='Форма отчета',
        page_icon=':page_facing_up:',
        layout='wide'
    )

    st.markdown("# Форма отчета")

    try:
        user_func = user()
        user_class = user_func['user']
        st.sidebar.markdown(f'### {user_class.name}')
        st.sidebar.markdown(f'##### {user_class.group}')
        user_func['form'].logout('Выйти', 'sidebar')
    except AttributeError:
        st.stop()
    if user_class.status:
        form_head = ReportFormHead(user_class)
        form_head.form()
        form_body = ReportFormBody(
            form_head.user,
            form_head.fields_number,
            form_head.user_jobs,
            form_head.projects
        )
        form_body.form(form_head.user_jobs)
    else:
        st.warning('Пожалуйста авторизуйтесь')


asyncio.run(form())
