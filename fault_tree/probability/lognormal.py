from typing import Dict
from enum import Enum, auto
from fault_tree.probability import Probability


class MeanErrorFactor(Enum):
    """Enumeration for specifying the keys used in the LogNormal distribution parameters.

    Attributes:
        mean: Represents the mean of the lognormal distribution.
        error_factor: Represents the error factor of the lognormal distribution.
        percentile: Represents the percentile of the lognormal distribution.
    """
    mean = auto()
    error_factor = auto()
    percentile = auto()

    @staticmethod
    def build(mean: float, error_factor: float = 5, percentile: float = 0.99) -> Dict['MeanErrorFactor', float]:
        """Constructs a dictionary with lognormal distribution parameters.

        Args:
            mean (float): The mean value of the lognormal distribution.
            error_factor (float): The error factor value of the lognormal distribution.
            percentile (float): The percentile value of the lognormal distribution.

        Returns:
            Dict[MeanErrorFactor, float]: A dictionary containing the lognormal distribution parameters.
        """
        value: Dict[MeanErrorFactor, float] = {
            MeanErrorFactor.mean: mean,
            MeanErrorFactor.error_factor: error_factor,
            MeanErrorFactor.percentile: percentile,
        }
        return value


class LogNormal(Probability):
    """Represents a lognormal distribution for a probability.

    This class is a concrete implementation of the Probability abstract class,
    representing a probability as a lognormal distribution characterized by its mean,
    error factor, and percentile.

    Attributes:
        value (Dict[MeanErrorFactor, float]): A dictionary containing the parameters of the lognormal distribution.
    """

    def __init__(self, mean: float, error_factor: float = 5, percentile: float = 0.99):
        """Initializes a LogNormal distribution with the given parameters.

        Args:
            mean (float): The mean value of the lognormal distribution.
            error_factor (float): The error factor value of the lognormal distribution.
            percentile (float): The percentile value of the lognormal distribution.

        Raises:
            ValueError: If any of the provided parameters are out of their expected ranges.
        """
        # Add any necessary validation for mean, error_factor, and percentile here
        # For example, if mean should be positive, error_factor > 1, etc.
        value: Dict[MeanErrorFactor, float] = MeanErrorFactor.build(mean=mean, error_factor=error_factor, percentile=percentile)
        super().__init__(value=value)
