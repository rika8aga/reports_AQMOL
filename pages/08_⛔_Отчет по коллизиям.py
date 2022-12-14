import streamlit as st
import pandas as pd
import numpy as np
from modules import collision_report
from modules.plots import CollisionPlot

st.set_page_config(
    page_title='Отчет по коллизиям',
    page_icon=':triangular_ruler:',
    layout='wide'
)

st.markdown("# Отчет по коллизиям")

with st.spinner('Загрузка данных'):
    collisions = collision_report()
report_date = st.sidebar.selectbox(
    'Дата отчета',
    options=collisions['Дата отчета'].sort_values(ascending=False).unique()
)
projects = st.sidebar.selectbox(
    "Проект:",
    options=collisions['Проект'].sort_values().unique()
)
by_date = collisions[collisions['Дата отчета'] == report_date]
by_project = by_date[by_date['Проект'] == projects]

with st.expander('Общий отчет'):
    st.markdown(f'###### Общее число коллизий в проекте: {len(by_project)}')
    excel_pivot = pd.pivot_table(
        by_project,
        index='Наименование конфликта',
        columns='Блок',
        values='Номер конфликта',
        aggfunc=np.count_nonzero,
        margins=True,
        margins_name='Всего',
        fill_value=0
    )
    st.dataframe(excel_pivot, use_container_width=True)

with st.expander('Диаграммы'):
    collision_plot = CollisionPlot(projects)
    collision_plot.show_plots()

group = st.selectbox(
    'Раздел',
    options=[
        'Архитектурные решения',
        'Контрукции железобетонные',
        'ОВиК',
        'Водоснабжение и канализация',
        'Электрические сети',
        'Слаботочные сети'
    ]
)
match group:
    case 'Архитектурные решения':
        group = 'AS'
    case 'Контрукции железобетонные':
        group = 'KJ'
    case 'ОВиК':
        group = 'OV'
    case 'Водоснабжение и канализация':
        group = 'VK'
    case 'Электрические сети':
        group = 'EM'
    case 'Слаботочные сети':
        group = 'SS'

section = st.selectbox(
    'Блок',
    options=by_project['Блок'].sort_values().unique()
)
grouped = by_project[(by_project['Раздел_1'] == group) | (by_project['Раздел_2'] == group)]
blocked = grouped[grouped['Блок'] == section]
for name in blocked['Наименование конфликта'].unique():
    st.markdown('___')
    to_display = blocked[blocked['Наименование конфликта'] == name][[
        'Номер конфликта',
        'ID_1',
        'Наименование_1',
        'ID_2',
        'Наименование_2'
    ]].sort_values(by='Номер конфликта')
    st.markdown(f'##### {name} | Кол-во конфликтов: {len(to_display)}')

    to_display.reset_index(drop=True, inplace=True)
    to_display.index = to_display.index + 1
    with st.expander('Таблица'):
        st.dataframe(to_display, use_container_width=True)

if st.button('Обновить отчет'):
    st.experimental_memo.clear()
    st.session_state['collisions'] = collision_report()
