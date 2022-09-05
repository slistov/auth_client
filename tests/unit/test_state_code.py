def test_state_generated_and_saved_in_db():
    state_out = State()

    state_in = State(state_out.code)
    assert state_out == state_in