import streamlit as st
from datetime import datetime
import pandas as pd
import plotly_express as px
import numpy as np
from report_app.settings import to_xlsx, user
from report_app.to_import import cached_expenses

st.set_page_config(
    page_title='Отчет по проектам',
    page_icon=':straight_ruler:',
    layout='wide'
)
st.markdown("# Отчет по проектам")

try:
    user_func = user()
    user = user_func['user']
    user_func['form'].logout('Выйти', 'sidebar')
    match user.level:
        case 'НО' | 'ГИП' | 'АДМ':
            report = cached_expenses('all')
            with st.sidebar:
                choose_index = st.radio(
                    '', ('По отделам', 'По видам работ')
                )

                choose_time = st.radio(
                    '',
                    ('Отчет за период', 'Отчет за месяц')
                )

                values = st.radio(
                    '',
                    ('Отчет по трудозатратам', 'Отчет по расходам')
                )

            projects = st.selectbox(
                'Проекты',
                options=report['Проект'].sort_values().unique()
            )

            match choose_index:
                case 'По отделам':
                    index_col = 'Отдел'
                case _:
                    index_col = 'Вид работы'
            match choose_time:
                case 'Отчет за период':
                    col1, col2 = st.columns([1, 1])
                    with col2:
                        date_end = st.date_input('Окончание периода')
                    with col1:
                        default = np.busday_offset(date_end, -4, roll='forward').astype(datetime)
                        date_start = st.date_input('Начало периода', default)

                    date_start = np.datetime64(date_start)
                    date_end = np.datetime64(date_end)
                    period = '`Дата отчета` <= @date_end & `Дата отчета` >= @date_start'
                    pivot_columns = 'Дата отчета'
                case _:
                    report_months = report[['Месяц', 'Номер']].sort_values(by='Номер')
                    month = st.selectbox(
                        'Месяц',
                        options=report['Месяц'].unique()
                    )
                    period = 'Месяц == @month'
                    pivot_columns = 'Месяц'

            match values:
                case 'Отчет по трудозатратам':
                    value = 'Часы'
                case _:
                    value = 'Расходы'

            by_project = report[report['Проект'] == projects]
            report_selection = by_project.query(period)
            try:
                table = pd.pivot_table(
                    report_selection,
                    values=value,
                    index=index_col,
                    columns=pivot_columns,
                    aggfunc=np.sum,
                    margins=True,
                    margins_name='ИТОГО',
                    dropna=False,
                    fill_value=0
                )

                table.sort_values(by='ИТОГО', inplace=True, ascending=False)
                total = table.loc['ИТОГО', 'ИТОГО']
                table_drop = table.drop(['ИТОГО'])
                table_drop.columns = table_drop.columns.map(
                    lambda x: '.'.join(str(x).split(' ')[0].split('-')[::-1])
                )
                styled_table = table_drop.style.applymap(
                    lambda x: 'color:#182A3E;font-weight:bold;'
                    if x != 0 else 'opacity: 20%;'
                ).format('{:,.1f}')
                styled_table.highlight_max(axis=0)
                st.table(styled_table)

                st.markdown(f'##### Итого по проекту за период: {"{:,.2f}".format(total).replace(",", " ")}')

                to_fig = table_drop.head(10)
                fig = px.bar(
                    to_fig,
                    x="ИТОГО",
                    y=to_fig.index,
                    orientation='h',
                    labels={
                        index_col: '',
                        'ИТОГО': value
                    },
                    text_auto=',.1f',
                    color=to_fig.index
                )
                fig.update_layout(
                    barmode='stack',
                    yaxis={'categoryorder': 'total ascending'},
                    showlegend=False,
                    plot_bgcolor='#FFFFFF',
                    font=dict(family='Century Gothic',
                              size=15)
                )
                fig.update_traces(textfont_size=15, textposition="outside", cliponaxis=False, textfont={'family': 'Century Gothic, Bold'})
                st.plotly_chart(fig, use_container_width=True)

                st.download_button(
                    'Экспорт таблицы',
                    to_xlsx(table),
                    file_name=f'По проекту {projects}.xlsx'
                )
            except ValueError:
                st.info('Нет данных за данный период')
            if st.button('Обновить данные'):
                st.experimental_memo.clear()
                st.info('Обновите страницу')
        case _:
            st.warning('Доступ ограничен')
except AttributeError:
    pass
