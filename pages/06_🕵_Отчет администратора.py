import streamlit as st
import pandas as pd
from datetime import datetime
from glob import glob

st.set_page_config(
    page_title='Отчет администратора',
    page_icon=":space_invader:",
    layout='wide'
)
st.markdown('# Отчет администратора')


try:
    user = st.session_state['new_user']
    if user.level in ['АДМ']:
        directory = r'Z:\11. Bim-отдел\reports\*.*'
        files = glob(directory)
        report = reports_by_dir(files)
        resources = st.session_state['to_login']['Ф.И.О.']
        un_send = resources
        send = pd.DataFrame(columns=['Ф.И.О.', 'Часы'])
        date = st.date_input(
            'Дата отчета'
        )

        date = datetime.combine(date, datetime.min.time())
        report_by_date = report[pd.to_datetime(
            report['Дата отчета'], format='%d.%m.%Y') == date]
        for i, name in resources.iteritems():
            isSend = report_by_date[report_by_date['Ф.И.О.'] == name]
            if not isSend.empty:
                un_send = un_send.drop([i])
                send = pd.concat([send, isSend[['Ф.И.О.', 'Часы']]])

        un_send = un_send.reset_index(drop=True)
        un_send.index = un_send.index + 1
        st.markdown(f'Не сдали отчет {len(un_send)} человек(а):')
        with st.expander('Таблица 1'):
            st.table(un_send)

        send = send.groupby('Ф.И.О.').sum()
        # send = send.reset_index(drop=True)
        # send.index = send.index + 1
        st.markdown(f'Cдали отчет {len(send)} человек(а)')
        with st.expander('Таблица 2'):
            st.table(send)

    else:
        st.warning('Доступ ограничен')
except KeyError:
    st.info(
        'Перейдите на [Главную страницу](http://192.168.10.123:8501/Главная_страница)')
