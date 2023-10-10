import pytest
from Class_factors import Factors  # Replace 'your_module' with the actual module name

def test_set_min_max_prob():
    factors = Factors()
    factors.set_min_max_prob(0.1, 0.9)
    assert factors.min_prob == 0.1
    assert factors.max_prob == 0.9

def test_set_common_event_factors():
    factors = Factors()
    factors.set_common_event_factors(0.2, 0.3, 5, 7)
    assert factors.common_b == 0.2
    assert factors.common_g == 0.3
    assert factors.parents_b == 5
    assert factors.parents_g == 7

def test_set_num_factors():
    factors = Factors()
    factors.set_num_factors(4, 10, 2, 1)
    assert factors.num_args == 4
    assert factors.num_basic == 10
    assert factors.num_house == 2
    assert factors.num_ccf == 1

def test_calculate():
    factors = Factors()
    factors.set_num_factors(4, 10, 2, 1)
    factors.calculate()
    # You can add assertions to check calculated values

def test_get_gate_weights():
    factors = Factors()
    factors.set_gate_weights([0.1, 0.2, 0.3, 0.4, 0.5])
    weights = factors.get_gate_weights()
    assert weights == [0.1, 0.2, 0.3, 0.4, 0.5]

def test_get_random_operator():
    factors = Factors()
    operator = factors.get_random_operator()
    assert operator in factors._Factors__OPERATORS  # Testing a private constant

def test_get_num_args():
    factors = Factors()
    gate = factors.get_random_operator()
    num_args = factors.get_num_args(gate)
    if gate == "not" or gate == "xor":
        assert num_args == 1 or num_args == 2
    else:
        assert num_args >= 2

def test_get_percent_gate():
    factors = Factors()
    percent_gate = factors.get_percent_gate()
    assert percent_gate >= 0.0 and percent_gate <= 1.0

def test_get_num_gate():
    factors = Factors()
    factors.set_num_factors(4, 10, 2, 1)
    num_gate = factors.get_num_gate()
    assert num_gate > 0

def test_get_num_common_basic():
    factors = Factors()
    factors.set_num_factors(4, 10, 2, 1)
    num_gate = factors.get_num_gate()
    num_common_basic = factors.get_num_common_basic(num_gate)
    assert num_common_basic >= 0

def test_get_num_common_gate():
    factors = Factors()
    factors.set_num_factors(4, 10, 2, 1)
    num_gate = factors.get_num_gate()
    num_common_gate = factors.get_num_common_gate(num_gate)
    assert num_common_gate >= 0

def test_constrain_num_gate():
    factors = Factors()
    factors.set_num_factors(4, 10, 2, 1)
    num_gate = factors.get_num_gate()
    factors.constrain_num_gate(num_gate)
    # You can add assertions to check if the constraints were applied correctly


if __name__ == "__main__":
    pytest.main()
