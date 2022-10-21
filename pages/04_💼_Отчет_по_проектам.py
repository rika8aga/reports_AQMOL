import streamlit as st
from modules import user
from modules.project_report import ProjectSelector, PeriodSelector, ProjectInfo

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
            project_selector = ProjectSelector()
            period_selector = PeriodSelector()
            project_info = ProjectInfo(
                project_codes=project_selector.project_codes,
                date_start=period_selector.date_start,
                date_end=period_selector.date_end,
                columns=period_selector.columns
            )
            project_info.create_filter()
            project_info.create_pivot()
        case _:
            st.warning('Доступ ограничен')
except AttributeError:
    pass
