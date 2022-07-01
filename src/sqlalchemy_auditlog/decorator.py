from sqlalchemy_auditlog.declarative import audit_model as audit_model_func


def audit_model(_func=None, **kwargs):
    def decorated(model_cls):
        audit_model_func(model_cls, **kwargs)

        return model_cls

    if _func is None:
        return decorated
    return decorated(_func)
