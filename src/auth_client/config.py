import os
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
    host = os.environ.get("API_HOST", "localhost")
    return f"{host}"

def get_oauth_host():
    host = os.environ.get("OAUTH_HOST", "localhost:8000")    
    return f"{host}"

def get_client_credentials():
    return (
        os.environ.get("CLIENT_ID", "No CLIENT_ID provided"), 
        os.environ.get("CLIENT_SECRET", "No CLIENT_SECRET provided")
    )

def get_oauth_callback_URL():
    base_url = get_api_url()
    callback_uri = os.environ.get("API_OAUTH_CALLBACK")
    return f"{base_url}{callback_uri}"

def get_scope():
    return os.environ.get("SCOPE", "email")

def get_api_authorize_uri():
    endpoint = os.environ.get("API_AUTHORIZE")
    return f"{endpoint}"

# def get_token_default_expires_in():
#     return config