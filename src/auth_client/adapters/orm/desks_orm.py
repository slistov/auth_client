from sqlalchemy import (
    Table, 
    Column, 
    Integer, 
    String, 
    FetchedValue,
    DateTime, 
    Interval,
    Boolean,
    ForeignKey,
)

from sqlalchemy.orm import relationship, registry
from .orm import mapper_registry
from auth_client.domain import model

from sqlalchemy.dialects.postgresql import JSONB

# Из-за проблем при редактировании json "по месту",
# будем юзать эту либу
# https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/
from sqlalchemy_json import mutable_json_type


mapper_registry = registry()

desks = Table(
    'desks', mapper_registry.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, server_default=FetchedValue()),
    Column('name', String),
    Column('structure_json', mutable_json_type(dbtype=JSONB, nested=True),    
    Column('created', DateTime),
    Column('created_by', Integer, ForeignKey(User.id), nullable=False),    
    Column('is_active', Boolean)
)


class Desk(Base):
    __tablename__ = "desks"
    id = Column(BigInteger, primary_key=True, autoincrement=True, server_default=FetchedValue())
    name = Column(String)
    structure_json = Column(mutable_json_type(dbtype=JSONB, nested=True))
    created_by = Column(Integer, ForeignKey(User.id), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="desks")
