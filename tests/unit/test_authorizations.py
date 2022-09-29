from src.auth_client.domain import model


def test_for_auth_deactivate_deactivates_authorization_and_its_state_grants_and_tokens():
    state = model.State("test_state")
    grant = model.Grant("authorization_code", "test_code")
    token = model.Token("test_token")

    auth = model.Authorization(state, [grant], [token])
    
    assert state.is_active
    assert grant.is_active
    assert token.is_active

    auth.deactivate()

    assert not auth.is_active 
    assert not state.is_active 
    assert not grant.is_active
    assert not token.is_active
