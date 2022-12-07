import os
import json
from dotenv import load_dotenv
load_dotenv()

import yaml
config = yaml.safe_load(open("config.yaml", mode="r", encoding="utf-8"))


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 5432 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "abc123")
    user, db_name = "postgres", "client"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url():
    host = os.environ.get("API_HOST", "http://localhost:9000")
    return f"{host}"

def get_oauth_host():
    host = os.environ.get("OAUTH_HOST", "http://localhost:8000")    
    return f"{host}"

def get_client_credentials():
    return (
        os.environ.get("CLIENT_ID", "No CLIENT_ID provided"), 
        os.environ.get("CLIENT_SECRET", "No CLIENT_SECRET provided")
    )

# def get_token_default_expires_in():
#     return config

# ENDPOINTS
_API = config['API']

_API_OAUTH = _API['OAUTH']
_API_OAUTH_URL = f"{_API['BASE_URL']}{_API_OAUTH['BASE_URL']}"
_API_OAUTH_ENDPOINTS = _API_OAUTH['ENDPOINTS']

AUTHORIZE = f"{_API_OAUTH_URL}{_API_OAUTH_ENDPOINTS['AUTHORIZE']}"
CALLBACK = f"{_API_OAUTH_URL}{_API_OAUTH_ENDPOINTS['CALLBACK']}"
USER_INFO = f"{_API_OAUTH_URL}{_API_OAUTH_ENDPOINTS['USER_INFO']}"
TOKEN = f"{_API_OAUTH_URL}{_API_OAUTH_ENDPOINTS['TOKEN']}"

# Client api (not CRM)
_API_CRM = _API['CRM']
_API_CRM_BASE_URL = f"{_API['BASE_URL']}{_API_CRM['BASE_URL']}"
_API_CRM_ENDPOINTS = _API_CRM['ENDPOINTS']

LOGIN_CRM_URL = f"{_API_CRM_BASE_URL}{_API_CRM_ENDPOINTS['LOGIN']}"
USERS_CRM_URL = f"{_API_CRM_BASE_URL}{_API_CRM_ENDPOINTS['USERS']}"
EMPLOYEES_CRM_URL = f"{_API_CRM_BASE_URL}{_API_CRM_ENDPOINTS['EMPLOYEES']}"

_API_ENDPOINTS = _API['ENDPOINTS']
_API_BASE_URL = _API['BASE_URL']
DESKS = f"{_API_BASE_URL}{_API_ENDPOINTS['DESKS']}"


# OAUTH
_OAUTH_CONF = config['OAUTH']
# _URL = _OAUTH_CONF['URL']
_URL = os.getenv('OAUTH_URL')
_OAUTH_ENDPOINTS = _OAUTH_CONF['ENDPOINTS']

OAUTH_AUTHORIZE = f"{_URL}{_OAUTH_ENDPOINTS['AUTHORIZE']}"

#OAUTH_TOKEN = f"{_URL}{_OAUTH_ENDPOINTS['TOKEN']}"
OAUTH_TOKEN_ENDPOINT = _OAUTH_ENDPOINTS['TOKEN']

OAUTH_TOKEN_INFO = f"{_URL}{_OAUTH_ENDPOINTS['TOKEN_INFO']}"
OAUTH_USER_INFO = f"{_URL}{_OAUTH_ENDPOINTS['USER_INFO']}"

OAUTH_FRONT_URL = os.getenv('OAUTH_FRONT_URL')

# CRM api, client uses this api to request CRM
_CRM_CONF = config['CRM']
_CRM_URL = _CRM_CONF['URL']
_CRM_ENDPOINTS = _CRM_CONF['ENDPOINTS']

CRM_URL = _CRM_URL
CRM_LOGIN = _CRM_ENDPOINTS['LOGIN']
CRM_LOGIN['URL'] = f"{_CRM_URL}{CRM_LOGIN['URL']}"

CRM_USERS = _CRM_ENDPOINTS['USERS']
CRM_USERS['URL'] = f"{_CRM_URL}{CRM_USERS['URL']}"

CRM_EMPLOYEES = _CRM_ENDPOINTS['EMPLOYEES']
CRM_EMPLOYEES['URL'] = f"{_CRM_URL}{CRM_EMPLOYEES['URL']}"

CRM_TIMEOUT = _CRM_CONF['TIMEOUT']


# # CRM3 DESKS
# CRM3DESKS_URL = os.getenv('CRM3DESKS_URL')

# LOGGING
ERROR_LOG_FILENAME = config['ERROR_LOG_FILENAME']


# VARS
SCOPE = config['SCOPE']
STATE_LENGTH = config['STATE_LENGTH']
ORIGINS = json.loads(os.environ['ORIGINS'])
REDIRECT_URI = f"{get_api_url()}{CALLBACK}"

# TOKENS
LOGIN_TOKEN_EXPIRE_MINUTES = config['LOGIN_TOKEN_EXPIRE_MINUTES']

# Secrets
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = config['ALGORITHM']



def get_api_authorize_uri():
    return AUTHORIZE

def get_oauth_callback_URL():
    base_url = get_api_url()
    callback_uri = CALLBACK
    return f"{base_url}{callback_uri}"

def get_oauth_token_endpoint_uri():
    return OAUTH_TOKEN_ENDPOINT

def get_scope():
    return os.environ.get("SCOPE", "email")

