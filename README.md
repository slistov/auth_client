
# OAuth2 client library

Authenticate user with third-party OAuth2 provider for your Fastapi app

## Description

The library automates recieving of user email from oauth2 provider.
Two steps:

1. Redirect user to lib's endpoint and get **token** as a response.
2. Use the token to call lib's endpoint to get user's **email**

## Example

### 1. Get token

**Redirect user** to backend lib's endpoint

Ex.:

```
    curl -X 'GET' \
    'http://127.0.0.1:8000/api/oauth/redirect?provider=google' \
    -H 'accept: application/json'
```

...and get token as response

Ex.:

```
    {
        "access_token": "TokenSomeStringValue"
    }
```

### 2. Get user email

**Call userinfo** endpoint

Ex.:

```
    curl --location 'http://127.0.0.1:8000/api/oauth/userinfo' \
    --header 'Authorization: Bearer TokenSomeStringValue'
```

...and get user's email as response

Ex.:

```
    {
        "email": "roadtoumba@gmail.com"
    }
```

## How to integrate into your fastapi app

### Backend

#### Import router

```
from oauth_client_lib import oauth_router

app = FastAPI()

app.include_router(oauth_router, prefix='/api')
```

Your fastapi app got new endpoints now:

![Oauth endpoints](docs/images/oauth_endpoints.png)

### Frontend

#### Add oauth2 providers' pics

Ex.:

![Continue with...](docs/images/oauth_providers.png)

#### Link providers' pics to router's endpoints

- for google: /api/oauth/authorize?provider=google
- for yandex: /api/oauth/authorize?provider=yandex

## Settings

### Environment

There must be variables in your environment (use .env file, for example):

- OAUTH_DB_URI - postgres db connection for oauth purposes (grants, tokens, etc..)
- API_HOST - you fastapi app host

Ex.:

    OAUTH_DB_URI=postgresql://user:pwd123@localhost:5432/oauth
    API_HOST=http://192.168.0.100

### config.yaml

You can add custom oauth2 provider into oauth/providers:

```
oauth:
    providers:
        <provider_name>:
            scopes:
            - <scope1>
            - <scope2>
            - ...list of scopes enougth to request email
            urls:
                code: https://authorise-endpoint-that-returns-authorization-code
                token: https://token-request-endpoint
                userinfo: https://userinfo-endpoint
```

 Use *provider_name* as a query param while redirecting user on step 1 of example
