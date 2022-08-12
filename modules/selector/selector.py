import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
import numpy as np


class ProjectSelector:
    def __init__(self, df: pd.DataFrame):
        self.dataframe = df
        self.project_selector = None
        self.dataframe_by_project = None
        self.pivot = None
        self.styled_pivot = None

    def select_box(self):
        projects = self.dataframe['Проект'].drop_duplicates(
        ).sort_values().to_list()
        projects.insert(0, 'Все')
        self.project_selector = st.selectbox(
            'Проект',
            options=projects
        )
        return self.project_selector

    def df_by_project(self):
        selected_project = self.project_selector
        match selected_project:
            case 'Все':
                self.dataframe_by_project = self.dataframe
            case _:
                self.dataframe_by_project = self.dataframe[self.dataframe['Проект']
                                                           == selected_project]

    def pivot_by_project(self):
        try:
            self.pivot = pd.pivot_table(
                self.dataframe_by_project,
                index='Проект',
                values='Часы',
                columns='Вид работы',
                aggfunc=np.sum,
                margins=True,
                margins_name='ИТОГО',
                dropna=False,
                fill_value=0,
            )
            self.pivot.sort_values(by='ИТОГО', inplace=True, ascending=False)
            self.pivot.drop(['ИТОГО'], inplace=True)
        except ValueError:
            pass

    def get_styled_pivot(self):
        self.select_box()
        self.df_by_project()
        self.pivot_by_project()
        match self.pivot:
            case None:
                pass
            case _:
                self.styled_pivot = self.pivot.style.applymap(
                    lambda x: 'color:#182A3E;background-color:#DAF5E9;font-weight:bold;'
                    if x != 0 else 'opacity: 20%;'
                ).format('{:.1f}')


def date_input(default):
    match default:
        case '':
            diapason = date.today()
        case 'last_month':
            today = date.today()
            first_day_of_month = today.replace(day=1)
            date_start = today.replace(day=1, month=today.month - 1)
            date_end = first_day_of_month - timedelta(days=1)
            diapason = [date_start, date_end]
        case days:
            date_end = date.today()
            date_start = np.busday_offset(
                date.today(), days, roll='forward').astype(date)
            diapason = [date_start, date_end]
    return st.date_input('Период', diapason)


class MissReports:
    def __init__(self, group_name: str, df: pd.DataFrame, resources: pd.DataFrame):
        self.group = group_name
        self.df = df
        self.resources = resources
        self.group_resources = None
        self.merged = None
        self.merged_pivot = None
        self.missing_reports = None

    def get_group_resources(self):
        self.group_resources = self.resources[
            self.resources['Отдел'] == self.group
        ]

    def merging(self):
        match self.df.empty:
            case True:
                pass
            case False:
                self.merged = self.group_resources.merge(
                    self.df[['Ф.И.О.', 'Дата отчета']], how='left', on="Ф.И.О.")
                self.merged.drop_duplicates(inplace=True)

    def merge_to_pivot(self):
        try:
            self.merged_pivot = pd.pivot_table(
                self.merged,
                index='Ф.И.О.',
                columns='Дата отчета',
                values='Отдел',
                aggfunc='count',
                dropna=False,
                fill_value=0
            )
            self.merged_pivot.columns = self.merged_pivot.columns.map(
                lambda x: '.'.join(str(x).split(' ')[0].split('-')[::-1])
            )
        except TypeError:
            pass

    def pivot_to_style(self):
        self.get_group_resources()
        self.merging()
        self.merge_to_pivot()
        match self.merged_pivot:
            case None:
                pass
            case _:
                self.missing_reports = self.merged_pivot.style.applymap(
                    lambda x: 'color: #FC1781; background-color: #FC1781;'
                    if x == 0 else 'color: #47D094; background-color: #47D094;'
                )


class Selectors:
    def __init__(self):
        self.style_option = None
        self.value = None
        self.period = None
        self.dates = None
        self.value_selector = st.radio(
            'Показать в:',
            options=('часах', 'днях', 'тенге')
        )
        self.period_selector = st.radio(
            'Период отчета:',
            options=('по датам', 'по месяцам')
        )

    def select_date_filter(self, default: str | int):
        match self.period_selector:
            case 'по датам':
                self.dates = date_input(default)
                self.period = 'Дата отчета'
                return self.dates
            case _:
                self.period = 'Месяц'
                self.dates = (datetime.strptime(
                    '01.01.2019', '%d.%m.%Y'), datetime.today())

    def select_value_filter(self):
        match self.value_selector:
            case 'часах':
                self.value = 'Часы'
                self.style_option = 'в часах'
            case 'днях':
                self.value = 'Часы'
                self.style_option = 'в днях'
            case _:
                self.value = 'Расходы'
                self.style_option = 'в деньгах'
