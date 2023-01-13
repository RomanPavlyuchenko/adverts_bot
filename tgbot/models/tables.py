import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from tgbot.services.db_connection import Base


class User(Base):
    __tablename__ = "user"
    id = sa.Column(sa.BigInteger, primary_key=True, index=True)
    username = sa.Column(sa.String(), nullable=True)
    subscribe = sa.Column(sa.Date(), nullable=True)
    wbaccounts = sa.Column(sa.String, nullable=True)
    tracking_id = relationship("Tracking")


class Tracking(Base):
    __tablename__ = "tracking"
    tracking_id = sa.Column(UUID(as_uuid=True), primary_key=True)#), server_default=sa.text("public.gen_random_uuid()")
    user_id = sa.Column(sa.ForeignKey("user.id"))
    query_text = sa.Column(sa.String, unique=False, nullable=True)
    scu = sa.Column(sa.Integer, unique=False, nullable=True)


class WBAccounts(Base):
    __tablename__ = 'wbaccount'
    user_id = sa.Column(sa.BigInteger)
    name = sa.Column(sa.String)
    phone = sa.Column(sa.String, primary_key=True)
    choice = sa.Column(sa.Boolean, default=False)
    wb3token = sa.Column(sa.String, nullable=True)
    wbtoken = sa.Column(sa.String, nullable=True)
    wb_user_id = sa.Column(sa.BigInteger, nullable=True)
    supplier_id = sa.Column(sa.String, nullable=True)


class Campaigns(Base):
    __tablename__ = 'campaign'
    campaign_id = sa.Column(sa.BigInteger, primary_key=True)
    phone = sa.Column(sa.String)
    campaign_name = sa.Column(sa.String)
    type = sa.Column(sa.String)
    place = sa.Column(sa.Integer)
    limit = sa.Column(sa.Integer)
    keywords = sa.Column(sa.String, nullable=True)
    phrases = sa.Column(sa.String, nullable=True)
    auto_change_phrases = sa.Column(sa.Boolean, default=False)
    sku = sa.Column(sa.BigInteger, nullable=True, default=0)
    balance = sa.Column(sa.Integer, nullable=True)
    append_balance = sa.Column(sa.Integer, nullable=True, default=0)
    is_active = sa.Column(sa.Boolean, default=False)


class Buffer(Base):
    __tablename__ = 'buffer'
    message_id = sa.Column(sa.Integer, primary_key=True)
    cid = sa.Column(sa.BigInteger)
    text = sa.Column(sa.String)


class DefaultCampaigns(Base):
    __tablename__ = 'default_campaign'
    campaign_id = sa.Column(sa.BigInteger, primary_key=True)
    phone = sa.Column(sa.String)
    name = sa.Column(sa.String)
    type = sa.Column(sa.String)
