
# OAuth2 client

Authenticate user with third-party OAuth2 provider for your Fastapi app

## Description

The app gets token from oauth service according to oauth2.0 specs

## How to use

### 1. Get token

On your frontend
>use links

- Google authentication
`GET /api/oauth/authorize?provider=google`
- Yandex authentication
`GET /api/oauth/authorize?provider=yandex`
- (any other, you can set it up)

>...and get token as response

### 2. Get user's email

On your frontend
>use token as authorization header

```
GET /api/oauth/userinfo
```

>...and get user's email as response

### 3. That's it

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

![Continue with...](docs/images/oauth_providers.png)

#### Link providers' pics to router's endpoints

- for google: /api/oauth/authorize?provider=google
- for yandex: /api/oauth/authorize?provider=yandex

## Settings

### Environment

There must be variables in your environment (use .env file, for example):

OAUTH_DB_URI - postgres db connection for oauth purposes (grants, tokens, etc..)

Ex.:

    OAUTH_DB_URI=postgresql://user:pwd123@localhost:5432/oauth

API_HOST - you fastapi app host

Ex.:

    API_HOST=http://192.168.0.100
