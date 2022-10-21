import plotly_express as px
import pandas as pd
import numpy as np
from ..settings import collision_report
import streamlit as st


class CollisionPlot:
    def __init__(self, project: str):
        self.plot_by_group = None
        self.plot_overall = None
        self.grouped_table = None
        self.pivot_table = None
        self.dataframe: pd.DataFrame = collision_report()
        self.project_data: pd.DataFrame = self.dataframe[self.dataframe['Проект'] == project].copy(deep=True)

    def get_by_group(self):
        for i in ['AS', 'KJ', 'OV', 'VK', 'EM', 'SS']:
            self.project_data[i] = self.project_data.apply(
                lambda x: -1 if i == x['Раздел_1'] or i == x['Раздел_2'] else 0,
                axis=1
            )

    def get_pivot(self):
        self.pivot_table = pd.pivot_table(
            data=self.project_data,
            index=['Дата отчета'],
            values=['AS', 'KJ', 'OV', 'VK', 'EM', 'SS'],
            aggfunc=np.sum
        )

    def get_plot_overall(self):
        self.pivot_table['Итого'] = self.pivot_table.sum(axis=1)
        self.plot_overall = px.line(
            title='Общее колличество',
            data_frame=self.pivot_table,
            x=self.pivot_table.index,
            y='Итого',
            template='seaborn',
            markers=True,
            text='Итого'
        )
        self.plot_overall.update_traces(
            textposition='top center'
        )

    def create_plot_by_group(self):
        self.plot_by_group = px.line(
            title='По разделам',
            data_frame=self.pivot_table,
            x=self.pivot_table.index,
            y=self.pivot_table.columns,
            template='seaborn',
            markers=True,
            text='value'
        )
        self.plot_by_group.update_layout(
            yaxis_title='Количество'
        )
        self.plot_by_group.update_traces(
            textposition='top center'
        )

    def show_plots(self):
        self.get_by_group()
        self.get_pivot()
        self.create_plot_by_group()
        self.get_plot_overall()
        st.plotly_chart(self.plot_overall, use_container_width=True)
        st.plotly_chart(self.plot_by_group, use_container_width=True)
