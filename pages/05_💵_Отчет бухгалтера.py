import streamlit as st
from modules.export import accountant_report_xlsx
from modules.settings import user
from modules.selector import date_input
from modules.to_import import cashed_accountant_report, Report1C
from modules.filtering import by_date0


st.set_page_config(
    page_title='Отчет Бухгалтера',
    page_icon=":space_invader:",
    layout='wide'
)
st.markdown('# Отчет Бухгалтера')

user_func = user()
user = user_func['user']
user_func['form'].logout('Выйти', 'sidebar')

try:
    match user.status:
        case False | None:
            st.warning('Для доступа к данным необходима авторизация')
        case True:
            match user.level:
                case 'АДМ':
                    dates = date_input('last_month')
                    with st.spinner('Загрузка данных'):
                        report = cashed_accountant_report()
                    report_selection = by_date0(report, dates)
                    report_1C = Report1C()
                    report_1C.create_report(report_selection)
                    report_1C.get_pivot_report(dates)
                    report_df = report_1C.pivot_report
                    st.dataframe(report_df)
                    st.download_button(
                        'Экспорт таблицы',
                        accountant_report_xlsx(report_df),
                        file_name=f'отчет_{dates[1]}.xlsx'
                    )
                case _:
                    st.warning('Доступ ограничен')
except AttributeError:
    st.warning('Необходимо авторизоваться')
