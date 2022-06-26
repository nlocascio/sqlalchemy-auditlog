from sqlalchemy import Column, Table, types

from sqlalchemy_auditlog.ddl import create_audit_trigger_ddl


def audit(_func=None, *, ignore_columns=[]):
    def decorated(model_cls):
        audit_model(model_cls, ignore_columns=ignore_columns)

        return model_cls

    if _func is None:
        return decorated
    return decorated(_func)


def audit_model(model_cls, ignore_columns=[]):
    audit_model = create_audit_model(model_cls, ignore_columns=ignore_columns)

    model_cls.__audit_cls__ = audit_model


def create_audit_model(model_cls, ignore_columns=[]):
    audit_table = create_audit_table(model_cls.__table__, ignore_columns=ignore_columns)

    return type(
        f"{model_cls.__name__}Audit",
        model_cls.__bases__,
        {"__table__": audit_table},
    )


def create_audit_table(table, ignore_columns=[]):
    name = f"{table.name}_audit"
    schema = table.schema or "public"

    columns = [
        Column(
            c.name,
            c.type,
            nullable=True,
            primary_key=c.primary_key,
        )
        for c in table.c.values()
        if c.name not in ignore_columns
    ]

    audit_operation_columns = [
        Column("audit_operation", types.String(1), nullable=False),
        Column("audit_operation_timestamp", types.DateTime, nullable=False, primary_key=True),
    ]

    info = {
        "audit.create_trigger_ddl": create_audit_trigger_ddl(
            table_name=table.name,
            schema=schema,
            audit_table_name=name,
            columns=columns,
            audit_operation_columns=audit_operation_columns,
        )
    }

    return Table(
        name,
        table.metadata,
        *columns,
        *audit_operation_columns,
        schema=schema,
        info=info,
    )
