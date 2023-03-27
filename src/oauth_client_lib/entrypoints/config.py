import json
import os
import yaml

from dotenv import load_dotenv

load_dotenv()

config = yaml.safe_load(open("config.yaml", mode="r", encoding="utf-8"))


def get_postgres_uri():
    oauth_db_uri = os.environ.get("OAUTH_DB_URI", "localhost")
    return oauth_db_uri


# LOGGING
ERROR_LOG_FILENAME = config["ERROR_LOG_FILENAME"]


def get_oauth_secrets(provider):
    with open(f"client_secret_{provider}.json") as f:
        secrets = json.load(f)["web"]
        return secrets["client_id"], secrets["client_secret"]


def get_oauth_params(provider):
    assert config["oauth"]["providers"][provider]["scopes"]
    assert config["oauth"]["providers"][provider]["urls"]
    provider = config["oauth"]["providers"][provider]
    scopes = provider["scopes"]
    urls = provider["urls"]
    return scopes, urls


def get_api_host():
    return os.environ["API_HOST"]


def get_oauth_callback_URL():
    base_url = get_api_host()
    callback_path = config["oauth"]["callback"]
    return f"{base_url}{callback_path}"
