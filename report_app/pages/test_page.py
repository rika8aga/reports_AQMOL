import streamlit as st
from report_app.export import ReportFormHead, ReportFormBody
from report_app.settings import user


st.set_page_config(
    page_title='Форма отчета',
    page_icon=':page_facing_up:',
    layout='wide'
)
style = '''
    <style>
        header {visibility: visible;}
        footer {visibility: hidden;}
    </style>
'''
st.markdown("# Форма отчета")
st.markdown(style, unsafe_allow_html=True)

try:
    user_func = user()
    user = user_func['user']
    st.sidebar.markdown(f'### {user.name}')
    st.sidebar.markdown(f'##### {user.group}')
    user_func['form'].logout('Выйти', 'sidebar')
except AttributeError:
    st.stop()
if user.status:
    form_head = ReportFormHead(user)
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
