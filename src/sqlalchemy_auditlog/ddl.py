import textwrap
from typing import List

from sqlalchemy import Column


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
    schema: str,
    audit_table_name: str,
    columns: List[Column],
    audit_operation_columns: List[Column],
):
    trigger_name = f"audit_{schema}_{table_name}"
    column_names = ", ".join(c.name for c in columns + audit_operation_columns)

    insert_elements = [f'NEW."{c.name}"' for c in columns]
    update_elements = [f'NEW."{c.name}"' for c in columns]
    delete_elements = [f'OLD."{c.name}"' for c in columns]

    insert_elements.extend(
        [
            "'I'",
            "now()",
        ]
    )
    update_elements.extend(
        [
            "'U'",
            "now()",
        ]
    )
    delete_elements.extend(
        [
            "'D'",
            "now()",
        ]
    )

    return PROCEDURE_TEMPLATE.format(
        trigger_name=trigger_name,
        table_name=f"{schema}.{table_name}",
        audit_table_name=f"{schema}.{audit_table_name}",
        column_names=column_names,
        insert_elements=", ".join(insert_elements),
        update_elements=", ".join(update_elements),
        delete_elements=", ".join(delete_elements),
    )


PROCEDURE_TEMPLATE = textwrap.dedent(
    """\
    CREATE OR REPLACE FUNCTION {trigger_name}()
        RETURNS TRIGGER
    AS
    $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            INSERT INTO {audit_table_name} ({column_names}) SELECT {insert_elements};
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO {audit_table_name} ({column_names}) SELECT {update_elements};
        ELSIF (TG_OP = 'DELETE') THEN
            INSERT INTO {audit_table_name} ({column_names}) SELECT {delete_elements};
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
