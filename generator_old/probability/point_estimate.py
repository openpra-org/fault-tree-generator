from generator_old.probability.Probability import Probability


class PointEstimate(Probability):
    """
        The PointEstimate class is a subclass of the Probability abstract class.
        This class represents the probability of a particular event given only a
        single value.
        Args:
            value: A float value between 0.0 and 1.0 inclusive.

        Attributes:
            value: The float value that was passed in.

        Raises:
            ValueError: If the value is not between 0.0 and 1.0 inclusive.
    """
    def __init__(self, value: any):

        if value > 1.0 or value < 0:
            raise ValueError('Point estimate value cannot be outside domain [0, 1]')

        super().__init__(value)

    def to_openpra_json(self, printer):
        pass

    def to_aralia(self, printer):
        pass

    def to_xml(self, printer):
        """Produces the Open-PSA MEF XML definition of a point estimate."""
        printer('<float value="', self.value, '"/>')
