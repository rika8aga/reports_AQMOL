import pandas as pd
from datetime import datetime, date
import numpy as np
import streamlit as st


@st.experimental_memo(show_spinner=False)
def by_resource(df: pd.DataFrame, resource_name: str):
    output_df = df[df['Ф.И.О.'] == resource_name]
    return output_df


def by_date(df: pd.DataFrame, date_start: datetime.date, date_end: datetime.date):
    date_start = np.datetime64(date_start)
    date_end = np.datetime64(date_end)
    output_df = df.query('`Дата отчета` <= @date_end & `Дата отчета` >= @date_start').sort_values(by='Дата отчета')
    return output_df


def project_output(df: pd.DataFrame, projects_name: str):
    filtered = df[df['Human_name'] == projects_name]
    project_code = filtered['Название проекта'].iloc[0]
    project_type = filtered['Тип'].iloc[0]
    project_id = filtered['ID'].iloc[0]
    dict_output = {
        'code': project_code,
        'type': project_type,
        'id': project_id
    }
    return dict_output


def by_group(df: pd.DataFrame, group_name: str):
    output_df = df[df['Отдел'] == group_name]
    return output_df


def by_date0(df: pd.DataFrame, diapason: tuple):
    match diapason:
        case date_start, date_end:
            date_start = np.datetime64(date_start)
            date_end = np.datetime64(date_end)
        case (date_start,):
            date_start = np.datetime64(date_start)
            date_end = np.datetime64(date.today())
    output_df = df.query('`Дата отчета` <= @date_end & `Дата отчета` >= @date_start').sort_values(by='Дата отчета')
    output_df.sort_values(by='Ф.И.О.', inplace=True)
    output_df.reset_index(drop=True, inplace=True)
    return output_df
