import textwrap


def install_audit_triggers(metadata, connection):
    trigger_ddl = [
        t.info["audit.create_trigger_ddl"]
        for t in metadata.tables.values()
        if t.info.get("audit.create_trigger_ddl")
    ]

    for ddl in trigger_ddl:
        connection.execute(ddl)


def create_audit_trigger_ddl(model_cls, audit_model):
    # TODO: actually make the trigger
    trigger_name = f"audit_{model_cls.__table__.schema}_{model_cls.__table__.name}"
    audit_table = audit_model.__table__.name
    audit_columns = ", ".join(c.name for c in audit_model.__table__.c.values())
    insert_elements = ", ".join([])
    update_elements = ", ".join([])
    delete_elements = ", ".join([])
    table = model_cls.__table__.name

    return PROCEDURE_TEMPLATE.format(
        trigger_name=trigger_name,
        audit_table=audit_table,
        audit_columns=audit_columns,
        insert_elements=insert_elements,
        update_elements=update_elements,
        delete_elements=delete_elements,
        table=table,
    )


PROCEDURE_TEMPLATE = textwrap.dedent(
    """\
    CREATE OR REPLACE FUNCTION {trigger_name}()
        RETURNS TRIGGER
        LANGUAGE plpgsql
    AS
    $$
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            INSERT INTO {audit_table} ({audit_columns}) SELECT {insert_elements};
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO {audit_table} ({audit_columns}) SELECT {update_elements};
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO {audit_table} ({audit_columns}) SELECT {delete_elements};
        END IF;
        RETURN NULL;
    END;
    $$

    DROP TRIGGER IF EXISTS {trigger_name} ON {table};

    CREATE TRIGGER {trigger_name}
    AFTER INSERT OR UPDATE OR DELETE ON {table}
    FOR EACH ROW EXECUTE PROCEDURE {trigger_name}();
    """
)
