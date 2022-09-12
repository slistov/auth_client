from src.auth_client.domain import model
from pytest import Session

class FakeCodeGenerator():
    def get_state_code(self):
        return "test_state"

def test_state_is_saved_in_db(session):
    # code_gen = FakeCodeGenerator()
    # new_state = code_gen.get_state_code()

    state = model.State()
    code = state.get_code()

    

    assert code == "test_state"