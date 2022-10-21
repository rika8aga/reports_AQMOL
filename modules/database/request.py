import sqlalchemy
from sqlalchemy import create_engine, select, delete, update
from sqlalchemy.orm import sessionmaker
from sql_classes import UserSQL, ProjectSQL

if __name__ == '__main__':
    engine = create_engine(
        "sqlite:////Users/rika_aga/Library/CloudStorage/OneDrive-Личная/python_projects/reports_AQMOL/data/test_10.db",
        echo=True
    )
    connection = engine.connect()

    query = f'ALTER TABLE users ADD image TEXT'
    connection.execute(query)


