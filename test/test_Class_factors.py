import pytest
from Class_factors import Factors, FactorError  # Replace 'your_module' with the actual module where Factors is defined

# Test the set_min_max_prob function
def test_set_min_max_prob():
    factors = Factors()
    factors.set_min_max_prob(0, 0.5)
    assert factors.min_prob == 0
    assert factors.max_prob == 0.5

    with pytest.raises(FactorError, match="Min probability must be in [0, 1] range."):
        factors.set_min_max_prob(-0.1, 0.5)

    with pytest.raises(FactorError, match="Max probability must be in [0, 1] range."):
        factors.set_min_max_prob(0.1, 1.1)

    with pytest.raises(FactorError, match="Min probability > Max probability."):
        factors.set_min_max_prob(0.5, 0.4)

# Test the set_common_event_factors function
def test_set_common_event_factors():
    factors = Factors()
    factors.set_common_event_factors(0.2, 0.3, 5, 6)
    assert factors.common_b == 0.2
    assert factors.common_g == 0.3
    assert factors.parents_b == 5
    assert factors.parents_g == 6

    with pytest.raises(FactorError, match="common_b not in (0, 0.9]."):
        factors.set_common_event_factors(0, 0.3, 5, 6)

    with pytest.raises(FactorError, match="parents_b not in [2, 100]."):
        factors.set_common_event_factors(0.2, 0.3, 1, 6)

# Test the set_num_factors function
def test_set_num_factors():
    factors = Factors()
    factors.set_num_factors(4, 10, 2, 3, 1, 0)
    assert factors.num_args == 4
    assert factors.num_basic == 10
    assert factors.num_house == 2
    assert factors.num_ccf == 3
    assert factors.ccf_model == 1
    assert factors.ccf_size == 0

    with pytest.raises(FactorError, match="avg. # of gate arguments can't be less than 2."):
        factors.set_num_factors(1, 10, 2, 3)

    with pytest.raises(FactorError, match="# of basic events must be more than 0."):
        factors.set_num_factors(4, 0, 2, 3)

# Test the __calculate_max_args function (private method)
def test_calculate_max_args():
    factors = Factors()
    max_args = factors._Factors__calculate_max_args(4, [0.1, 0.2, 0.3, 0.4, 0.5])
    assert max_args == 4.5  # Expected result based on the formula

# Test the set_gate_weights function
def test_set_gate_weights():
    factors = Factors()
    factors.set_gate_weights([0.1, 0.2, 0.3, 0.4])
    assert factors.get_gate_weights() == [0.1, 0.2, 0.3, 0.4]

    with pytest.raises(FactorError, match="No weights are provided"):
        factors.set_gate_weights([])

    with pytest.raises(FactorError, match="Weights cannot be negative"):
        factors.set_gate_weights([0.1, 0.2, -0.3, 0.4])

# Add tests for the remaining functions similarly

# ...

