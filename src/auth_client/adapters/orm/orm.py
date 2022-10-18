from auth_client.domain import model
from sqlalchemy import event
from .oauth_orm import start_oauth_mappers

def start_mappers():
    start_oauth_mappers()

@event.listens_for(model.Authorization, "load")
def receive_load(auth, _):
    auth.events = []



    # authorizations_mapper = mapper(model.Authorization, authorizations)
    # states_mapper = mapper(model.State, states)
    # grants_mapper = mapper(model.Grant, grants)    
    # tokens_mapper = mapper(model.Token, tokens)
    


# class User(Base):
#     __tablename__ = "users"

#     id = Column(BigInteger, primary_key=True, autoincrement=True, server_default=FetchedValue())    
#     username = Column(String, unique=True, index=True)
#     email = Column(String, unique=True, index=True)
#     created = Column(DateTime, server_default=func.now())
#     is_active = Column(Boolean, default=True)

#     authorizations = relationship("Authorization")
#     desks = relationship("Desk")


# class Authorization(Base):
#     __tablename__ = "authorizations"

#     id = Column(Integer, primary_key=True, index=True)
#     # nullable=True, так как после получения кода авторизации
#     # мы о пользователе ещё ничего не знаем
#     user_id = Column(Integer, ForeignKey(User.id), nullable=True)
#     client_id = Column(UUID(as_uuid=True), nullable=False)
#     scope = Column(String, nullable=False)
#     state = Column(String, nullable=False)
#     expires_in = Column(Interval, nullable=False)
#     is_active = Column(Boolean, nullable=False)
#     source_url = Column(String)

#     user = relationship("User", back_populates="authorizations")
#     grants = relationship("Grant")


# class GrantType(str, enum.Enum):
#     """#### Тип гранта [OAuth2](https://oauth.net/2/grant-types/).
#     """
#     AuthorizationCode = 'authorization_code'
#     RefreshToken = 'refresh_token'
#     # Password = 'password'
#     # ClientCredentials = 'client_credentials'
#     # DeviceCode = 'device_code'
    

# class Grant(Base):
#     __tablename__ = "grants"

#     id = Column(Integer, primary_key=True, index=True)
#     authorization_id = Column(Integer, ForeignKey(Authorization.id), nullable=False)    
#     type = Column('grant_type', Enum(GrantType), nullable=False)
#     code = Column(String, nullable=False)
#     created = Column(DateTime, server_default=func.now())
#     expires_in = Column(Interval, nullable=False)
#     is_active = Column(Boolean, nullable=False)

#     authorization = relationship("Authorization", back_populates="grants")
#     tokens = relationship("Token")

# class Token(Base):
#     __tablename__ = "tokens"
#     id = Column(BigInteger, primary_key=True, autoincrement=True, server_default=FetchedValue())
#     grant_id = Column(Integer, ForeignKey(Grant.id), nullable=False)
#     access_token = Column(String, nullable=False, index=True)
#     created = Column(DateTime, server_default=func.now())
#     expires_in = Column(Interval, nullable=False)
#     is_active = Column(Boolean, nullable=False, default=True)

#     grant = relationship("Grant", back_populates="tokens")


# class Desk(Base):
#     __tablename__ = "desks"
#     id = Column(BigInteger, primary_key=True, autoincrement=True, server_default=FetchedValue())
#     name = Column(String)
#     structure_json = Column(mutable_json_type(dbtype=JSONB, nested=True))
#     created_by = Column(Integer, ForeignKey(User.id), nullable=False)
#     is_active = Column(Boolean, nullable=False, default=True)

#     user = relationship("User", back_populates="desks")

