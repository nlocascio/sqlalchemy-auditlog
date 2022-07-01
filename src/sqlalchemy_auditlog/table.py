from sqlalchemy import Column, Table, types

from sqlalchemy_auditlog.ddl import create_audit_trigger_ddl


def create_audit_table(table, session_setting_columns=[]):
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
    ]

    audit_operation_columns = [
        Column("audit_operation", types.String(1), nullable=False),
        Column("audit_operation_current_user", types.String, nullable=False),
        Column("audit_operation_timestamp", types.DateTime, nullable=False, primary_key=True),
    ]

    info = {
        "audit.create_trigger_ddl": create_audit_trigger_ddl(
            table_name=table.name,
            audit_table_name=name,
            schema=schema,
            columns=columns,
            audit_operation_columns=audit_operation_columns,
            session_setting_columns=session_setting_columns,
        )
    }

    return Table(
        name,
        table.metadata,
        *columns,
        *audit_operation_columns,
        *session_setting_columns,
        schema=schema,
        info=info,
    )
