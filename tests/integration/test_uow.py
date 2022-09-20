from src.auth_client.service_layer import unit_of_work
from src.auth_client.domain import model
from datetime import datetime

def insert_state(session, code, created=datetime.utcnow(), is_active=True):
    session.execute(
        "INSERT INTO states (code, created, is_active) VALUES (:code, :created, :is_active)",
        dict(code=code, created=created, is_active=is_active),
    )


def test_uow_can_save_a_state(session_factory):
    session = session_factory()
    insert_state(session, code="test_state_code", created=datetime.utcnow(), is_active=True)
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        state = uow.states.get(code="test_state_code")
        code = state.code
        uow.commit()

    assert code == "test_state_code"
