import os
from dotenv import load_dotenv
load_dotenv()



def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 5432 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "abc123")
    user, db_name = "postgres", "client"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    if host == "localhost":
        port = 9000
        schema = f"http://"
    else: 
        port = 9000
        schema = f"https://"
    return f"{schema}{host}:{port}"

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