from pytest_mock_resources import create_postgres_fixture
from sqlalchemy.schema import CreateSchema

def session_fn(session):
    session.execute(CreateSchema('test_schema'))

session = create_postgres_fixture(session_fn, session=True)
