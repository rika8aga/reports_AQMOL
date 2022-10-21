import pandas as pd
import streamlit as st
from sqlalchemy import select, update, insert
from .sql_classes import Project, session


class Projects:
    def __init__(self):
        self.dataframe = None
        self.selected_project = None
        self.all_projects = None
        self.data = None

    def read_as_dataframe(self):
        self.dataframe = pd.read_sql_table(
            'projects',
            "sqlite:///C:\\Users\\zharmakin\\OneDrive\\python_projects\\reports_AQMOL\\data\\test_6.db"
        )

    def get_all_projects(self):
        stmt = select(Project)
        result = session.execute(stmt).scalars().all()
        self.all_projects = pd.DataFrame([i.name for i in result])
        self.all_projects.rename(columns={0: 'Наименование проекта'}, inplace=True)
        session.commit()

    def project_selector(self):
        self.selected_project = st.selectbox(
            label='Проект',
            options=self.all_projects
        )

    def project_info(self):
        stmt = select(Project).where(Project.name == self.selected_project)
        result = session.execute(stmt).first()
        for i in result:
            self.data = [
                i.id,
                i.code,
                i.cipher_pilot,
                i.type,
                i.status,
                i.chief,
                i.cipher_fin,
                i.sections,
                i.date_start,
                i.date_end,
                i.expert_start,
                i.expert_end,
                i.information,
                i.users,
                i.plan_AS,
                i.plan_KJ,
                i.plan_OV,
                i.plan_VK,
                i.plan_EM,
                i.plan_SS
            ]
        self.data = pd.DataFrame(
            data=self.data,
            columns=[
                'id', 'code', 'cipher_pilot', 'type', 'status', 'chief', 'cipher_fin',
                'sections', 'date_start', 'date_end', 'expert_start', 'expert_end',
                'information', 'users', 'plan_AS', 'plan_KJ', 'plan_OV', 'plan_VK',
                'plan_EM', 'plan_SS'
            ]
        )
        self.data.astype(
            {
                'id': int,
                'code': str,
                'cipher_pilot': str,
                'type': str,
                'status': str,
                'chief': int,
                'cipher_fin': str,
                'sections': str,
                'information': str,
                'plan_AS': float,
                'plan_KJ': float,
                'plan_OV': float,
                'plan_VK': float,
                'plan_EM': float,
                'plan_SS': float
            }
        )

