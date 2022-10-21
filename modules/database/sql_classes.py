import datetime
import sqlalchemy.orm
from sqlalchemy import Column, String, ForeignKey, create_engine, PrimaryKeyConstraint, Integer, Date, Boolean, update
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Vacation(Base):
    __tablename__ = 'vacation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date_start = Column(Date, default=datetime.date.today())
    date_end = Column(Date, default=datetime.date.today())


class ProjectSQL(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True)
    cipher_pilot = Column(String)
    type = Column(String)
    name = Column(String)
    status = Column(String)
    chief = Column(Integer, ForeignKey('users.id'))
    cipher_fin = Column(String)
    sections = Column(String, default='Нет')
    date_start = Column(Date, default=datetime.date.today())
    date_end = Column(Date, default=datetime.date.today())
    expert_start = Column(Date, default=datetime.date.today())
    expert_end = Column(Date, default=datetime.date.today())
    information = Column(String)
    users = relationship('UserSQL', secondary='user_projects')
    plan_AS = Column(String, default='0')
    plan_KJ = Column(String, default='0')
    plan_OV = Column(String, default='0')
    plan_VK = Column(String, default='0')
    plan_EM = Column(String, default='0')
    plan_SS = Column(String, default='0')

    def __repr__(self):
        return f'Project(code = {self.code}, name = {self.name})'


class UserProject(Base):
    __tablename__ = 'user_projects'
    __table_args__ = (PrimaryKeyConstraint('user_id', 'project_id'),)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)


class RoleSQL(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    function = Column(String)
    level = Column(String)
    users = relationship('UserSQL', secondary='users_roles')

    def __repr__(self):
        return f'Resource(id = {self.id}, function = {self.function}, level = {self.level})'


class UserSQL(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(String)
    code = Column(String, unique=True)
    username = Column(String)
    name = Column(String)
    password = Column(String, default='12345678')
    salary = Column(Integer)
    is_active = Column(Boolean, default=True)
    group = relationship('GroupSQL', secondary='users_groups', overlaps='users')
    role = relationship('RoleSQL', secondary='users_roles', overlaps='users')
    projects = relationship('ProjectSQL', secondary='user_projects', overlaps='users')

    def __repr__(self):
        return f'User(id = {self.id}, code = {self.code}, username = {self.username})'


class GroupSQL(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True)
    group_name = Column(String)
    users = relationship('UserSQL', secondary='users_groups')

    def __repr__(self):
        return f'Group(code = {self.id}, group = {self.group_name})'


class UserGroup(Base):
    __tablename__ = 'users_groups'
    __table_args__ = (PrimaryKeyConstraint('user_id', 'group_id'),)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=False, index=True)


class UserRole(Base):
    __tablename__ = 'users_roles'
    __table_args__ = (PrimaryKeyConstraint('user_id', 'role_id'),)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True)


engine = create_engine(
    "sqlite:///C:\\Users\\zharmakin\\OneDrive\\python_projects\\reports_AQMOL\\data\\test_10.db",
    echo=True
)

# Base.metadata.create_all(engine)
# Session = sessionmaker()
# Session.configure(bind=engine)
# session: sqlalchemy.orm.Session = Session()

# if __name__ == '__main__':
#     data = pd.read_excel(
#         '/Users/rika_aga/Library/CloudStorage/OneDrive-Личная/python_projects/reports_AQMOL/data/resources.xlsx',
#         dtype={'code': str, 'username': str, 'password': str}
#     )
#
#     for i, row in data.iterrows():
#         group = session.query(Group).filter_by(group_name=row['group_name']).scalar()
#         if not group:
#             group = Group(group_name=row['group_name'], id=row['group_code'])
#             session.add(group)
#         role = session.query(Role).filter_by(function=row['function']).scalar()
#         if not role:
#             role = Role(function=row['function'], level=row['level'])
#             session.add(role)
#         user = session.query(User).filter_by(name=row['username']).scalar()
#         if not user:
#             user = User(id=row['code'], username=row['username'], password=row['password'])
#         session.add(user)
#         user.role.append(role)
#         user.group.append(group)
#         session.commit()
if __name__ == '__main__':
    Session = sessionmaker()
    Session.configure(bind=engine)
    session: sqlalchemy.orm.Session = Session()
    stmt = update(ProjectSQL).where(ProjectSQL.id == 113).values(code='1-212')
    session.execute(stmt)
    session.commit()
    session.close()
