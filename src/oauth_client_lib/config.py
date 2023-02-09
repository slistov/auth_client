import os
import json
from dotenv import load_dotenv
load_dotenv()

import yaml
config = yaml.safe_load(open("config.yaml", mode="r", encoding="utf-8"))


def get_postgres_uri():
    oauth_db_uri = os.environ.get("OAUTH_DB_URI", "localhost")
    return oauth_db_uri


# LOGGING
ERROR_LOG_FILENAME = config['ERROR_LOG_FILENAME']


def get_oauth_secrets(provider_name):
    with open(f'client_secret_{provider_name}.json') as f:
        secrets = json.load(f)["web"]
        return secrets["client_id"], secrets["client_secret"]


def get_oauth_params(provider_name):
    assert config['oauth']['providers'][provider_name]['scopes']
    assert config['oauth']['providers'][provider_name]['urls']
    providers = config['oauth']['providers']
    provider = providers[provider_name]
    scopes = provider['scopes']
    urls = provider['urls']
    return scopes, urls


def get_api_host():
    return os.environ['API_HOST']


def get_oauth_callback_URL():
    base_url = get_api_host()
    callback_path = config['oauth']['callback']
    return f"{base_url}{callback_path}"
