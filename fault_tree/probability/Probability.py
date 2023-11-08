

class Probability:
    def __init__(self, value: any):
        self.value = value

    def to_xml(self, printer):
        raise NotImplementedError

    def to_openpra_json(self, printer):
        raise NotImplementedError

    def to_aralia(self, printer):
        raise NotImplementedError
