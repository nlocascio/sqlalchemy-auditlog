import textwrap
from typing import List, Literal, Union

from sqlalchemy import Column, Table, insert, select, text


def install_audit_triggers(metadata, connection):
    trigger_ddl = [
        t.info["audit.create_trigger_ddl"]
        for t in metadata.tables.values()
        if t.info.get("audit.create_trigger_ddl")
    ]

    for ddl in trigger_ddl:
        connection.execute(ddl)


def create_audit_trigger_ddl(
    table_name: str,
    audit_table_name: str,
    schema: str,
    columns: List[Column],
    audit_operation_columns: List[Column],
    session_setting_columns: List[Column],
):
    trigger_name = f"audit_{schema}_{table_name}"

    column_names = ", ".join(f"\"{c.name}\"" for c in columns + audit_operation_columns + session_setting_columns)

    insert_stmt = INSERT_STMT_TEMPLATE.format(
        audit_table_name=f"{schema}.{audit_table_name}",
        columns=column_names,
        values=_get_values_for_operation(columns, session_setting_columns, "insert"),
    )

    update_stmt = INSERT_STMT_TEMPLATE.format(
        audit_table_name=f"{schema}.{audit_table_name}",
        columns=column_names,
        values=_get_values_for_operation(columns, session_setting_columns, "update"),
    )

    delete_stmt = INSERT_STMT_TEMPLATE.format(
        audit_table_name=f"{schema}.{audit_table_name}",
        columns=column_names,
        values=_get_values_for_operation(columns, session_setting_columns, "delete"),
    )

    return PROCEDURE_TEMPLATE.format(
        trigger_name=trigger_name,
        table_name=f"{schema}.{table_name}",
        insert_stmt=insert_stmt,
        update_stmt=update_stmt,
        delete_stmt=delete_stmt,
    )


def _get_values_for_operation(columns: List[Column], session_setting_columns: List[Column], operation: Union[Literal["insert"], Literal["update"], Literal["delete"]]):
    session_setting_values = [f"current_setting('audit.{c.name}')" for c in session_setting_columns]

    if operation == "insert":
        values = [f"NEW.\"{c.name}\"" for c in columns] + ["'I'", "current_user", "NOW()"] + session_setting_values
    elif operation == "update":
        values = [f"NEW.\"{c.name}\"" for c in columns] + ["'U'", "current_user", "NOW()"] + session_setting_values
    elif operation == "delete":
        values = [f"OLD.\"{c.name}\"" for c in columns] + ["'D'", "current_user", "NOW()"] + session_setting_values

    return ", ".join(values)


INSERT_STMT_TEMPLATE = textwrap.dedent(
    """\
        INSERT INTO {audit_table_name} ({columns}) SELECT {values};
    """
)

PROCEDURE_TEMPLATE = textwrap.dedent(
    """\
    CREATE OR REPLACE FUNCTION {trigger_name}()
        RETURNS TRIGGER
    AS
    $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            {insert_stmt}
        ELSIF (TG_OP = 'UPDATE') THEN
            {update_stmt}
        ELSIF (TG_OP = 'DELETE') THEN
            {delete_stmt}
        END IF;
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};

    CREATE TRIGGER {trigger_name}
    AFTER INSERT OR UPDATE OR DELETE ON {table_name}
    FOR EACH ROW EXECUTE PROCEDURE {trigger_name}();
    """
)
