from src.auth_client.domain import model, events
import unit_of_work
 

def create_state(
    event: events.StateRequired,
    uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        state = model.State()
        uow.states.add(state)
        uow.commit()
    