from sqlalchemy import Column, types
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class QaCheck(Base):
    __tablename__ = "qa_check"
    __abstract__ = True
    __mapper_args__ = {
        "polymorphic_on": type,
    }

    id = Column(types.Integer, primary_key=True, autoincrement=True)
    type = Column(types.String(50))


class QaCheckFacebook(QaCheck):
    __tablename__ = "qa_check_facebook"
    __mapper_args__ = {
        "polymorphic_identity": "facebook",
    }


class QaCheckLinkedIn(QaCheck):
    __tablename__ = "qa_check_linkedin"
    __mapper_args__ = {
        "polymorphic_identity": "linkedin",
    }



class QaCheckFacebookCampaignSettings(Base):
    __tablename__ = "qa_check_facebook_campaign_settings"
