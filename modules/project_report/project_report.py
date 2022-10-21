import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from numpy import datetime64
from modules.database.project_database import load_projects_data
from modules.database.user_database import load_users_data
from modules.to_import import calendar
import streamlit as st
from glob import glob
from datetime import date, timedelta


def read_csv(args: str) -> DataFrame:
    header = [
        'name',
        'group',
        'project_code',
        'section',
        'job_type',
        'is_correction',
        'hours',
        'percentage',
        'date_report',
        'date_send',
        'comment'
    ]
    return pd.read_csv(args, header=None, names=header)


def value_format(value):
    match value:
        case float() | int() if value != 0:
            return 'color: #182A3E; background-color: #DAF5E9;'
        case float() | int() if value == 0:
            return 'color: #ffffff;'


class Reports:
    def __init__(self):
        self.users = load_users_data().drop_duplicates(subset=['name'])
        self.projects = load_projects_data().rename(
            mapper={
                'name': 'project_name',
                'code': 'project_code'
            },
            axis=1
        )
        self.dataframe = pd.concat(map(read_csv, glob(r'Z:\11. Bim-отдел\reports\*.csv')), ignore_index=True)
        self.dataframe.fillna(value='Нет', inplace=True)
        self.dataframe['date_report'] = pd.to_datetime(self.dataframe['date_report'], format='%d.%m.%Y')

    def complete_report(self):
        self.dataframe = self.dataframe.merge(
            self.projects[['project_code', 'cipher_pilot', 'project_name', 'cipher_fin']],
            how='left',
            on='project_code'
        )

    def add_days(self):
        self.dataframe['days'] = self.dataframe['hours'] / 8

    def add_month(self):
        self.dataframe['month_number'] = pd.DatetimeIndex(self.dataframe['date_report']).month
        self.dataframe['month_name'] = self.dataframe['date_report'].dt.month_name(locale='Ru')

    def add_work_hours(self):
        calendar_table = calendar().reset_index().rename(
            {
                'Часы': 'work_hours',
                'Номер': 'month_number'
            },
            axis=1
        )
        self.dataframe = self.dataframe.merge(
            calendar_table[['month_number', 'work_hours']],
            how='left',
            on='month_number',
        )

    def add_salary(self):
        self.dataframe = self.dataframe.merge(
            self.users[['name', 'salary']],
            how='left',
            on='name'
        )

    def get_job_price(self):
        self.dataframe['price'] = self.dataframe['hours'] * self.dataframe['salary'] / self.dataframe['work_hours']

    def create_data(self):
        self.complete_report()
        self.add_days()
        self.add_month()
        self.add_work_hours()
        self.add_salary()
        self.get_job_price()


@st.experimental_memo(show_spinner=False)
def cash_report():
    with st.spinner('Загрузка данных'):
        report = Reports()
        report.create_data()
    return report.dataframe


class ProjectSelector:
    def __init__(self):
        self.projects: DataFrame = load_projects_data()
        col1, col2 = st.columns([2, 1])
        with col1:
            cipher_pilot: list = st.multiselect(
                label='Проект',
                options=self.projects['cipher_pilot'].drop_duplicates(),
                default='000'
            )
            self.projects = self.projects[self.projects['cipher_pilot'].isin(cipher_pilot)]
        with col2:
            project_type: list = st.multiselect(
                label='Тип',
                options=self.projects['type'].drop_duplicates()
            )
            match project_type:
                case []:
                    self.project_codes = self.projects['code']
                case _:
                    self.project_codes = self.projects[self.projects['type'].isin(project_type)]['code']


class PeriodSelector:
    def __init__(self):
        period_type = st.sidebar.selectbox(
            label='period',
            label_visibility='collapsed',
            options=['all', 'period'],
            format_func=lambda x: 'За весь период' if x == 'all' else 'Выбрать период',
            index=1
        )
        match period_type:
            case 'period':
                period = st.sidebar.date_input(
                    label='period',
                    label_visibility='collapsed',
                    value=[date.today() - timedelta(days=7), date.today()]
                )
                match period:
                    case start, end:
                        self.date_start = np.datetime64(start)
                        self.date_end = np.datetime64(end)
                    case (start,):
                        self.date_start = np.datetime64(start)
                        self.date_end = np.datetime64(date.today())
            case _:
                self.date_start = np.datetime64('1991-05-22')
                self.date_end = np.datetime64('today')
        self.columns = st.sidebar.selectbox(
            label='column',
            label_visibility='collapsed',
            options=['month_name', 'date_report'],
            format_func=lambda x: 'По месяцам' if x == 'month_name' else 'По дням'
        )


class ProjectInfo:
    def __init__(self, project_codes: Series, date_start: datetime64, date_end: datetime64, columns: str):
        self.filter = None
        self.project_codes = project_codes
        self.columns = columns
        values = {
            'hours': 'Часы',
            'days': 'Дни',
            'price': 'Тенге'
        }
        self.values = st.sidebar.radio(
            label='values',
            label_visibility='collapsed',
            options=values.keys(),
            format_func=lambda x: values.get(x),
            horizontal=True
        )
        self.pivot_table = None
        report = cash_report()
        self.report = report[
            (report['project_code'].isin(project_codes)) &
            (report['date_report'] >= date_start) &
            (report['date_report'] <= date_end)
        ].copy(deep=True)
        self.report.sort_values(by=['date_report', 'name', 'project_name'], inplace=True)
        self.indexes = {
            'project_name': 'Проект',
            'section': 'Блок',
            'group': 'Отдел',
            'job_type': 'Вид работы',
            'name': 'Сотрудник'
        }
        self.index = st.multiselect(
            label='Группировать по:',
            options=self.indexes.keys(),
            format_func=lambda x: self.indexes.get(x)
        )
        if not self.index:
            self.index = ['project_name']
        
    def create_filter(self):
        with st.expander('Фильтры'):
            for i in self.index:
                value = st.multiselect(
                    label=self.indexes[i],
                    options=self.report[i].drop_duplicates()
                )
                if value:
                    self.report = self.report[self.report[i].isin(value)]

    def create_pivot(self):
        if not self.report.empty:
            pivot_table = pd.pivot_table(
                data=self.report,
                index=self.index,
                columns=self.columns,
                values=self.values,
                aggfunc=np.sum,
                margins=True,
                margins_name='Итого',
                sort=False,
                fill_value=0
            )
            match self.columns:
                case 'date_report':
                    pivot_table.columns = pivot_table.columns.map(
                        lambda x: '.'.join(str(x).split(' ')[0].split('-')[::-1])
                    )
            pivot_table = pivot_table.style.format(
                formatter='{:,.2f}', thousands=' '
            )
            pivot_table = pivot_table.applymap(
                lambda x: 'color: #ffffff;' if x == 0 else 'color: #182A3E;'
            )
            pivot_table.background_gradient(
                subset=(
                    pivot_table.index[:-1],
                    pivot_table.columns.tolist()
                )
            )
            st.dataframe(pivot_table, use_container_width=True)
        else:
            st.info('Не выбран проект')

