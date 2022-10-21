import streamlit as st
from modules.database import Users, AddUsers
from modules.settings import user
from modules.levels import Levels

st.set_page_config(
    page_title='Проекты',
    page_icon=':chart_with_upwards_trend:',
    layout='wide'
)
st.markdown("# Сотрудники")

try:
    user_func = user()
    user = user_func['user']
    st.sidebar.markdown(f'### {user.name}')
    st.sidebar.markdown(f'##### {user.group}')
    user_func['form'].logout('Выйти', 'sidebar')
    if user.status:
        tab1, tab2 = st.tabs([
            'Данные пользователей',
            'Добавление пользователя'
        ])
        with tab1:
            match user.level:
                case Levels.leader | Levels.admin:
                    to_change_user = st.checkbox('Изменить данные', key='user')
                case _:
                    to_change_user = False
            users = Users(to_change_user, user)
            users.show_user_data()
            users.send_changes()
        with tab2:
            match user.level:
                case Levels.leader | Levels.admin:
                    add_users = AddUsers()
                    add_users.form()
                case _:
                    st.warning('Недостаточно прав')
    else:
        st.info('Необходимо авторизоваться')
except AttributeError:
    pass
