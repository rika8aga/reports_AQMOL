import streamlit as st
import pandas as pd
import numpy as np
import plotly_express as px
import locale

locale.setlocale(locale.LC_ALL, "ru")


def pivot_table(df, index, unit_type):
    match unit_type:
        case 'в часах' | 'в днях':
            values = 'Часы'
            agg_func = np.sum
        case _:
            values = 'Процент выполнения'
            agg_func = max

    pivot_tabel = pd.pivot_table(
        df,
        values=values,
        index=index,
        columns='Дата отчета',
        aggfunc=agg_func,
        margins=True,
        margins_name='ИТОГО',
        dropna=False,
        fill_value=0,
        sort=True
    )
    pivot_tabel.reset_index(inplace=True)
    pivot_tabel.dropna(inplace=True)
    pivot_tabel.reset_index(inplace=True, drop=True)
    pivot_tabel.index += 1
    return pivot_tabel


def resource_plot(df: pd.DataFrame, indexes: str):
    match len(df):
        case 0:
            pass
        case _:
            by_date_chart = px.bar(
                data_frame=df,
                x='Дата отчета',
                y='Часы',
                color=indexes,
                labels={
                    'x': 'Дата',
                    'Часы': 'Часы работы'
                },
                text_auto='d'
            )
            by_date_chart.update_xaxes(
                dtick="d1",
                tickformat="%d.%m.%Y")
            by_date_chart.update_layout(
                font=dict(
                    family='Century Gothic',
                    size=15
                ),
                plot_bgcolor='#FFFFFF'
            )
            by_date_chart.update_traces(
                textfont_size=15,
                textposition='outside',
                cliponaxis=False,
                textfont={'family': 'Century Gothic, Bold'},
                textangle=0
            )
            by_date_chart.add_hline(y=8, line_width=3, line_dash="dash", line_color='#FC1781')
            by_date_chart.add_hline(y=4, line_width=2, line_dash="dash", line_color='#FD73B3')
            return st.plotly_chart(by_date_chart, use_container_width=True)


def float_format(value, unit_type):
    match value, unit_type:
        case float() | int(), 'в часах':
            return f'{value:.1f}'
        case float() | int(), 'в днях':
            return f'{value / 8:.3f}'
        case str(), str():
            return f'{value}'
        case float() | int(), 'в процентах':
            return f'{value:.1f}%'
        case float() | int(), 'в деньгах':
            return f'{locale.format_string("%10.2f", value, grouping=True)}'


def value_format(value):
    match value:
        case float() | int() if value != 0:
            return 'color: #182A3E; background-color: #DAF5E9; font-weight: bold;'
        case float() | int() if value == 0:
            return 'opacity: 20%;'


def resource_pivot(df: pd.DataFrame, indexes: list, unit_type: str):
    try:
        table = pivot_table(df, indexes, unit_type)
        table.columns = table.columns.map(
            lambda x: '.'.join(str(x).split(' ')[0].split('-')[::-1])
        )
        styled_table = table.style.format(lambda x: float_format(x, unit_type))
        styled_table = styled_table.applymap(
            value_format
        )
        return styled_table
    except ValueError:
        return st.write('Не данных за период')


def group_chart(df_pivot: pd.DataFrame.pivot_table):
    by_project_chart = px.bar(
        df_pivot,
        x='ИТОГО',
        y=df_pivot.index,
        orientation='h',
        barmode='relative',
        labels={
            'Проект': '',
            'ИТОГО': 'Трудозатраты'
        },
        text_auto='.1f'
    )
    by_project_chart.update_layout(
        barmode='stack',
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        plot_bgcolor='#FFFFFF',
        font=dict(family='Century Gothic',
                  size=15)
    )
    by_project_chart.update_traces(textfont_size=15, textangle=0, textposition="outside", cliponaxis=False)
    return st.plotly_chart(by_project_chart, use_container_width=True)
