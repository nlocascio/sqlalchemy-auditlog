from sqlalchemy_auditlog.table import create_audit_table


def audit_model(model_cls, **kwargs):
    audit_model = create_audit_model(model_cls, **kwargs)

    model_cls.__audit_cls__ = audit_model

    return model_cls


def create_audit_model(model_cls, **kwargs):
    audit_table = create_audit_table(model_cls.__table__, **kwargs)

    return type(
        f"{model_cls.__name__}Audit",
        model_cls.__bases__,
        {"__table__": audit_table},
    )
