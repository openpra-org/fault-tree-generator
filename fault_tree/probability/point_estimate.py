from fault_tree.probability import Probability


class PointEstimate(Probability):
    """Represents a point estimate probability.

    This class is a concrete implementation of the Probability abstract class,
    representing a probability as a single fixed value, known as a point estimate.

    Attributes:
        value (float): The numerical value representing the probability, which must
            be between 0.0 and 1.0 inclusive.

    Raises:
        ValueError: If the value is not within the range [0.0, 1.0].
    """

    def __init__(self, value: float):
        """Initializes a PointEstimate with a given probability value.

        Args:
            value (float): The numerical value representing the probability, which must
                be between 0.0 and 1.0 inclusive.

        Raises:
            ValueError: If the value is not within the range [0.0, 1.0].
        """
        if not 0.0 <= value <= 1.0:
            raise ValueError('Point estimate value must be within the domain [0, 1].')

        super().__init__(value)
