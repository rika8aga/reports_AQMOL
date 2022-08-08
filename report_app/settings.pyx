from glob import glob
from datetime import datetime
import pandas as pd
import streamlit as st
import pickle


def to_month(date):
    try:
        day = datetime.strptime(date, '%d.%m.%Y')
        month = day.strftime("%B")
        number = day.strftime("%m")
    except TypeError:
        month = 'error'
        number = 'error'
    return [month, number]


@st.experimental_memo
def reports_by_dir(lst: list):
    headers = ['Ф.И.О.',
               'Отдел',
               'Проект',
               'Блок',
               'Вид работы',
               'Корректировка',
               'Часы',
               'Процент выполнения',
               'Дата отчета',
               'Отчет сдан',
               'Примечание']
    report = pd.DataFrame(columns=headers)
    for i in lst:
        to_add = pd.read_csv(i, header=None, names=headers, encoding='utf-8-sig')
        report = pd.concat([report, to_add], ignore_index=True)
    report['Часы'] = report['Часы'].astype('float')
    report['Месяц'] = report['Дата отчета'].apply(lambda x: to_month(x)[0])
    report['Номер'] = report['Дата отчета'].apply(lambda x: to_month(x)[1])
    report = report[report['Часы'] != 0]
    report['Дата отчета'] = pd.to_datetime(report['Дата отчета'], dayfirst=True)
    return report


def report_by_user(user_code: str):
    files = glob(f'Z:\\11. Bim-отдел\\reports\\*{user_code}*.csv')
    return reports_by_dir(files)


def report_by_group(user_code: str):
    files = glob(f'Z:\\11. Bim-отдел\\reports\\*{user_code[:2]}*.csv')
    return reports_by_dir(files)


def key_word(string, word, grouping: bool):
    output = 'Другое'
    word = word.replace(' ', '')
    if ',' in word:
        keys = word.split(',')
        for i in keys:
            if f" {i.lower()} " in string.lower():
                if grouping:
                    output = 'Содержит ключевое слово'
                else:
                    output = string
    else:
        if f" {word.lower()} " in (' ' + string.lower() + ' '):
            if grouping:
                output = 'Содержит ключевое слово'
            else:
                output = string
    return output


@st.experimental_memo
def get_pass(file):
    with open(file, "rb") as file:
        hashed_passwords = pickle.load(file)
    return hashed_passwords
