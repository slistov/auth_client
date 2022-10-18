from auth_client.domain import model

def test_desk():
    desk = model.Desk("Desk", {'struct': 'test struct'})

    assert desk.name == 'Desk'
    assert desk.structure_json == {'struct': 'test struct'}
