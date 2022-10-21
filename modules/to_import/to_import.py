from datetime import datetime, date
from glob import glob
import numpy as np
import pandas as pd
import streamlit as st
import locale
from modules.levels import Groups
from modules.plots import value_format, float_format

locale.setlocale(locale.LC_ALL, "ru")


@st.experimental_memo(show_spinner=False)
def job_types():
    return pd.read_excel(r"Z:\11. Bim-отдел\data\types_of_job.xlsx", 'job_types',  dtype={'group_code': str})


@st.experimental_memo(show_spinner=False)
def resources():
    return pd.read_excel(r"Z:\11. Bim-отдел\data\resources.xlsx", sheet_name='TDSheet')


@st.experimental_memo(show_spinner=False)
def projects():
    return pd.read_excel(
        r"Z:\11. Bim-отдел\data\projects.xlsx",
        'Реестр проектов 08.07.'
    )


@st.experimental_memo(show_spinner=False)
def calendar():
    return pd.read_excel(
        r"Z:\11. Bim-отдел\data\Календарь.xlsx",
        'Лист1',
        index_col='Номер'
    )


@st.experimental_memo(show_spinner=False)
def salaries():
    return pd.read_excel(
        r"Z:\11. Bim-отдел\data\resource_salaries.xlsx",
        'TDSheet',
        index_col='Ф.И.О.'
    )


def get_salary(name: str):
    df_salaries = salaries()
    try:
        salary_by_name = df_salaries.loc[name, 'Оклад']
    except KeyError:
        salary_by_name = 1
    return salary_by_name


def get_work_hours(month_number: int):
    df_calendar = calendar()
    work_hours = df_calendar.loc[month_number, 'Часы']
    return work_hours


def get_task_price(salary: int, hours: float, work_hours: int):
    hour_price = salary / work_hours
    task_price = hours * hour_price
    return task_price


def get_month(date_in: str):
    day = datetime.strptime(date_in, '%d.%m.%Y')
    month = day.strftime("%B")
    number = day.strftime("%m")
    return pd.Series([month, int(number)])


def get_project_names(project_id: str):
    project_names = projects()
    name_by_id = project_names.loc[project_id, 'Human_name']
    return name_by_id


class Reports:
    def __init__(self):
        self.directory = r'Z:\11. Bim-отдел\reports'
        self.files = None
        self.headers = [
            'Ф.И.О.',
            'Отдел',
            'ID',
            'Блок',
            'Вид работы',
            'Корректировка',
            'Часы',
            'Процент выполнения',
            'Дата отчета',
            'Отчет сдан',
            'Описание работы'
        ]
        self.report_day = 'Дата отчета'
        self.d_types = {
            'Ф.И.О.': 'object',
            'Отдел': 'object',
            'ID': 'object',
            'Блок': 'object',
            'Вид работы': 'object',
            'Корректировка': 'int',
            'Часы': 'float',
            'Процент выполнения': 'int',
            'Дата отчета': 'object',
            'Отчет сдан': 'object',
            'Описание работы': 'object'
        }
        self.to_fill = {
            'Часы': 0,
            'Блок': 'Нет',
            'Описание работы': 'Нет'
        }
        self.report = pd.DataFrame(columns=self.headers)
        self.expenses_report = None
        self.accountant_report = None

    def read_directory(self, filter_by: str | tuple):
        match filter_by:
            case 'all':
                self.files = glob(f'{self.directory}\\*.*')
            case code_1, code_2:
                files_1 = glob(f'{self.directory}\\*{code_1}*.csv')
                files_2 = glob(f'{self.directory}\\*{code_2}*.csv')
                self.files = files_1 + files_2
            case code:
                self.files = glob(f'{self.directory}\\*{code}*.csv')

    def read_csv(self, filter_by: str | tuple):
        self.report = pd.DataFrame(columns=self.headers)
        self.read_directory(filter_by)
        for file in self.files:
            try:
                df_file = pd.read_csv(
                    file,
                    header=None,
                    names=self.headers,
                    dtype=self.d_types,
                    encoding='utf-8-sig'
                )
                self.report = pd.concat([self.report, df_file], ignore_index=True)
            except:
                st.write(file)

    def fill_na(self):
        self.report.fillna(value=self.to_fill, inplace=True)

    def add_month_columns(self):
        self.report[['Месяц', 'Номер']
                    ] = self.report[self.report_day].apply(get_month)

    def add_work_hours(self):
        self.report['Рабочие часы'] = self.report['Номер'].apply(
            get_work_hours)

    def add_salaries(self):
        self.report['Оклад'] = self.report['Ф.И.О.'].apply(get_salary)

    def date_type(self):
        self.report[self.report_day] = pd.to_datetime(
            self.report[self.report_day], format='%d.%m.%Y')

    # def code_to_names(self):
    #     self.report['Проект'] = self.report['ID'].apply(get_project_names)

    def code_to_names(self):
        project_names = projects()[['Human_name', 'ID']]
        self.report = self.report.merge(project_names, how='left', on='ID')
        self.report.rename(columns={'Human_name': 'Проект'}, inplace=True)

    def code_to_cipher(self):
        project_names = projects()[['Название проекта', 'ID']]
        self.report = self.report.merge(project_names, how='left', on='ID')
        self.report.rename(
            columns={'Название проекта': 'Проект'}, inplace=True)

    def get_report(self, filter_by: str | tuple):
        self.read_csv(filter_by)
        self.fill_na()
        self.add_month_columns()
        self.date_type()
        self.code_to_names()

    def get_expenses(self, filter_by: str | tuple):
        self.get_report(filter_by)
        self.add_work_hours()
        self.add_salaries()
        self.expenses_report = self.report.copy()
        self.expenses_report['Расходы'] = self.expenses_report.apply(
            lambda x: get_task_price(x['Оклад'], x['Часы'], x['Рабочие часы']),
            axis=1
        )

    def reduce_dates(self):
        self.accountant_report['Всего часов'] = self.accountant_report.groupby(
            ['Ф.И.О.', 'Номер'], sort=False
        )['Часы'].transform('sum')
        self.accountant_report['Процент уменьшения'] = self.accountant_report.apply(
            lambda x: x['Рабочие часы'] / x['Всего часов'] if x['Рабочие часы'] < x['Всего часов'] else 1,
            axis=1
        )
        self.accountant_report['Часы'] = self.accountant_report['Часы'] * self.accountant_report['Процент уменьшения']

    def get_accountant_report(self):
        self.read_csv('all')
        self.fill_na()
        self.add_month_columns()
        self.date_type()
        self.code_to_cipher()
        self.add_work_hours()
        self.add_salaries()
        self.accountant_report = self.report.copy()
        self.reduce_dates()
        self.accountant_report['Расходы'] = self.accountant_report.apply(
            lambda x: get_task_price(x['Оклад'], x['Часы'], x['Рабочие часы']),
            axis=1
        )


def zero_project(project_id: str, project_name: str, group_name: str):
    match project_id:
        case '0-00':
            jt = job_types()
            try:
                zero_job = jt[jt['Отдел'] == group_name]['0-00'].iloc[0]
                return zero_job
            except IndexError:
                print(f'{project_id},{project_name},{group_name}')
        case _:
            return project_name


def for_estimate(group_name: str, project_id: str, job_type: str) -> str:
    try:
        project_type = project_id.split('-')[0]
    except AttributeError:
        st.write(project_id, group_name, job_type)
    match group_name, project_type:
        case Groups.estimate, '3':
            return 'Сметная документация_3Д'
        case Groups.estimate, '2':
            return 'Сметная документация_2Д'
        case str(), '0':
            return 'Зарплата'
        case _:
            return job_type


def section_by_id(project_id: str, section: str) -> str:
    match section:
        case 'Нет' | 'Все' | 'ЭП' | 'нет':
            output_sec = 'объект'
        case _:
            if '-' in section:
                output_sec = section.split('-')[0]
            else:
                output_sec = section
    match project_id:
        case '0-00':
            output_sec = 'Зарплата'
    return output_sec


class Report1C:
    def __init__(self):
        self.selected_group = None
        self.filtered_pivot = None
        self.block_filter = None
        self.job_type_filter = None
        self.project_filter = None
        self.dates_filter = None
        self.names_filter = None
        self.table_1C = None
        self.transaction_day = None
        self.dataframe_length = None
        self.pivot_report = None

    def report_init(self, df: pd.DataFrame):
        self.table_1C: pd.DataFrame = df

    def group_selector(self):
        group_list = ['Все'] + self.table_1C['Отдел'].drop_duplicates().tolist()
        self.selected_group = st.selectbox(
            'Отдел:',
            options=group_list
        )

    def filter_by_group(self):
        match self.selected_group:
            case 'Все':
                pass
            case _:
                self.table_1C = self.table_1C[self.table_1C['Отдел'] == self.selected_group]

    def replace_sections(self):
        self.table_1C['Блок'] = self.table_1C.apply(
            lambda x: section_by_id(x['ID'], x['Блок']), axis=1)

    def get_length(self):
        self.dataframe_length = len(self.pivot_report)

    def add_transaction_column(self, diapason: tuple):
        try:
            self.transaction_day = [diapason[0]]
        except IndexError:
            self.transaction_day = [date.today()]
        self.pivot_report.insert(
            1,
            'Период взаиморасчета',
            pd.Series(self.transaction_day * self.dataframe_length)
        )

    def replace_estimate_job(self):
        self.table_1C['Вид работы'] = self.table_1C.apply(
            lambda x: for_estimate(x['Отдел'], x['ID'], x['Вид работы']),
            axis=1
        )

    def replace_zero_project(self):
        self.table_1C['Проект'] = self.table_1C.apply(
            lambda x: zero_project(x['ID'], x['Проект'], x['Отдел']), axis=1)

    def get_columns(self):
        self.table_1C = self.table_1C[[
            'Ф.И.О.', 'Проект', 'Вид работы', 'Блок', 'Расходы'
        ]]

    def create_report(self, df: pd.DataFrame):
        self.report_init(df)
        self.group_selector()
        self.filter_by_group()
        self.replace_sections()
        self.replace_estimate_job()
        self.replace_zero_project()
        self.get_columns()

    def reset_index(self):
        self.pivot_report.reset_index(inplace=True)

    def rename_columns(self):
        self.pivot_report.rename(columns={
            'Ф.И.О.': 'Физлицо',
            'Проект': 'Номенклатурная группа',
            'Вид работы': 'Вид работ',
            'Блок': 'Тип здания',
            'Расходы': 'заработная плата'
        }, inplace=True)

    def get_pivot_report(self, diapason: tuple):
        self.pivot_report = self.table_1C.pivot_table(
            index=['Ф.И.О.', 'Проект', 'Вид работы', 'Блок'],
            values='Расходы',
            aggfunc=np.sum
        )
        self.reset_index()
        self.get_length()
        self.add_transaction_column(diapason)
        self.rename_columns()


class GroupReport:
    def __init__(self, df: pd.DataFrame):
        self.styled_pivot = None
        self.dataframe = df
        self.fields = None
        self.pivot_df = None
        self.index_df = None

    def get_fields(self):
        options = ['Ф.И.О.', 'Проект', 'Блок', 'Вид работы', 'Описание работы']
        self.fields = st.multiselect(
            'Поля группировки',
            options=options,
            default=options[:-2]
        )

    def get_pivot(self, period, value, style_option):
        match self.fields:
            case []:
                return st.info('Нет данных')
            case _:
                self.pivot_df = pd.pivot_table(
                    self.dataframe,
                    index=self.fields,
                    values=value,
                    columns=period,
                    aggfunc=np.sum,
                    margins=True,
                    margins_name='ИТОГО',
                    fill_value=0
                )
                self.reset_index()
                self.to_style(style_option)
                return st.table(self.styled_pivot)

    def reset_index(self):
        self.pivot_df.reset_index(inplace=True)

    def to_style(self, unit_type: str):
        self.pivot_df.columns = self.pivot_df.columns.map(
            lambda x: '.'.join(str(x).split(' ')[0].split('-')[::-1])
        )
        self.styled_pivot = self.pivot_df.style.format(
            lambda x: float_format(x, unit_type))
        self.styled_pivot = self.styled_pivot.applymap(
            value_format
        )


@st.experimental_memo(show_spinner=False)
def cached_expenses(code: str):
    report_class = Reports()
    report_class.get_expenses(code)
    return report_class.expenses_report


@st.experimental_memo(show_spinner=False)
def cached_report(code: str):
    report_class = Reports()
    report_class.get_report(code)
    return report_class.report


@st.experimental_memo(show_spinner=False)
def cashed_accountant_report():
    report_class = Reports()
    report_class.get_accountant_report()
    return report_class.accountant_report


if __name__ == '__main__':
    reports = Reports()
