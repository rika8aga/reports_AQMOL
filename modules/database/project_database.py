import pandas as pd
import streamlit as st
import sqlalchemy.orm
from sqlalchemy import select, update
from .sql_classes import ProjectSQL, UserSQL, engine
from .user_database import load_users_data
import locale
from sqlalchemy.orm import sessionmaker

locale.setlocale(locale.LC_ALL, "ru")


def create_session() -> sqlalchemy.orm.Session:
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    return session


@st.experimental_memo()
def load_projects_data() -> pd.DataFrame:
    connection = engine.connect(close_with_result=True)
    stmt = select(ProjectSQL, UserSQL.name.label('chief_name')).join(UserSQL, isouter=True)
    dataframe = pd.read_sql(stmt, connection)
    return dataframe


class Projects:
    def __init__(self, change_data: bool):
        self.cipher_fin = None
        self.dataframe = load_projects_data()
        self.users = load_users_data()
        self.new_plan_ss = None
        self.new_plan_em = None
        self.new_plan_vk = None
        self.new_plan_ov = None
        self.new_plan_kj = None
        self.new_plan_as = None
        self.new_sections = None
        self.new_project_name = None
        self.new_project_type = None
        self.new_cipher_pilot = None
        self.expert_end = None
        self.expert_start = None
        self.project_id = None
        self.chief = None
        self.project_type = None
        self.project_name = None
        self.cipher_pilot = None
        self.selected_project = None
        self.all_projects = None
        self.data = None
        self.column = st.sidebar.selectbox(
            label='Поиск по:',
            options=[
                'По коду проекта',
                'По наименованию'
            ],
            index=1
        )
        self.not_to_change = 1 - change_data

    def project_selector(self):
        col1, col2, col3 = st.columns([2, 2, 6])
        match self.column:
            case 'По коду проекта':
                with col1:
                    self.cipher_pilot = st.selectbox(
                        'Код проекта:',
                        self.dataframe['cipher_pilot'].drop_duplicates()
                    )
                with col2:
                    self.project_type = st.selectbox(
                        'Тип проекта:',
                        self.dataframe[self.dataframe['cipher_pilot'] == self.cipher_pilot]['type']
                    )
                with col3:
                    self.data = self.dataframe[
                        (self.dataframe['cipher_pilot'] == self.cipher_pilot) &
                        (self.dataframe['type'] == self.project_type)
                        ]
                    self.project_name = st.selectbox(
                        'Наименование проекта:',
                        self.data['name'],
                        disabled=True
                    )
            case _:
                with col3:
                    self.project_name = st.selectbox(
                        'Наименование проекта:',
                        options=self.dataframe['name']
                    )
                    self.data = self.dataframe[self.dataframe['name'] == self.project_name]
                with col1:
                    self.cipher_pilot = st.selectbox(
                        'Код проекта:',
                        self.data['cipher_pilot'],
                        disabled=True
                    )
                with col2:
                    self.project_type = st.selectbox(
                        'Тип проекта:',
                        self.data['type'],
                        disabled=True
                    )
        self.project_id = int(self.data['id'].iloc[0])

    def show_name_changer(self):
        if not self.not_to_change:
            col1, col2, col3 = st.columns([2, 2, 6])
            with col1:
                self.new_cipher_pilot = st.text_input(
                    'Новый код:',
                    key=1,
                    value=self.cipher_pilot
                )
            with col2:
                self.new_project_type = st.text_input(
                    'Новый тип:',
                    key=2,
                    value=self.project_type
                )
            with col3:
                self.new_project_name = st.text_input(
                    'Новое наименование:',
                    key=3,
                    value=self.project_name
                )

    def show_cipher_fin(self):
        self.cipher_fin = st.text_input(
            'Шифр проекта:',
            value=self.data['cipher_fin'].iloc[0],
            disabled=self.not_to_change
        )

    def show_chief_and_dates(self):
        col1, col2, col3 = st.columns([4, 3, 3])
        with col1:
            if self.not_to_change:
                self.chief = st.selectbox(
                    label='Ответственный:',
                    options=self.data['chief_name'],
                    disabled=self.not_to_change
                )
            else:
                try:
                    index = self.users[
                        self.users['name'] == self.data['chief_name'].iloc[0]
                    ].iloc[0].name
                except IndexError:
                    index = 0
                self.chief = st.selectbox(
                    label='Ответственный:',
                    options=self.users['name'],
                    index=int(index)
                )
        with col2:
            self.expert_start = st.date_input(
                'Дата начала экпертизы:',
                self.data['expert_start'].iloc[0],
                disabled=self.not_to_change
            )
        with col3:
            self.expert_end = st.date_input(
                'Дата окончания экспертизы:',
                self.data['expert_end'].iloc[0],
                disabled=self.not_to_change
            )

    def show_sections(self):
        sections_string = self.data['sections'].iloc[0]
        sections_list = sections_string.split(',')

        plan_as_string = self.data['plan_AS'].iloc[0]
        plan_as_list = plan_as_string.split(',')

        plan_kj_string = self.data['plan_KJ'].iloc[0]
        plan_kj_list = plan_kj_string.split(',')

        plan_ov_string = self.data['plan_OV'].iloc[0]
        plan_ov_list = plan_ov_string.split(',')

        plan_vk_string = self.data['plan_VK'].iloc[0]
        plan_vk_list = plan_vk_string.split(',')

        plan_em_string = self.data['plan_EM'].iloc[0]
        plan_em_list = plan_em_string.split(',')

        plan_ss_string = self.data['plan_SS'].iloc[0]
        plan_ss_list = plan_ss_string.split(',')

        new_sections = []
        new_plan_as = []
        new_plan_kj = []
        new_plan_ov = []
        new_plan_vk = []
        new_plan_em = []
        new_plan_ss = []
        sections_number = st.number_input(
            'Кол-во секций',
            step=1,
            value=len(sections_list),
            disabled=self.not_to_change
        )
        col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 1.16, 1.16, 1.16, 1.16, 1.16, 1.16])
        for i in range(sections_number):
            if i != 0:
                visibility = 'collapsed'
            else:
                visibility = 'visible'
            with col1:
                try:
                    sec = st.text_input(
                        label='Блок-секции:',
                        label_visibility=visibility,
                        value=sections_list[i],
                        disabled=self.not_to_change,
                        key=f'section_{i}'
                    )
                except IndexError:
                    sec = st.text_input(
                        label='Блок-секции:',
                        label_visibility=visibility,
                        value=sections_list[0],
                        disabled=self.not_to_change,
                        key=f'section_{i}'
                    )
            with col2:
                try:
                    plan_as = st.text_input(
                        label='План АС:',
                        label_visibility=visibility,
                        value=plan_as_list[i],
                        disabled=self.not_to_change,
                        key=f'plan_as_{i}'
                    )
                except IndexError:
                    plan_as = st.text_input(
                        label='План АС:',
                        label_visibility=visibility,
                        value=plan_as_list[0],
                        disabled=self.not_to_change,
                        key=f'plan_as_{i}'
                    )
            with col3:
                try:
                    plan_kj = st.text_input(
                        label='План КЖ:',
                        label_visibility=visibility,
                        value=plan_kj_list[i],
                        disabled=self.not_to_change,
                        key=f'plan_kj_{i}'
                    )
                except IndexError:
                    plan_kj = st.text_input(
                        label='План КЖ:',
                        label_visibility=visibility,
                        value=plan_kj_list[0],
                        disabled=self.not_to_change,
                        key=f'plan_kj_{i}'
                    )
            with col4:
                try:
                    plan_ov = st.text_input(
                        label='План ОВ:',
                        label_visibility=visibility,
                        value=plan_ov_list[i],
                        disabled=self.not_to_change,
                        key=f'plan_ov_{i}'
                    )
                except IndexError:
                    plan_ov = st.text_input(
                        label='План ОВ:',
                        label_visibility=visibility,
                        value=plan_ov_list[0],
                        disabled=self.not_to_change,
                        key=f'plan_ov_{i}'
                    )
            with col5:
                try:
                    plan_vk = st.text_input(
                        label='План ВК:',
                        label_visibility=visibility,
                        value=plan_vk_list[i],
                        disabled=self.not_to_change,
                        key=f'plan_vk_{i}'
                    )
                except IndexError:
                    plan_vk = st.text_input(
                        label='План ВК:',
                        label_visibility=visibility,
                        value=plan_vk_list[0],
                        disabled=self.not_to_change,
                        key=f'plan_vk_{i}'
                    )
            with col6:
                try:
                    plan_em = st.text_input(
                        label='План ЭМ:',
                        label_visibility=visibility,
                        value=plan_em_list[i],
                        disabled=self.not_to_change,
                        key=f'plan_em_{i}'
                    )
                except IndexError:
                    plan_em = st.text_input(
                        label='План ЭМ:',
                        label_visibility=visibility,
                        value=plan_em_list[0],
                        disabled=self.not_to_change,
                        key=f'plan_em_{i}'
                    )
            with col7:
                try:
                    plan_ss = st.text_input(
                        label='План СС:',
                        label_visibility=visibility,
                        value=plan_ss_list[i],
                        disabled=self.not_to_change,
                        key=f'plan_ss_{i}'
                    )
                except IndexError:
                    plan_ss = st.text_input(
                        label='План СС:',
                        label_visibility=visibility,
                        value=plan_ss_list[0],
                        disabled=self.not_to_change,
                        key=f'plan_ss_{i}'
                    )
            new_sections.append(sec)
            new_plan_as.append(plan_as)
            new_plan_kj.append(plan_kj)
            new_plan_ov.append(plan_ov)
            new_plan_vk.append(plan_vk)
            new_plan_em.append(plan_em)
            new_plan_ss.append(plan_ss)
        self.new_sections = ','.join(new_sections)
        self.new_plan_as = ','.join(new_plan_as)
        self.new_plan_kj = ','.join(new_plan_kj)
        self.new_plan_ov = ','.join(new_plan_ov)
        self.new_plan_vk = ','.join(new_plan_vk)
        self.new_plan_em = ','.join(new_plan_em)
        self.new_plan_ss = ','.join(new_plan_ss)

    def show_data(self):
        self.show_name_changer()
        self.show_cipher_fin()
        self.show_chief_and_dates()
        self.show_sections()

    def change_name(self, session: sqlalchemy.orm.Session):
        if self.new_cipher_pilot != self.cipher_pilot:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                cipher_pilot=self.new_cipher_pilot
            )
            session.execute(stmt)
        if self.new_project_type != self.project_type:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                type=self.new_project_type
            )
            session.execute(stmt)
        if self.new_project_name != self.project_name:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                name=self.new_project_name
            )
            session.execute(stmt)

    def change_cipher_fin(self, session: sqlalchemy.orm.Session):
        if self.cipher_fin != self.data['cipher_fin'].iloc[0]:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                cipher_fin=self.cipher_fin
            )
            session.execute(stmt)

    def change_chief(self, session: sqlalchemy.orm.Session):
        if self.chief != self.data['chief_name'].iloc[0]:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                chief=select(UserSQL.id).where(UserSQL.name == self.chief)
            )
            session.execute(stmt)

    def change_dates(self, session: sqlalchemy.orm.Session):
        if pd.Timestamp(self.expert_start) != self.data['expert_start'].iloc[0]:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                expert_start=self.expert_start,
                expert_end=self.expert_end
            )
            session.execute(stmt)

    def change_sections_and_plan(self, session: sqlalchemy.orm.Session):
        if self.new_sections != self.data['sections'].iloc[0]:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                sections=self.new_sections
            )
            session.execute(stmt)
        if self.new_plan_as != self.data['plan_AS'].iloc[0]:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                plan_AS=self.new_plan_as
            )
            session.execute(stmt)
        if self.new_plan_kj != self.data['plan_KJ'].iloc[0]:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                plan_KJ=self.new_plan_kj
            )
            session.execute(stmt)
        if self.new_plan_ov != self.data['plan_OV'].iloc[0]:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                plan_OV=self.new_plan_ov
            )
            session.execute(stmt)
        if self.new_plan_vk != self.data['plan_VK'].iloc[0]:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                plan_AS=self.new_plan_vk
            )
            session.execute(stmt)
        if self.new_plan_em != self.data['plan_EM'].iloc[0]:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                plan_AS=self.new_plan_em
            )
            session.execute(stmt)
        if self.new_plan_ss != self.data['plan_SS'].iloc[0]:
            stmt = update(ProjectSQL).where(ProjectSQL.id == self.project_id).values(
                plan_AS=self.new_plan_ss
            )
            session.execute(stmt)

    def send_changes(self):
        if not self.not_to_change:
            change = st.button('Отправить изменения')
            if change:
                session = create_session()
                self.change_chief(session)
                self.change_dates(session)
                self.change_name(session)
                self.change_sections_and_plan(session)
                self.change_cipher_fin(session)
                session.commit()
                session.close()
                st.experimental_memo.clear()
                st.success('Изменения внесены')


class AddProject:
    def __init__(self):
        self.code = None
        self.users = load_users_data()
        self.projects = load_projects_data()
        col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 1.5])
        with col1:
            self.cipher_pilot = st.text_input(
                'Код проекта:', key='cipher_pilot'
            )
        with col2:
            self.project_kind = st.text_input(
                'Вид проекта (Б, К1...):', key='peoject_kind',
                value='Б'
            )
        with col3:
            self.project_type = st.selectbox(
                'Тип проекта:',
                options=['ЭП', '2Д', '3Д', 'НИС'], key='project_type'
            )
        with col4:
            project_build = st.selectbox(
                'Тип здания',
                options=['МЖК', 'ИЖД', 'Вилла', 'ОЗ'], key='project_build'
            )
        col1, col2, col3, col4 = st.columns([1.5, 1, 1.5, 2])
        with col1:
            self.project_name = st.text_input(
                'Наименование проекта:', key='project_name'
            )
        with col2:
            self.project_customer = st.text_input(
                'Заказчик', key='prject_customer'
            )
        with col3:
            project_year = st.number_input(
                'Год подписания:',
                min_value=2022, key='project_year',
                step=1
            )
        with col4:
            project_price = st.number_input(
                'Сумма по договору', key='project_price',
                step=1
            )
        col1, col2 = st.columns([3, 7])
        with col1:
            self.status = st.selectbox(
                'Статус:',
                options=[
                    'Перспективный',
                    'Разработка',
                    'Экспертиза',
                    'Завершен',
                    'Авторский надзор',
                    'Корректировка',
                    'Приостановлен',
                    'Отказ'
                ], key='status'
            )
        with col2:
            self.information = st.text_input(
                'Информация о проекте:', key='information'
            )
        self.cipher_fin = st.text_input(
            'Шифр проекта',
            value=f'ОД_{self.cipher_pilot}_'
                  f'{self.project_kind}_'
                  f'{self.project_type}_'
                  f'{project_build}_'
                  f'{self.project_name}_'
                  f'{self.project_customer}_{project_year}_{project_price}',
            disabled=True,
            key='cipher_fin'
        )
        col1, col2, col3 = st.columns([4, 3, 3])
        with col1:
            self.chief_name = st.selectbox(
                'Ответственный:',
                options=self.users['name'], key='chief_name'
            )
        with col2:
            self.expert_start = st.date_input(
                'Дата начала экспертизы:', key='expert_start'
            )
        with col3:
            self.expert_end = st.date_input(
                'Дата окончания экспертизы:', key='expert_end'
            )
        col1, col2, col3 = st.columns([4, 3, 3])
        with col1:
            sections_number = st.number_input(
                'Количество блоков',
                min_value=1,
                step=1
            )
        with col2:
            self.date_start = st.date_input(
                'Дата начала проекта:', key='date_start'
            )
        with col3:
            self.date_end = st.date_input(
                'Дата окончания проекта:', key='date_end'
            )
        sections = []
        plans_as = []
        plans_kj = []
        plans_ov = []
        plans_vk = []
        plans_em = []
        plans_ss = []
        col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 1.16, 1.16, 1.16, 1.16, 1.16, 1.16])
        for row in range(sections_number):
            if row == 0:
                visibility = 'visible'
            else:
                visibility = 'collapsed'
            with col1:
                section = st.text_input(
                    'Блок-секции:',
                    key=f'sections_{row}',
                    value=f'Блок {row + 1}',
                    label_visibility=visibility
                )
            with col2:
                plan_as = st.text_input(
                    label='План АС:',
                    label_visibility=visibility,
                    value=0,
                    key=f'plans_as_{row}'
                )
            with col3:
                plan_kj = st.text_input(
                    label='План КЖ:',
                    label_visibility=visibility,
                    value=0,
                    key=f'plans_kj_{row}'
                )
            with col4:
                plan_ov = st.text_input(
                    label='План ОВ:',
                    label_visibility=visibility,
                    value=0,
                    key=f'plans_ov_{row}'
                )
            with col5:
                plan_vk = st.text_input(
                    label='План ВК:',
                    label_visibility=visibility,
                    value=0,
                    key=f'plans_vk_{row}'
                )
            with col6:
                plan_em = st.text_input(
                    label='План ЭМ:',
                    label_visibility=visibility,
                    value=0,
                    key=f'plans_em_{row}'
                )
            with col7:
                plan_ss = st.text_input(
                    label='План СС:',
                    value=0,
                    label_visibility=visibility,
                    key=f'plans_ss_{row}'
                )
            sections.append(section)
            plans_as.append(plan_as)
            plans_kj.append(plan_kj)
            plans_ov.append(plan_ov)
            plans_vk.append(plan_vk)
            plans_em.append(plan_em)
            plans_ss.append(plan_ss)
        self.sections = ','.join(sections)
        self.plans_as = ','.join(plans_as)
        self.plans_kj = ','.join(plans_kj)
        self.plans_ov = ','.join(plans_ov)
        self.plans_vk = ','.join(plans_vk)
        self.plans_em = ','.join(plans_em)
        self.plans_ss = ','.join(plans_ss)

    def get_project_code(self):
        match self.project_type:
            case 'ЭП':
                code = '1'
            case '2Д':
                code = '2'
            case '3Д':
                code = '3'
            case _:
                code = '4'
        max_code = self.projects['code'].str.split('-', expand=True)[1].astype(int).max()
        self.code = f'{code}-{str(max_code + 1)}'

    def create_request(self):
        self.get_project_code()
        chief_id = int(self.users[self.users['name'] == self.chief_name]['id'].iloc[0])
        project = ProjectSQL(
            code=self.code,
            cipher_pilot=self.cipher_pilot,
            type=self.project_type,
            name=f'{self.cipher_pilot}_{self.project_name}_{self.project_type}_{self.project_kind}',
            status=self.status,
            chief=chief_id,
            cipher_fin=self.cipher_fin,
            sections=self.sections,
            date_start=self.date_start,
            date_end=self.date_end,
            expert_start=self.expert_start,
            expert_end=self.expert_end,
            information=self.information,
            plan_AS=self.plans_as,
            plan_KJ=self.plans_kj,
            plan_OV=self.plans_ov,
            plan_VK=self.plans_vk,
            plan_EM=self.plans_em,
            plan_SS=self.plans_ss
        )
        session = create_session()
        session.add(project)
        session.commit()
        session.close()
        st.success('Проект добавлен в базу')

    def send_request(self):
        if '' in [self.cipher_pilot, self.project_name, self.project_customer]:
            st.warning('Заполните необходимые поля')
        else:
            if st.button('Отправить'):
                self.create_request()
                st.experimental_memo.clear()
