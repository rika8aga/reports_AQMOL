import streamlit as st
from modules.database import Projects, AddProject
from modules.settings import user
from modules.levels import Levels

st.set_page_config(
    page_title='Проекты',
    page_icon=':chart_with_upwards_trend:',
    layout='wide'
)
st.markdown("# Проекты")

try:
    user_func = user()
    user = user_func['user']
    st.sidebar.markdown(f'### {user.name}')
    st.sidebar.markdown(f'##### {user.group}')
    user_func['form'].logout('Выйти', 'sidebar')
    if user.status:
        tab1, tab2 = st.tabs([
            'Данные о проектах',
            'Добавление проекта'
        ])
        with tab1:
            match user.level:
                case Levels.leader | Levels.admin:
                    to_change = st.checkbox('Изменить данные', key='project')
                case _:
                    to_change = False
            projects = Projects(to_change)
            projects.project_selector()
            projects.show_data()
            projects.send_changes()
            with st.expander('Проекты'):
                st.dataframe(projects.dataframe, use_container_width=True)
        with tab2:
            match user.level:
                case Levels.leader | Levels.admin:
                    add_project = AddProject()
                    add_project.send_request()
                case _:
                    st.warning('Недостаточно прав')
    else:
        st.info('Необходимо авторизоваться')
except AttributeError:
    pass
