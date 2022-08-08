from datetime import datetime, date
import streamlit as st
from io import BytesIO
import openpyxl
import pandas as pd
from openpyxl.styles import Border, Side, Font, Alignment
from report_app.plots import pivot_table
from report_app.levels import Levels
from report_app.to_import import resources, projects, job_types


def exel_styling(sheet, df_length):
    cell_range = sheet['A12':f'M{12 + df_length}']
    border = Border(
        left=Side(border_style='thin', color='00000000'),
        right=Side(border_style='thin', color='00000000'),
        top=Side(border_style='thin', color='00000000'),
        bottom=Side(border_style='thin', color='00000000')
    )

    font = Font(
        name='TimesNewRoman',
        size=11
    )

    alignment = Alignment(
        wrap_text=True,
        vertical='center'
    )
    for row in cell_range:
        for cell in row:
            cell.font = font
            cell.alignment = alignment
            cell.border = border


def to_xlsx(name: str, diapason: tuple, df: pd.DataFrame, unit_type):
    match diapason:
        case date_start, date_end:
            date_end = date_end
        case (date_start,):
            date_end = date.today()
    binary_output = BytesIO()
    group_by = ['Проект', 'Блок', 'Вид работы', 'ИТОГО']
    output_df = pivot_table(df, group_by[:-1], unit_type)
    output_df.drop(len(output_df), inplace=True, axis=0)
    last_row = len(output_df)
    book = openpyxl.load_workbook(r"Z:\11. Bim-отдел\data\бланк_ЗП.xlsx")
    sheet = book.active

    sheet['C3'] = name
    sheet['B5'] = date_end.strftime("%B")
    sheet['F5'] = date_end.strftime("%Y")
    sheet['F7'] = datetime.today()

    for index, row in output_df.iterrows():
        sheet[f'C{12 + index - 1}'] = row['Проект']
        sheet[f'F{12 + index - 1}'] = row['Вид работы']
        sheet[f'E{12 + index - 1}'] = row['Блок']
        sheet[f'I{12 + index - 1}'] = row['ИТОГО'] / 8
        sheet.insert_rows(12 + index)
    sheet[f'I{12 + last_row + 1}'] = f'=SUM(I12:I{12 + last_row})'
    exel_styling(sheet, last_row)
    book.save(binary_output)
    return binary_output


def report_to_csv(user_code: str, df: pd.DataFrame):
    report_file_name = f'report_{user_code}_{datetime.today().strftime("%m")}.csv'
    report_file = f'Z:\\11. Bim-отдел\\reports\\{report_file_name}'
    df.to_csv(
        report_file,
        header=False,
        mode='a',
        encoding='utf-8-sig',
        index=False
    )


def accountant_report_xlsx(df: pd.DataFrame):
    binary_output = BytesIO()
    df.to_excel(binary_output, encoding='utf-8-sig', index=False, sheet_name='TDSheet', startcol=1)
    return binary_output


class ReportFormHead:
    def __init__(self, user_class):
        self.fields_number = None
        self.user = user_class
        self.resource_name = None
        self.resources = resources()
        self.projects = projects()
        self.job_types = job_types()
        match self.user.group_code:
            case group_code_1, group_code_2:
                self.user_jobs = self.job_types[
                    (self.job_types['group_code'] == group_code_1) | (self.job_types['group_code'] == group_code_2)
                ]
            case group_code:
                self.user_jobs = self.job_types[self.job_types['group_code'] == group_code]
        match self.user.level:
            case Levels.worker:
                self.user_jobs = self.user_jobs[self.user_jobs['level'] == self.user.level]

    def name_selector(self):
        match self.user.level:
            case Levels.admin:
                self.resource_name = st.selectbox(
                    'Ф.И.О',
                    options=self.resources['Ф.И.О.'].unique(),
                    help='Выберите свое имя'
                )
            case _:
                self.resource_name = st.text_input(
                    'Ф.И.О',
                    value=self.user.name,
                    disabled=True
                )

    def fields_selector(self):
        self.fields_number = st.number_input(
            'Количество полей',
            min_value=1,
            max_value=5,
            step=1,
            format='%d'
        )

    def form(self):
        name_column, field_column = st.columns([8, 2])
        with name_column:
            self.name_selector()
        with field_column:
            self.fields_selector()


class ReportFormBody:
    def __init__(self, user_class, field_number, user_jobs, projects_df):
        self.data_dataframe = None
        self.projects = projects_df
        self.resource_name = user_class.name
        self.user_code = user_class.code
        self.user_jobs = user_jobs
        self.field_number = field_number
        self.collected_data = []
        self.date = None
        self.hours = None
        self.percentage = None
        self.correction = None
        self.comment = None
        self.sections = None
        self.project_name = None
        self.section = None
        self.job = None
        self.file_name = f'report_{self.user_code}_{datetime.today().strftime("%m")}.csv'
        self.file_path = f'Z:\\11. Bim-отдел\\reports\\{self.file_name}'
        self.clear_on_submit = False

    def project_selector(self, field_index):
        self.project_name = st.selectbox(
            'Проект:',
            options=self.projects['Human_name'].sort_values(),
            key=f'Проект_{field_index}'
        )
        self.sections = self.projects[self.projects['Human_name'] == self.project_name].iloc[0, 4]

    def section_selector(self, field_index):
        self.section = st.selectbox(
            'Блок:',
            key=f'Блок_{field_index}',
            options=self.sections.split(',')
        )

    def job_selector(self, user_jobs, field_index):
        self.job = st.selectbox(
            'Вид работы:',
            key=f'Вид работы_{field_index}',
            options=user_jobs['Вид работы']
        )

    def comment_input(self, field_index):
        self.comment = st.text_area(
            'Описание работы:',
            key=f'Примечание_{field_index}',
            placeholder='...',
            height=129
        )

    def correction_selector(self, field_index):
        self.correction = st.selectbox(
            'Коррект-ка:',
            key=f'Корректировка_{field_index}',
            options=('Нет', 'Да')
        )
        match self.correction:
            case 'Нет':
                self.correction = 0
            case _:
                self.correction = 1

    def percentage_selector(self, field_index):
        self.percentage = st.slider(
            'Процент:',
            0, 100, 0,
            step=5,
            key=f'Процент_{field_index}'
        )

    def hours_selector(self, field_index):
        self.hours = st.number_input(
            'Часы:',
            key=f'Часы_{field_index}',
            min_value=0.0,
            max_value=8.0,
            step=0.5,
            format='%a'
        )

    def date_selector(self, field_index):
        self.date = st.date_input(
            'Дата отчета:',
            key=f'Дата отчета_{field_index}'
        )

    def get_group_by_job(self):
        group = self.user_jobs[self.user_jobs['Вид работы'] == self.job]['Отдел'].iloc[0]
        return group

    def get_project_id(self):
        project_id = self.projects[self.projects['Human_name'] == self.project_name]['ID'].iloc[0]
        return project_id

    def get_job_by_project(self):
        match self.project_name:
            case '000_Без проекта':
                return self.job
            case _:
                project_type = self.projects[self.projects['Human_name'] == self.project_name]['Тип'].iloc[0]
                job_by_project = f'{self.job}_{project_type}'
                return job_by_project

    def container(self, user_jobs, field_index):
        st.markdown(f'##### Поле {field_index + 1}')
        self.project_selector(field_index)
        col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
        with col1:
            self.section_selector(field_index)
            self.job_selector(user_jobs, field_index)
        with col2:
            self.correction_selector(field_index)
            self.percentage_selector(field_index)
        with col3:
            self.hours_selector(field_index)
            self.date_selector(field_index)
        with col4:
            self.comment_input(field_index)

        st.write("""---""")
        group = self.get_group_by_job()
        project_id = self.get_project_id()
        job_by_project = self.get_job_by_project()
        field_data = [
            self.resource_name,
            group,
            project_id,
            self.section,
            job_by_project,
            self.correction,
            self.hours,
            self.percentage,
            self.date.strftime('%d.%m.%Y'),
            datetime.today().strftime('%d.%m.%Y'),
            self.comment
        ]
        # field_data = {
        #     'date': self.date,
        #     'hours': self.hours,
        #     'percentage': self.percentage,
        #     'correction': self.correction,
        #     'comment': self.comment,
        #     'project': self.project_name,
        #     'section': self.section,
        #     'job': self.job
        # }
        self.collected_data.append(field_data)

    def data_to_dataframe(self):
        self.data_dataframe = pd.DataFrame(data=self.collected_data)

    def save_report(self):
        self.data_dataframe.to_csv(
            self.file_path,
            header=False,
            mode='a',
            encoding='utf-8-sig',
            index=False
        )

    def form(self, user_jobs):
        for i in range(int(self.field_number)):
            self.container(user_jobs, i)
        unfilled = [i for i in self.collected_data if i[6] == 0 or i[10] == '']
        match len(unfilled):
            case 0:
                placeholder = st.empty()
                button = placeholder.button(
                    'Отправить',
                    disabled=False,
                    key='1'
                )
                if button:
                    self.data_to_dataframe()
                    self.save_report()
                    placeholder.button(
                        'Отправить',
                        disabled=True,
                        key='2'
                    )
                    st.success('Отчет отправлен')
            case _:
                st.warning('Заполните **Часы** и **Описание работы**')
