import pytest
from sqlalchemy import Column, types
from sqlalchemy.orm import declarative_base

from sqlalchemy_auditlog.ddl import install_audit_triggers
from sqlalchemy_auditlog.declarative import audit
from sqlalchemy.schema import CreateSchema


@pytest.mark.parametrize("schema", [None, "test_schema"])
def test_it_creates_an_audit_log_model(session, schema):
    Base = declarative_base()

    @audit
    class Foo(Base):
        __tablename__ = "foo"
        __table_args__ = {"schema": schema}

        id = Column(types.Integer(), autoincrement=True, primary_key=True)
        name = Column(types.String())

    Base.metadata.create_all(bind=session.connection())

    assert Foo.__audit_cls__.__name__ == "FooAudit"
    assert Foo.__audit_cls__.__table__.name == "foo_audit"


@pytest.mark.parametrize("schema", [None, "test_schema"])
def test_it_creates_rows_in_audit_table_for_inserts(session, schema):
    Base = declarative_base()

    @audit
    class Foo(Base):
        __tablename__ = "foo"
        __table_args__ = {"schema": schema}

        id = Column(types.Integer(), autoincrement=True, primary_key=True)
        name = Column(types.String())

    Base.metadata.create_all(bind=session.connection())
    install_audit_triggers(Base.metadata, session.connection())

    foo = Foo(name="foo")
    session.add(foo)
    session.commit()

    audits = session.query(Foo.__audit_cls__).all()
    assert len(audits) == 1
    assert audits[0].audit_operation == "I"
    assert audits[0].audit_operation_timestamp is not None
    assert audits[0].id == foo.id
    assert audits[0].name == foo.name


@pytest.mark.parametrize("schema", [None, "test_schema"])
def test_it_creates_rows_in_audit_table_for_updates(session, schema):
    Base = declarative_base()

    @audit
    class Foo(Base):
        __tablename__ = "foo"
        __table_args__ = {"schema": schema}

        id = Column(types.Integer(), autoincrement=True, primary_key=True)
        name = Column(types.String())

    Base.metadata.create_all(bind=session.connection())
    install_audit_triggers(Base.metadata, session.connection())

    foo = Foo(name="foo")
    session.add(foo)
    session.commit()

    foo.name = "bar"
    session.commit()

    audits = session.query(Foo.__audit_cls__).all()
    assert len(audits) == 2
    assert audits[0].audit_operation == "I"
    assert audits[0].audit_operation_timestamp is not None
    assert audits[0].id == foo.id
    assert audits[0].name == "foo"
    assert audits[1].audit_operation == "U"
    assert audits[1].audit_operation_timestamp is not None
    assert audits[1].id == foo.id
    assert audits[1].name == "bar"


@pytest.mark.parametrize("schema", [None, "test_schema"])
def test_it_creates_rows_in_audit_table_for_deletes(session, schema):
    Base = declarative_base()

    @audit
    class Foo(Base):
        __tablename__ = "foo"
        __table_args__ = {"schema": schema}

        id = Column(types.Integer(), autoincrement=True, primary_key=True)
        name = Column(types.String())

    Base.metadata.create_all(bind=session.connection())
    install_audit_triggers(Base.metadata, session.connection())

    foo = Foo(name="foo")
    session.add(foo)
    session.commit()

    session.delete(foo)

    audits = session.query(Foo.__audit_cls__).all()
    assert len(audits) == 2
    assert audits[0].audit_operation == "I"
    assert audits[0].audit_operation_timestamp is not None
    assert audits[0].id == foo.id
    assert audits[0].name == foo.name
    assert audits[1].audit_operation == "D"
    assert audits[1].audit_operation_timestamp is not None
    assert audits[1].id == foo.id
    assert audits[1].name == foo.name
