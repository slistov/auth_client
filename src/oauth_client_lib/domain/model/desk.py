class Desk:
    def __init__(self, name, structure_json) -> None:
        self._name = name
        self._structure_json = structure_json
    
    @property
    def name(self):
        return self._name

    @property
    def structure_json(self):
        return self._structure_json
    