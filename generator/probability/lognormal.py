from typing import Dict

from Probability import Probability

from enum import Enum, auto


class MeanErrorFactor(Enum):
    mean = auto()
    error_factor = auto()
    percentile = auto()

    @staticmethod
    def build(mean: float, error_factor: float = 5, percentile: float = 0.99) -> Dict['MeanErrorFactor', float]:
        value: Dict[MeanErrorFactor, float] = {
            MeanErrorFactor.mean: mean,
            MeanErrorFactor.error_factor: error_factor,
            MeanErrorFactor.percentile: percentile,
        }
        return value


class LogNormal(Probability):
    def to_openpra_json(self, printer):
        pass

    def __init__(self, mean: float, error_factor: float = 5, percentile: float = 0.99):
        value: Dict[MeanErrorFactor, float] = MeanErrorFactor.build(mean=mean, error_factor=error_factor, percentile=percentile)
        super().__init__(value=value)

    def to_xml(self, printer):
        printer('<lognormal-deviate>')
        printer('<float value="', self.value[MeanErrorFactor.mean], '"/>')
        printer('<float value="', self.value[MeanErrorFactor.error_factor], '"/>')
        printer('<float value="', self.value[MeanErrorFactor.percentile], '"/>')
        printer('</lognormal-deviate>')

    def to_aralia(self, printer):
        raise NotImplementedError
