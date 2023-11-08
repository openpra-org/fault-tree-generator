from typing import Optional


class Probability:
    """Represents the abstract concept of a probability.

    This class is intended to be subclassed by specific probability distribution
    implementations, such as point estimates or continuous distributions.

    Attributes:
        value (Optional[float]): The numerical value representing the probability.
            This could be a single point estimate or parameters for a distribution.

    Raises:
        NotImplementedError: If instantiated directly, as it is intended to be an abstract class.
    """

    def __init__(self, value: Optional[float]):
        """Initializes the Probability with a given value.

        Args:
            value (Optional[float]): The numerical value representing the probability.

        Raises:
            NotImplementedError: If this base class is instantiated directly.
        """
        if type(self) is Probability:
            raise NotImplementedError("Probability is an abstract class and cannot be instantiated directly.")
        self.value = value
