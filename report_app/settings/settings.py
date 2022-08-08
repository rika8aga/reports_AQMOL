from glob import glob
import pandas as pd
from dataclasses import dataclass
import streamlit as st
import pickle
from io import BytesIO
import streamlit_authenticator as stauth
import locale
from report_app.to_import import resources

locale.setlocale(locale.LC_ALL, "ru")


@dataclass
class GroupAndProject:
    project: str
    group_code: str
    level: str


@dataclass
class User:
    status: bool
    name: str
    level: str
    group: str
    group_code: int
    username: str
    code: str


def to_xlsx(df):
    output = df.sort_values(by='ИТОГО', ascending=True)
    output.columns = output.columns.map(
        lambda x: '.'.join(str(x).split(' ')[0].split('-')[::-1])
    )
    output = output.style.applymap(
        lambda x: 'color:#182A3E;font-weight:bold;'
        if x != 0 else 'opacity: 20%;'
    ).format('{:,.1f}')
    output.highlight_max(axis=0)
    binary_output = BytesIO()
    output.to_excel(binary_output, encoding='utf-8-sig')
    return binary_output


def style_to_xlsx(df):
    binary_output = BytesIO()
    df.to_excel(binary_output, encoding='utf-8-sig')
    return binary_output


def block_from_str(string):
    block = string.split('/', 1)[1][0]
    return f'Блок {block}'


def group_from_string(string):
    lst = string.split('>')
    grp = lst[2].split('_')[4][:2]
    name = lst[6]
    return [grp, name]


def id_by_string(string):
    el_id = string.split(':')[1]
    return el_id


@st.experimental_memo(show_spinner=False)
def collision_report():
    directory = r'R:\Отчеты\*.html'
    files = glob(directory)
    collision_reports = pd.DataFrame()
    for file in files:
        tables = pd.read_html(file)

        file = file.split('\\')[-1]
        project_name = file.split('.')[0]

        output = pd.DataFrame()
        for i, table in enumerate(tables):
            if i % 2 != 0:
                info = tables[i + 1]
                if len(info) > 2:
                    name = table.iloc[0, 0]
                    info = tables[i + 1].drop(tables[i + 1].index[:2])
                    info.reset_index(drop=True, inplace=True)
                    info.rename(columns={0: 'Not 0'}, inplace=True)
                    names = [name] * len(info)
                    names = pd.Series(names, dtype='object', )
                    new_table = pd.concat([names, info], axis=1)
                    output = pd.concat([output, new_table], ignore_index=True)
        output.dropna(how='all', inplace=True)

        output = output[[0, 2, 6, 8, 12, 13, 14, 16, 17, 18]]
        mapping = {
            0: 'Наименование конфликта',
            2: 'Номер конфликта',
            6: 'Раположение',
            8: 'Дата отчета',
            12: 'ID_1',
            13: 'Уровень_1',
            14: 'Раздел_1',
            16: 'ID_2',
            17: 'Уровень_2',
            18: 'Раздел_2'
        }
        output.rename(columns=mapping, inplace=True)

        output['Блок'] = output['Раположение'].apply(block_from_str)
        output['Наименование_1'] = output['Раздел_1'].apply(lambda x: group_from_string(x)[1])
        output['Наименование_2'] = output['Раздел_2'].apply(lambda x: group_from_string(x)[1])
        output['Раздел_1'] = output['Раздел_1'].apply(lambda x: group_from_string(x)[0])
        output['Раздел_2'] = output['Раздел_2'].apply(lambda x: group_from_string(x)[0])
        output['ID_1'] = output['ID_1'].apply(id_by_string)
        output['ID_2'] = output['ID_2'].apply(id_by_string)
        project_names = [project_name] * len(output)
        project_names = pd.Series(project_names)
        output = pd.concat([project_names, output], axis=1)
        output.rename(columns={0: 'Проект'}, inplace=True)
        collision_reports = pd.concat([collision_reports, output], ignore_index=True)
        collision_reports['Дата отчета'] = pd.to_datetime(collision_reports['Дата отчета']).dt.date
    return collision_reports


@st.experimental_memo
def get_pass(file):
    with open(file, "rb") as file:
        hashed_passwords = pickle.load(file)
    return hashed_passwords


def loging():
    resources_df = resources()
    names = resources_df['Ф.И.О.']
    usernames = resources_df['username']
    file = r"Z:\11. Bim-отдел\data\new_passes.pkl"
    hashed_passwords = get_pass(file)
    form = stauth.Authenticate(
        names,
        usernames,
        hashed_passwords, 'authen', 'authen_key', cookie_expiry_days=30
    )
    name, authentication_status, username = form.login('Введите логин и пароль', 'main')
    output = {'name': name, 'status': authentication_status, 'username': username, 'form': form}
    return output


def user():
    resources_df = resources()
    login = loging()
    name = login['name']
    authentication_status = login['status']
    username = login['username']
    filtered = resources_df[resources_df['Ф.И.О.'] == name]
    try:
        level = filtered['level'].iloc[0]
        code = filtered['Code'].iloc[0]
        if len(filtered) == 1:
            group = filtered['Отдел'].iloc[0]
            group_code = filtered['group_code'].iloc[0]
        else:
            group = filtered['Отдел'].to_list()
            group_code = filtered['group_code'].to_list()

        user_class = User(
            name=name,
            username=username,
            status=authentication_status,
            level=level,
            group=group,
            group_code=group_code,
            code=code
        )
        output = {'user': user_class, 'form': login['form']}
    except IndexError:
        output = {'user': '', 'form': login['form']}
    return output
