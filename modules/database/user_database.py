import pandas as pd
import sqlalchemy.orm
from sqlalchemy import select
from .sql_classes import UserSQL, engine, RoleSQL, GroupSQL
import streamlit as st
from sqlalchemy.orm import sessionmaker
from modules.levels import Levels
from PIL import Image


def create_session() -> sqlalchemy.orm.Session:
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    return session


@st.experimental_memo(show_spinner=False)
def load_users_data() -> pd.DataFrame:
    connection = engine.connect(close_with_result=True)
    stmt = select(
        UserSQL,
        RoleSQL.function,
        RoleSQL.level,
        GroupSQL.group_name,
        GroupSQL.code.label('group_code')
    ).join(UserSQL.role).join(UserSQL.group)
    dataframe = pd.read_sql(stmt, connection)
    return dataframe


@st.experimental_memo(show_spinner=False)
def get_roles() -> pd.DataFrame:
    connect = engine.connect(close_with_result=True)
    stmt = select(RoleSQL)
    roles = pd.read_sql(stmt, connect)
    return roles


@st.experimental_memo(show_spinner=False)
def get_groups() -> pd.DataFrame:
    connection = engine.connect(close_with_result=True)
    stmt = select(GroupSQL)
    groups = pd.read_sql(stmt, connection)
    return groups


class Users:
    def __init__(self, change_data: bool, external_user):
        self.image = None
        self.is_active = None
        self.salary = None
        self.password = None
        self.username = None
        self.name = None
        self.user_level = None
        self.user_group = None
        self.dataframe = load_users_data()
        self.user_id = None
        self.user_data = None
        self.user_role = None
        self.not_change_data = 1 - change_data
        self.external_user = external_user
        self.roles = get_roles()
        self.groups = get_groups()

    # def show_image(self):
    #     self.image = Image.open(self.user_data['image'].iloc[0])
    #     st.image(self.image)

    def show_name(self):
        self.name = st.selectbox(
            'ФИО:',
            options=self.dataframe['name'].sort_values().drop_duplicates()
        )
        self.user_data = self.dataframe[self.dataframe['name'] == self.name]
        self.user_id = int(self.user_data['id'].iloc[0])

    def show_activity(self):
        self.is_active = st.radio(
            'Действующий:',
            options=[True, False],
            format_func=lambda x: 'Да' if x else 'Нет',
            horizontal=True
        )

    def show_username(self):
        self.username = st.text_input(
            'Username:',
            value=self.user_data['username'].iloc[0],
            disabled=self.not_change_data
        )

    def show_password(self):
        if self.name == self.external_user.name:
            disabled = True
            value = self.user_data['password'].iloc[0]
        else:
            disabled = True
            value = '*********'
        self.password = st.text_input(
            'Password:',
            value=value,
            type='password',
            disabled=disabled
        )

    def show_user_role(self):
        if self.not_change_data:
            self.user_role = st.selectbox(
                'Должность:',
                options=self.user_data['function'],
                disabled=self.not_change_data
            )
        else:
            self.user_role = st.selectbox(
                'Должность:',
                options=self.roles['function'],
                index=int(self.roles[self.roles['function'] == self.user_data['function'].iloc[0]].index[0])
            )

    def show_user_group(self):
        if self.not_change_data:
            self.user_group = st.selectbox(
                'Отдел:',
                options=self.user_data['group_name'],
                disabled=self.not_change_data
            )
        else:
            self.user_group = st.selectbox(
                'Отдел:',
                options=self.groups['group_name'].drop_duplicates(),
                index=int(self.groups[self.groups['group_name'] == self.user_data['group_name'].iloc[0]].index[0])
            )

    def show_user_level(self):
        if self.not_change_data:
            self.user_level = st.selectbox(
                'Уровень доступа:',
                options=self.user_data['level'],
                disabled=self.not_change_data
            )
        else:
            self.user_level = st.selectbox(
                'Уровень доступа:',
                options=['СО', 'НО', 'АДМ'],
                index=[i for i, j in enumerate(['СО', 'НО', 'АДМ']) if j == self.user_data['level'].iloc[0]][0]
            )

    def show_salary(self):
        self.salary = st.number_input(
            'Оклад:',
            value=self.user_data['salary'].iloc[0],
            disabled=self.not_change_data
        )

    def show_user_data(self):
        self.show_name()
        self.show_activity()
        col1, col2 = st.columns(2)
        with col1:
            self.show_username()
        with col2:
            self.show_password()
        self.show_user_role()
        self.show_user_group()
        match self.external_user.level:
            case Levels.admin:
                col1, col2 = st.columns(2)
                with col1:
                    self.show_user_level()
                with col2:
                    self.show_salary()
                with st.expander('Таблица 1 ПОльзователи'):
                    st.dataframe(self.dataframe, use_container_width=True)

    def change_image(self):
        image = st.file_uploader(
            label='Выберите фото',
            type=['png', 'jpg']
        )

    def change_data(self, user: UserSQL):
        if self.username != self.user_data['username'].iloc[0]:
            user.username = self.username
        if self.password != self.user_data['password'].iloc[0] and self.password != '*********':
            user.password = self.password
        if self.salary != self.user_data['salary'].iloc[0]:
            user.salary = self.salary
        if self.is_active != self.user_data['is_active'].iloc[0]:
            user.is_active = self.is_active

    def change_role(self, session: sqlalchemy.orm.Session, user):
        role = session.query(RoleSQL).filter_by(
            function=self.user_role,
            level=self.user_level
        ).scalar()
        if not role:
            role = RoleSQL(function=self.user_role, level=self.user_level)
            session.add(role)
        user.role = []
        user.role.append(role)

    def change_group(self, session: sqlalchemy.orm.Session, user: UserSQL):
        group = session.query(GroupSQL).filter_by(group_name=self.user_group).scalar()
        user.group = []
        user.group.append(group)

    def send_changes(self):
        if not self.not_change_data:
            subbmit = st.button(
                'Отправить изменения'
            )
            if subbmit:
                session = create_session()
                user = session.query(UserSQL).filter_by(
                    id=self.user_id
                ).scalar()
                self.change_data(user)
                self.change_role(session, user)
                self.change_group(session, user)
                session.commit()
                session.close()
                st.experimental_memo.clear()
                st.experimental_rerun()


class AddUsers:
    def __init__(self):
        self.button = False
        self.code = None
        self.username = None
        self.name = None
        self.password = None
        self.salary = None
        self.user_group = None
        self.user_role = None
        self.user_level = None
        self.roles = get_roles()
        self.groups = get_groups()
        self.users = load_users_data()

    def show_name(self):
        self.name = st.text_input(
            'Ф.И.О'
        )

    def show_username(self):
        self.username = st.text_input(
            'Username'
        )

    def show_password(self):
        self.password = st.text_input(
            'Password',
            type='password'
        )

    def show_group(self):
        self.user_group = st.selectbox(
            'Отдел',
            options=self.groups['group_name']
        )

    def show_role(self):
        self.user_role = st.selectbox(
            'Должность',
            options=self.roles['function']
        )

    def show_level(self):
        self.user_level = st.selectbox(
            'Уровень доступа:',
            options=['СО', 'НО', 'АДМ']
        )

    def show_salary(self):
        self.salary = st.number_input(
            'Оклад',
            step=1
        )

    def get_user_code(self):
        in_group_codes = self.users[self.users['group_name'] == self.user_group]['code']
        max_code = in_group_codes.str.split('-', expand=True)[1].astype(int).max()
        group_code = self.groups[self.groups['group_name'] == self.user_group]['code'].iloc[0]
        self.code = f'{group_code}-{max_code + 1}'

    def add_user_to_db(self):
        session = create_session()
        new_user = UserSQL(
            code=self.code,
            username=self.username,
            name=self.name,
            salary=self.salary
        )
        new_role = session.query(RoleSQL).filter_by(function=self.user_role, level=self.user_level).scalar()
        if not new_role:
            new_role = RoleSQL(function=self.user_role, level=self.user_level)
            session.add(new_role)
        group = session.query(GroupSQL).filter_by(group_name=self.user_group).scalar()
        session.add(new_user)
        new_user.role.append(new_role)
        new_user.group.append(group)
        session.commit()
        session.close()

    def form(self):
        with st.form('form'):
            col1, col2 = st.columns([4, 1])
            with col1:
                self.show_name()
            with col2:
                self.show_salary()
            col1, col2 = st.columns(2)
            with col1:
                self.show_username()
            with col2:
                self.show_password()
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                self.show_role()
            with col2:
                self.show_group()
            with col3:
                self.show_level()
            self.button = st.form_submit_button('Добавить пользователя')
            if self.button:
                self.get_user_code()
                self.add_user_to_db()
                st.experimental_memo.clear()
                st.experimental_rerun()
