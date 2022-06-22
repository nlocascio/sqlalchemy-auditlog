from sqlalchemy import Column, Table, types
from sqlalchemy_auditlog.ddl import create_audit_trigger_ddl


def audit(ignore_columns=[]):
    def decorated(model_cls):
        audit_model(model_cls, ignore_columns=ignore_columns)

        return model_cls

    return decorated


def audit_model(model_cls, ignore_columns=[]):
    audit_model = create_audit_model(model_cls, ignore_columns=ignore_columns)

    audit_model.__table__.info["audit.create_trigger_ddl"] = create_audit_trigger_ddl(
        model_cls=model_cls,
        audit_model=audit_model,
    )

    model_cls.__audit_cls__ = audit_model


def create_audit_model(model_cls, ignore_columns=[]):
    audit_table = create_audit_table(model_cls, ignore_columns=ignore_columns)

    return type(
        f"{model_cls.__name__}Audit",
        model_cls.__bases__,
        {"__table__": audit_table},
    )


def create_audit_table(model_cls, ignore_columns=[]):
    name = f"{model_cls.__tablename__}_audit"
    schema = model_cls.__table__.schema or "public"

    columns = [
        Column(
            c.name,
            c.type,
            nullable=True,
        )
        for c in model_cls.__table__.c.values()
        if c.name not in ignore_columns
    ]

    columns.extend(
        [
            Column("audit_id", types.Integer, autoincrement=True, primary_key=True),
            Column("audit_operation", types.String(1), nullable=False),
            Column("audit_operation_timestamp", types.DateTime, nullable=False),
        ]
    )

    return Table(
        name,
        model_cls.metadata,
        *columns,
        schema=schema,
    )
