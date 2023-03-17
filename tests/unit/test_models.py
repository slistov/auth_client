from src.oauth_client_lib.domain import model


def create_auth_data():
    state = model.State("test_state")
    grant = model.Grant("authorization_code", "test_code")
    token = model.Token("test_token")
    auth = model.Authorization(state, [grant], [token])
    return state, grant, token, auth


def test_when_authorization_deactivates_it_also_deactivates_its_state_grants_and_tokens():
    state, grant, token, auth = create_auth_data()

    assert state.is_active
    assert grant.is_active
    assert token.is_active

    auth.deactivate()

    assert not auth.is_active
    assert not state.is_active
    assert not grant.is_active
    assert not token.is_active
