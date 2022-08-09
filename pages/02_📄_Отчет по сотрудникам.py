import streamlit as st
from datetime import date
from modules.settings import user
from modules.export import to_xlsx
from modules.levels import Levels
from modules.filtering import by_resource, by_date0
from modules.plots import resource_pivot, resource_plot
from modules.to_import import Reports, cached_report, resources
from modules.selector import date_input

st.set_page_config(
    page_title='Отчет по сотрудникам',
    page_icon=':chart_with_upwards_trend:',
    layout='wide'
)
try:
    user_func = user()
    user = user_func['user']
    st.sidebar.markdown(f'### {user.name}')
    st.sidebar.markdown(f'##### {user.group}')
    user_func['form'].logout('Выйти', 'sidebar')
    if user.status:
        col1, col2 = st.columns([3, 1])
        reports = Reports()
        with col1:
            match user.level:
                case Levels.admin:
                    st.markdown("# Отчет по сотрудникам")
                    report = cached_report('all')
                    employer = st.selectbox(
                        'Ф.И.О',
                        options=report['Ф.И.О.'].unique()
                    )
                    resources = resources()
                    user_code = resources[resources['Ф.И.О.'] == employer]['Code'].iloc[0]
                    st.write(user_code)
                case Levels.leader:
                    st.markdown("# Отчет по сотрудникам")
                    reports.get_report(f'{user.group_code}-')
                    report = reports.report
                    employer = st.selectbox(
                        'Ф.И.О',
                        options=report['Ф.И.О.'].unique()
                    )
                case Levels.worker:
                    st.markdown("# Отчет по сотрудникам")
                    employer = st.text_input(
                        'Ф.И.О',
                        value=user.name,
                        disabled=True
                    )
                    reports.get_report(user.code)
                    report = reports.report
        with col2:
            st.write('###')
            st.write('##')
            st.write('##')
            dates = date_input(-5)
        try:
            by_resource = by_resource(report, employer)
            report_selection = by_date0(by_resource, dates)
            indexes = st.multiselect(
                label='Группировать по:',
                options=['Проект', 'Блок', 'Вид работы', 'Описание работы'],
                default=['Проект', 'Блок', 'Вид работы']
            )
            units = st.sidebar.radio('Показать трудозатраты...', ('в часах', 'в днях', 'в процентах'))
            if indexes:
                table = resource_pivot(report_selection, indexes, units)
                if table is not None:
                    st.table(table)
                    st.download_button(
                        'Экспорт таблицы',
                        to_xlsx(user.name, dates, report_selection, units),
                        file_name=f'{user.name}_{date.today()}.xlsx'
                    )
                resource_plot(report_selection, indexes[0])
                if st.button('Обновить данные'):
                    st.experimental_memo.clear()
                    st.experimental_rerun()
        except NameError:
            pass
    else:
        st.info('Необходимо авторизоваться на [Главной странице](http://192.168.10.123:8501/Главная_страница)')
except AttributeError:
    pass
