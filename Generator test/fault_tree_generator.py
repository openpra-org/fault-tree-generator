# pylint: disable=too-many-lines

from collections import deque
import numpy
import random
import math
import sys
import json
import itertools
import argparse as ap
from itertools import combinations
from math import factorial
from math import comb

from fault_tree import BasicEvent, HouseEvent, Gate, CcfGroup, FaultTree

class FactorError(Exception):
    """Errors in configuring factors for the fault tree generation."""


class Factors:  # pylint: disable=too-many-instance-attributes
    """Collection of factors that determine the complexity of the fault tree.

    This collection must be setup and updated
    before the fault tree generation processes.

    Attributes:
        num_args: The average number of arguments for gates.
        num_basic: The number of basic events.
        num_house: The number of house events.
        num_ccf: The number of ccf groups.
        common_b: The percentage of common basic events per gate.
        common_g: The percentage of common gates per gate.
        parents_b: The average number of parents for common basic events.
        parents_g: The average number of parents for common gates.
    """

    # Constant configurations
    __OPERATORS = ["and", "or", "atleast", "not", "xor"]  # the order matters

    def __init__(self):
        """Partial constructor."""
        # Probabilistic factors
        self.min_prob = 0
        self.max_prob = 1

        # Configurable graph factors
        self.num_basic = None
        self.num_house = None
        self.num_ccf = None
        self.common_b = None
        self.common_g = None
        self.num_args = None
        self.parents_b = None
        self.parents_g = None
        self.__weights_g = None  # should not be set directly

        # Calculated factors
        self.__norm_weights = []  # normalized weights
        self.__cum_dist = []  # CDF from the weights of the gate types
        self.__max_args = None  # the upper bound for the number of arguments
        self.__ratio = None  # basic events to gates ratio per gate
        self.__percent_basic = None  # % of basic events in gate arguments
        self.__percent_gate = None  # % of gates in gate arguments

        # Special case with the constrained number of gates
        self.__num_gate = None  # If set, all other factors get affected.
        self.ccf_model = None
        self.ccf_size = None

    def set_min_max_prob(self, min_value, max_value):
        """Sets the probability boundaries for basic events.

        Args:
            min_value: The lower inclusive boundary.
            max_value: The upper inclusive boundary.

        Raises:
            FactorError: Invalid values or setup.
        """
        if min_value < 0 or min_value > 1:
            raise FactorError("Min probability must be in [0, 1] range.")
        if max_value < 0 or max_value > 1:
            raise FactorError("Max probability must be in [0, 1] range.")
        if min_value > max_value:
            raise FactorError("Min probability > Max probability.")
        self.min_prob = min_value
        self.max_prob = max_value

    def set_common_event_factors(self, common_b, common_g, parents_b,
                                 parents_g):
        """Sets the factors for the number of common events.

        Args:
            common_b: The percentage of common basic events per gate.
            common_g: The percentage of common gates per gate.
            parents_b: The average number of parents for common basic events.
            parents_g: The average number of parents for common gates.

        Raises:
            FactorError: Invalid values or setup.
        """
        max_common = 0.9  # a practical limit (not a formal constraint)
        if common_b <= 0 or common_b > max_common:
            raise FactorError("common_b not in (0, " + str(max_common) + "].")
        if common_g <= 0 or common_g > max_common:
            raise FactorError("common_g not in (0, " + str(max_common) + "].")
        max_parent = 100  # also a practical limit
        if parents_b < 2 or parents_b > max_parent:
            raise FactorError("parents_b not in [2, " + str(max_parent) + "].")
        if parents_g < 2 or parents_g > max_parent:
            raise FactorError("parents_g not in [2, " + str(max_parent) + "].")
        self.common_b = common_b
        self.common_g = common_g
        self.parents_b = parents_b
        self.parents_g = parents_g

    def set_num_factors(self, num_args, num_basic, num_house=0, num_ccf=0, ccf_model = 0, ccf_size =0):
        """Sets the size factors.

        Args:
            num_args: The average number of arguments for gates.
            num_basic: The number of basic events.
            num_house: The number of house events.
            num_ccf: The number of ccf groups.
            ccf_model = model used to solve CCF, MGL or alpha-factor

        Raises:
            FactorError: Invalid values or setup.
        """
        if num_args < 2:
            raise FactorError("avg. # of gate arguments can't be less than 2.")
        if num_basic < 1:
            raise FactorError("# of basic events must be more than 0.")
        if num_house < 0:
            raise FactorError("# of house events can't be negative.")
        if num_ccf < 0:
            raise FactorError("# of CCF groups can't be negative.")
        if num_house >= num_basic:
            raise FactorError("Too many house events.")
        if num_ccf > num_basic / num_args:
            raise FactorError("Too many CCF groups.")
        self.num_args = num_args
        self.num_basic = num_basic
        self.num_house = num_house
        self.num_ccf = num_ccf
        self.ccf_model = ccf_model
        self.ccf_size = ccf_size
        # print(ccf_model)
        # print(ccf_size)
    #
    @staticmethod
    def __calculate_max_args(num_args, weights):
        """Calculates the maximum number of arguments for sampling.

        The result may have a fractional part
        that must be adjusted in sampling accordingly.

        Args:
            num_args: The average number of arguments for gates.
            weights: Normalized weights for gate types.

        Returns:
            The upper bound for sampling in symmetric distributions.
        """
        # Min numbers for AND, OR, K/N, NOT, XOR types.
        min_args = [2, 2, 3, 1, 2]
        # Note that max and min numbers are the same for NOT and XOR.
        const_args = min_args[3:]
        const_weights = weights[3:]
        const_contrib = [x * y for x, y in zip(const_args, const_weights)]
        # print(const_args)
        # print(const_weights)
        # print(const_contrib)
        # AND, OR, K/N gate types can have the varying number of args.
        var_args = min_args[:3]
        var_weights = weights[:3]
        var_contrib = [x * y for x, y in zip(var_args, var_weights)]
        # print(var_args)
        # print(var_weights)
        # print(var_contrib)
        # AND, OR, K/N gate types can have the varying number of arguments.
        # Since the distribution is symmetric, the average is (max + min) / 2.
        # print((2 * num_args - sum(var_contrib) - 2 * sum(const_contrib)) /
        #         sum(var_weights))
        # print(sum(var_contrib))
        # print(sum(const_contrib))
        # print(sum(var_weights))
        return ((2 * num_args - sum(var_contrib) - 2 * sum(const_contrib)) /
                sum(var_weights))

    def calculate(self):
        """Calculates any derived factors from the setup.

        This function must be called after all public factors are initialized.
        """
        self.__max_args = Factors.__calculate_max_args(self.num_args,
                                                       self.__norm_weights)
        g_factor = 1 - self.common_g + self.common_g / self.parents_g
        self.__ratio = self.num_args * g_factor - 1
        self.__percent_basic = self.__ratio / (1 + self.__ratio)
        self.__percent_gate = 1 / (1 + self.__ratio)
        # print(self.__max_args)
        # print(g_factor)
        # print(self.__ratio)
        # print(self.__percent_basic)
        # print(self.__percent_gate )

    def get_gate_weights(self):
        """Provides weights for gate types.

        Returns:
            Expected to return weights from the arguments.
        """
        assert self.__weights_g is not None
        return self.__weights_g

    def set_gate_weights(self, weights):
        """Updates gate type weights.

        Args:
            weights: Weights of gate types.
                The weights must have the same order as in OPERATORS list.
                If weights for some operators are missing,
                they are assumed to be 0.

        Raises:
            FactorError: Invalid weight values or setup.
        """
        if not weights:
            raise FactorError("No weights are provided")
        if [i for i in weights if i < 0]:
            raise FactorError("Weights cannot be negative")
        if len(weights) > len(Factors.__OPERATORS):
            raise FactorError("Too many weights are provided")
        if sum(weights) == 0:
            raise FactorError("At least one non-zero weight is needed")
        if len(weights) > 3 and not sum(weights[:3]):
            raise FactorError("Cannot work with only XOR or NOT gates")

        self.__weights_g = weights[:]
        for _ in range(len(Factors.__OPERATORS) - len(weights)):
            self.__weights_g.append(0)  # padding for missing weights
        self.__norm_weights = [
            x / sum(self.__weights_g) for x in self.__weights_g
        ]
        self.__cum_dist = self.__norm_weights[:]
        # print("self", self.__cum_dist )
        self.__cum_dist.insert(0, 0)
        # print("self", self.__cum_dist)
        for i in range(1, len(self.__cum_dist)):
            self.__cum_dist[i] += self.__cum_dist[i - 1]
        # print("self", self.__cum_dist[i])
    def get_random_operator(self):
        """Samples the gate operator.

        Returns:
            A randomly chosen gate operator.
        """
        r_num = random.random()
        bin_num = 1
        # print(r_num)
        while self.__cum_dist[bin_num] <= r_num:
            # print("test", self.__cum_dist[bin_num])
            bin_num += 1
            # print(bin_num)
        # print(Factors.__OPERATORS[bin_num - 1])
        return Factors.__OPERATORS[bin_num - 1]

    def get_num_args(self, gate):
        """Randomly selects the number of arguments for the given gate type.

        This function has a side effect.
        It sets k_num for the K/N type of gates
        depending on the number of arguments.

        Args:
            gate: The parent gate for arguments.

        Returns:
            Random number of arguments.
        """
        if gate.operator == "not":
            return 1
        if gate.operator == "xor":
            return 2

        max_args = int(self.__max_args)
        # Dealing with the fractional part.
        if random.random() < (self.__max_args - max_args):
            # print("max1",max_args)
            max_args += 1
            # print("max2",max_args)


        if gate.operator == "atleast":
            if max_args < 3:
                max_args = 3
            num_args = random.randint(3, max_args)
            # print(num_args)
            gate.k_num = random.randint(2, num_args - 1)
            return num_args
        # print("last", max_args)
        return random.randint(2, max_args)

    def get_percent_gate(self):
        """Returns the percentage of gates that should be in arguments."""
        return self.__percent_gate

    def get_num_gate(self):
        """Approximates the number of gates in the resulting fault tree.

        This is an estimate of the number of gates
        needed to initialize the fault tree
        with the given number of basic events
        and fault tree properties.

        Returns:
            The number of gates needed for the given basic events.
        """
        # Special case of constrained gates
        if self.__num_gate:
            return self.__num_gate
        b_factor = 1 - self.common_b + self.common_b / self.parents_b
        return int(self.num_basic /
                   (self.__percent_basic * self.num_args * b_factor))

    def get_num_common_basic(self, num_gate):
        """Estimates the number of common basic events.

        These common basic events must be chosen
        from the total number of basic events
        in order to ensure the correct average number of parents.

        Args:
            num_gate: The total number of gates in the future fault tree

        Returns:
            The estimated number of common basic events.
        """
        return int(self.common_b * self.__percent_basic * self.num_args *
                   num_gate / self.parents_b)

    def get_num_common_gate(self, num_gate):
        """Estimates the number of common gates.

        These common gates must be chosen
        from the total number of gates
        in order to ensure the correct average number of parents.

        Args:
            num_gate: The total number of gates in the future fault tree

        Returns:
            The estimated number of common gates.
        """
        return int(self.common_g * self.__percent_gate * self.num_args *
                   num_gate / self.parents_g)

    def constrain_num_gate(self, num_gate):
        """Constrains the number of gates.

        The number of parents and the ratios for common nodes are manipulated.

        Args:
            num_gate: The total number of gates in the future fault tree
        """
        if num_gate < 1:
            raise FactorError("# of gates can't be less than 1.")
        if num_gate * self.num_args <= self.num_basic:
            raise FactorError("Not enough gates and avg. # of args "
                              "to achieve the # of basic events")
        self.__num_gate = num_gate
        # Calculate the ratios
        alpha = self.__num_gate / self.num_basic
        # print("alpha",alpha)
        common = max(self.common_g, self.common_b)
        min_common = 1 - (1 + alpha) / self.num_args / alpha
        if common < min_common:
            common = round(min_common + 0.05, 1)
        elif common > 2 * min_common:  # Really hope it does not happen
            common = 2 * min_common
        assert common < 1  # Very brittle configuration here

        self.common_g = common
        self.common_b = common
        parents = 1 / (1 - min_common / common)
        assert parents > 2  # This is brittle as well
        self.parents_g = parents
        self.parents_b = parents


class GeneratorFaultTree(FaultTree):
    """Specialization of a fault tree for generation purposes.

    The construction of fault tree members are handled through this object.
    It is assumed that no removal is going to happen after construction.

    Args:
        factors: The fault tree generation factors.
    """

    def __init__(self, name, factors):
        """Initializes an empty fault tree.

        Args:
            name: The name of the system described by the fault tree container.
            factors: Fully configured generation factors.
        """
        super(GeneratorFaultTree, self).__init__(name)
        self.factors = factors
        # print("self.factors_f", self.factors)

    def construct_top_gate(self, root_name):
        """Constructs and assigns a new gate suitable for being a root.

        Args:
            root_name: Unique name for the root gate.
        """
        assert not self.top_gate and not self.top_gates
        operator = self.factors.get_random_operator()
        while operator in ("xor", "not"):
            operator = self.factors.get_random_operator()
        self.top_gate = Gate(root_name, operator)
        self.gates.append(self.top_gate)

    def construct_gate(self):
        """Constructs a new gate.

        Returns:
            A fully initialized gate with random attributes.
        """
        gate = Gate("G" + str(len(self.gates) + 1),
                    self.factors.get_random_operator())
        self.gates.append(gate)
        # print("gates", gate)
        return gate

    def construct_basic_event(self):
        """Constructs a basic event with a unique identifier.

        Returns:
            A fully initialized basic event with a random probability.
        """
        basic_event = BasicEvent(
            "B" + str(len(self.basic_events) + 1),
            random.uniform(self.factors.min_prob, self.factors.max_prob),self.factors.num_basic)
        self.basic_events.append(basic_event)
        return basic_event



    def construct_house_event(self):
        """Constructs a house event with a unique identifier.

        Returns:
            A fully initialized house event with a random state.
        """
        house_event = HouseEvent("H" + str(len(self.house_events) + 1),
                                 random.choice(["true", "false"]))
        self.house_events.append(house_event)
        return house_event

    def construct_ccf_group(self, members):
        """Constructs a unique CCF group with factors.

        Args:
            members: A list of member basic events.

        Returns:
            A fully initialized CCF group with random factors.
        """
        assert len(members) > 1

        ccf_group = CcfGroup("CCF" + str(len(self.ccf_groups) + 1))
        self.ccf_groups.append(ccf_group)


        ccf_group.members = members

        ccf_group.prob = random.uniform(self.factors.min_prob,
                                        self.factors.max_prob)
        ccf_group.model = self.factors.ccf_model

        # ccf_group.model = "alpha-factor"
        # levels = random.randint(2, len(members)) # the levels should be equal to the number of BEs for alpha-factor model and -1 for MGL
        levels = len(members)
        # print("levels=",levels)
        # ccf_group.factors = [random.uniform(0.1, 1) for _ in range(levels - 1)]
        # sorted(iterable, key=key, reverse=reverse)

        # ccf_event = Ccf_Event("CF", self.factors.num_ccf)
        # self.ccf_events.append(ccf_event)
        # return ccf_event

        if ccf_group.model == "MGL":
            summation = 0
            beta_factors = []
            for i in range(levels-1):
                if i == 0:
                    beta = random.uniform(5.0e-3,1.0e-1)
                    # print("beta",beta)
                    beta_factors.append(beta)
                elif i == 1:
                    gama = random.uniform(beta*5-beta/5, beta*5+beta/5)
                    # print("delta:",gama)
                    beta_factors.append(gama)
                elif i == 2:
                    delta = random.uniform(beta * 5 - beta / 5, beta * 5 + beta / 5)
                    beta_factors.append(delta)
                elif i == 3:
                    Epsilon = random.uniform(beta * 5 - beta / 5, beta * 5 + beta / 5)
                    beta_factors.append(Epsilon)
                elif i ==4:
                    Zeta = random.uniform(beta * 5 - beta / 5, beta * 5 + beta / 5)
                    beta_factors.append(Zeta)
                elif i ==5:
                    Eta = random.uniform(beta * 5 - beta / 5, beta * 5 + beta / 5)
                    beta_factors.append(Eta)
                elif i ==6:
                    Theta = random.uniform(beta * 5 - beta / 5, beta * 5 + beta / 5)
                    beta_factors.append(Theta)
                elif i ==7:
                    lota = random.uniform(beta * 5 - beta / 5, beta * 5 + beta / 5)
                    beta_factors.append(lota)
                else:
                    kappa = random.uniform(beta * 5 - beta / 5, beta * 5 + beta / 5)
                    beta_factors.append(kappa)


            n = 1
            tot = range(levels)
            for i,k in zip(beta_factors,tot):
                    ccf_factors = (1/comb(len(range(levels))-1,k))*(1 - i) * n
                    n = i*n
                    # print('n',n)
                    ccf_group.factors.append(ccf_factors)

            # print(ccf_group.actors)
            # ccf_group.factors = sorted([(_* for _ in tests], reverse = True)
            # ccf_group.factors.append(ccf_group.factors)
            # print("ccf_test", ccf_group.factors)

            # ccf_group.factors = sorted([(random.uniform(0.1, 1)) for _ in range(levels - 1)], reverse=True)

        else:
            summation = 0
            alpha_factors = []
            for i in range(levels):
                # print(i)
                if i == 0:
                    alpha1 = random.uniform(0.9, 1)
                    alpha_factors.append(alpha1)
                    total = alpha1
                elif i > 0 and i <3:
                    alpha2 = random.uniform(0.001, 0.01)
                    alpha_factors.append(alpha2)
                    total += alpha2
                elif i > 3 and i <7:
                    alpha2 = random.uniform(0.0001, 0.001)
                    alpha_factors.append(alpha2)
                    total += alpha2
                else:
                    alpha = random.uniform(0.00001,0.00001)
                    alpha_factors.append(alpha)
                    total += alpha

            summation += total
            # print("sum", summation)
            # ccf_group.factors = sorted([(_/summation) for _ in range(levels)], reverse=True)
            ccf_group.factors = sorted([(_ / summation) for _ in alpha_factors], reverse = True)
            # print("levels", range(levels))

            # ccf_group.factors = sorted([(random.uniform(0.1, 1)) for _ in range(levels)], reverse=True)
            # test_sum = sum(ccf_group.factors)
            # ccf_group.factors.append(ccf_group.factors)
            # print(ccf_group.factors)

            # for i in ccf_group.factors:
            #     print(i)
            #     store += i
            #     print(store)
            # test = list(map(float, ccf_group.factors))
            # total = math.fsum(test)
            # print(test)

            # print(sum(ccf_group.factors))
            # w = numpy.array(ccf_group.factors)
            # print("test",w)
            # print("ccf_test",ccf_group.factors)
            # print("tests_sum",summ)
        return ccf_group


def candidate_gates(common_gate):
    """Lazy generator of candidates for common gates.

    Args:
        common_gate: A list of common gates.

    Yields:
        A next gate candidate from common gates container.
    """
    orphans = [x for x in common_gate if not x.parents]
    random.shuffle(orphans)
    for i in orphans:
        # print(i)
        yield i

    single_parent = [x for x in common_gate if len(x.parents) == 1]
    random.shuffle(single_parent)
    for i in single_parent:
        # print(i)
        yield i

    multi_parent = [x for x in common_gate if len(x.parents) > 1]
    random.shuffle(multi_parent)
    for i in multi_parent:
        # print(i)
        yield i


def correct_for_exhaustion(gates_queue, common_gate, fault_tree):
    """Corrects the generation for queue exhaustion.

    Corner case when not enough new basic events initialized,
    but there are no more intermediate gates to use
    due to a big ratio or just random accident.

    Args:
        gates_queue: A deque of gates to be initialized.
        common_gate: A list of common gates.
        fault_tree: The fault tree container of all events and constructs.
    """
    if gates_queue:
        return
    if len(fault_tree.basic_events) < fault_tree.factors.num_basic:
        # Initialize one more gate
        # by randomly choosing places in the fault tree.
        random_gate = random.choice(fault_tree.gates)
        while (random_gate.operator == "not" or random_gate.operator == "xor" or
               random_gate in common_gate):
            random_gate = random.choice(fault_tree.gates)
        new_gate = fault_tree.construct_gate()
        random_gate.add_argument(new_gate)
        gates_queue.append(new_gate)


def choose_basic_event(s_common, common_basic, fault_tree):
    """Creates a new basic event or uses a common one for gate arguments.

    Args:
        s_common: Sampled factor to choose common basic events.
        common_basic: A list of common basic events to choose from.
        fault_tree: The fault tree container of all events and constructs.

    Returns:
        Basic event argument for a gate.
    """
    if s_common >= fault_tree.factors.common_b or not common_basic:
        return fault_tree.construct_basic_event()

    orphans = [x for x in common_basic if not x.parents]
    if orphans:
        return random.choice(orphans)

    single_parent = [x for x in common_basic if len(x.parents) == 1]
    if single_parent:
        return random.choice(single_parent)

    return random.choice(common_basic)


def init_gates(gates_queue, common_basic, common_gate, fault_tree):
    """Initializes gates and other basic events.

    Args:
        gates_queue: A deque of gates to be initialized.
        common_basic: A list of common basic events.
        common_gate: A list of common gates.
        fault_tree: The fault tree container of all events and constructs.
    """
    # Get an intermediate gate to initialize breadth-first
    # print(len(fault_tree.basic_events))
    gate = gates_queue.popleft()
    # print(gate)
    num_arguments = fault_tree.factors.get_num_args(gate)
    # print(num_arguments)
    # print(gate.num_arguments())
    ancestors = None  # needed for cycle prevention
    max_tries = len(common_gate)  # the number of maximum tries
    num_tries = 0  # the number of tries to get a common gate

    # pylint: disable=too-many-nested-blocks
    # This code is both hot and coupled for performance reasons.
    # There may be a better solution than the current approach.
    while gate.num_arguments() < num_arguments:
        s_percent = random.random()  # sample percentage of gates
        s_common = random.random()  # sample the reuse frequency

        # Case when the number of basic events is already satisfied
        if len(fault_tree.basic_events) == fault_tree.factors.num_basic:
            s_common = 0  # use only common nodes

        if s_percent < fault_tree.factors.get_percent_gate():
            # Create a new gate or use a common one
            if s_common < fault_tree.factors.common_g and num_tries < max_tries:
                # Lazy evaluation of ancestors
                if not ancestors:
                    ancestors = gate.get_ancestors()

                for random_gate in candidate_gates(common_gate):
                    num_tries += 1
                    if num_tries >= max_tries:
                        break
                    if random_gate in gate.g_arguments or random_gate is gate:
                        continue
                    if (not random_gate.g_arguments or
                            random_gate not in ancestors):
                        if not random_gate.parents:
                            gates_queue.append(random_gate)
                        gate.add_argument(random_gate)
                        break
            else:
                new_gate = fault_tree.construct_gate()
                gate.add_argument(new_gate)
                gates_queue.append(new_gate)
        else:
            gate.add_argument(
                choose_basic_event(s_common, common_basic, fault_tree))

    correct_for_exhaustion(gates_queue, common_gate, fault_tree)


def distribute_house_events(fault_tree):
    """Distributes house events to already initialized gates.

    Args:
        fault_tree: The fault tree container of all events and constructs.
    """
    while len(fault_tree.house_events) < fault_tree.factors.num_house:
        target_gate = random.choice(fault_tree.gates)
        if (target_gate is not fault_tree.top_gate and
                target_gate.operator != "xor" and
                target_gate.operator != "not"):
            target_gate.add_argument(fault_tree.construct_house_event())


def generate_ccf_groups(fault_tree):
    """Creates CCF groups from the existing basic events.

    Args:
        fault_tree: The fault tree container of all events and constructs.
    """
    if fault_tree.factors.num_ccf:
        num_ccf_total = fault_tree.factors.num_ccf
        # print("num_ccf", num_ccf_total)
        members = fault_tree.basic_events[:]
        # print("members", len(members))
        random.shuffle(members)
        first_mem = 0
        last_mem = 0
        while len(fault_tree.ccf_groups) < fault_tree.factors.num_ccf:
            max_args = int(2 * fault_tree.factors.num_args - 2)
            max_args = fault_tree.factors.ccf_size
            # print(max_args)
            group_size = random.randint(2, max_args)
            # print(group_size)
            last_mem = first_mem + group_size
            if last_mem > len(members):
                break
            fault_tree.construct_ccf_group(members[first_mem:last_mem])
            # print("fir",members)
            first_mem = last_mem
        fault_tree.non_ccf_events = members[first_mem:]




def generate_fault_tree(ft_name, root_name, factors):
    """Generates a fault tree of specified complexity.

    The Factors class attributes are used as parameters for complexity.

    Args:
        ft_name: The name of the fault tree.
        root_name: The name for the root gate of the fault tree.
        factors: Factors for fault tree generation.

    Returns:
        Top gate of the created fault tree.
    """
    fault_tree = GeneratorFaultTree(ft_name, factors)
    fault_tree.construct_top_gate(root_name)

    # Estimating the parameters
    num_gate = factors.get_num_gate()
    num_basic_events = factors.num_basic
    num_common_basic = factors.get_num_common_basic(num_gate)
    num_common_gate = factors.get_num_common_gate(num_gate)
    common_basic = [
        fault_tree.construct_basic_event() for _ in range(num_common_basic)
    ]
    common_gate = [fault_tree.construct_gate() for _ in range(num_common_gate)]

    # Container for not yet initialized gates
    # A deque is used to traverse the tree breadth-first
    gates_queue = deque()
    gates_queue.append(fault_tree.top_gate)
    while gates_queue:
        init_gates(gates_queue, common_basic, common_gate, fault_tree)

    assert (not [x for x in fault_tree.basic_events if x.is_orphan()])
    assert (not [
        x for x in fault_tree.gates
        if x.is_orphan() and x is not fault_tree.top_gate
    ])

    distribute_house_events(fault_tree)
    generate_ccf_groups(fault_tree)
    return fault_tree


def write_info(fault_tree, printer, seed):
    """Writes the information about the setup for fault tree generation.

    Args:
        fault_tree: A full, valid, well-formed fault tree.
        printer: The output stream.
        seed: The seed of the pseudo-random number generator.
    """
    factors = fault_tree.factors
    printer('<?xml version="1.0"?>')
    printer('<!--')
    printer('This is a description of the auto-generated fault tree')
    printer('with the following parameters:\n')
    printer('The fault tree name: ', fault_tree.name)
    printer('The root gate name: ', fault_tree.top_gate.name)
    printer()
    printer('The seed of the random number generator: ', seed)
    printer('The number of basic events: ', factors.num_basic)
    printer('The number of house events: ', factors.num_house)
    printer('The number of CCF groups: ', factors.num_ccf)
    printer('The average number of gate arguments: ', factors.num_args)
    printer('The weights of gate types [AND, OR, K/N, NOT, XOR]: ',
            factors.get_gate_weights())
    printer('Percentage of common basic events per gate: ', factors.common_b)
    printer('Percentage of common gates per gate: ', factors.common_g)
    printer('The avg. number of parents for common basic events: ',
            factors.parents_b)
    printer('The avg. number of parents for common gates: ', factors.parents_g)
    printer('Maximum probability for basic events: ', factors.max_prob)
    printer('Minimum probability for basic events: ', factors.min_prob)
    printer('-->')

def write_info_JSON_printer(fault_tree, printer, seed):
    """Writes the information about the setup for fault tree generation in SAPHIRE Json format.

    Args:
        fault_tree: A full, valid, well-formed fault tree.
        printer: The output stream.
        seed: The seed of the pseudo-random number generator.
    """
    factors = fault_tree.factors
    printer('{')
    printer('"version": "1.0",')
    printer('"saphiresolveinput": {')
    printer('"header": {')
    printer('"projectpath": "Edatadrive82NCState-NEUPModelsGenericPWR Model-debug",')
    printer('"eventtree": {')
    printer('"name": "",')
    printer('"number": 0,')
    printer('"initevent": 0,')
    printer('"seqphase": 1')
    printer('},')
    printer('"flagnum": 0,')
    printer('"ftcount": 1,')
    printer('"fthigh": 139,')
    printer('"sqcount": 0,')
    printer('"sqhigh": 0,')
    printer('"becount":', 4 + factors.num_basic,",")
    #printer('"behigh":', max(
    # len(basic_events)), ",")
    printer('"behigh": 99996,')
    printer('"mthigh": 1,')
    printer('"phhigh": 1,')
    printer('"truncparam": {')
    printer('"ettruncopt": "NormalProbCutOff",')
    printer('"fttruncopt": "GlobalProbCutOff",')
    printer('"sizeopt": "ENoTrunc",')
    printer('"ettruncval": 1.000E-14,')
    printer('"fttruncval": 1.000E-14,')
    printer('"sizeval": 99,')
    printer('"transrepl": false,')
    printer('"transzones": false,')
    printer('"translevel": 0,')
    printer('"usedual": false,')
    printer('"dualcutoff": 0.000E+00')
    printer('},')
    printer('"workspacepair": {')
    printer('"ph": 1,')
    printer('"mt": 1')
    printer('},')
    printer('"iworkspacepair": {')
    printer('"ph": 1,')
    printer('"mt": 1')
    printer('}')
    printer('},')
    printer('"sysgatelist": [')
    printer('{')
    printer('"name":','\"',fault_tree.name,'\",')
    printer('"id": 139,')
    printer('"gateid":', fault_tree.top_gate.name.strip('root'),",")
    printer('"gateorig":', fault_tree.top_gate.name.strip('root'),",")
    printer('"gatepos": 0,')
    printer('"eventid": 99996,')
    printer('"gatecomp":', fault_tree.top_gate.name.strip('root'),",")
    printer('"comppos": 0,')
    printer('"compflag": " ",')
    printer('"gateflag": " ",')
    printer('"gatet": " ",')
    printer('"bddsuccess": false,')
    printer('"done": false')
    printer('}')
    printer('],')
    printer('"faulttreelist": [')
    printer('{')
    printer('"ftheader": {')
    printer('"ftid": 139,')
    printer('"gtid":', fault_tree.top_gate.name.strip('root'),',')
    printer('"evid": 99996,')
    printer('"defflag": 0,')
    printer('"numgates":',len(fault_tree.gates), "")
    printer('},')
    printer('"gatelist": [')

def write_info_SAPHSOLVE_JSON_object(fault_tree, base, seed):
    # with open("base-json.json", "r") as f:
    #     base = json.load(f)
    with open("base-json.json", "r") as f:
        base = json.load(f)
    factors = fault_tree.factors
        # @BasicEvent(event)
    test = False
    base['saphiresolveinput']['header'][
        'projectpath'] = '"projectpath": "Edatadrive82NCState-NEUPModelsGenericPWR Model-debug",'
    base['saphiresolveinput']['header']['eventtree']['name'] = '"",'
    base['saphiresolveinput']['header']['eventtree']['number'] = 0
    base['saphiresolveinput']['header']['eventtree']['initevent'] = 0
    base['saphiresolveinput']['header']['eventtree']['seqphase'] = 1
    base['saphiresolveinput']['header']['flagnum'] = 0
    base['saphiresolveinput']['header']['ftcount'] = 1
    base['saphiresolveinput']['header']['fthigh'] = 139
    base['saphiresolveinput']['header']['sqcount'] = 0
    base['saphiresolveinput']['header']['sqhigh'] = 0
    base['saphiresolveinput']['header']['becount'] = 4 + factors.num_basic + factors.num_ccf
    base['saphiresolveinput']['header']['behigh'] = 99996
    base['saphiresolveinput']['header']['mthigh'] = 1
    base['saphiresolveinput']['header']['phhigh'] = 1
    base['saphiresolveinput']['header']['truncparam']['ettruncopt'] = 'NormalProbCutOff'
    base['saphiresolveinput']['header']['truncparam']['fttruncopt'] = 'GlobalProbCutOff'
    base['saphiresolveinput']['header']['truncparam']['sizeopt'] = 'ENoTrunc'
    base['saphiresolveinput']['header']['truncparam']['ettruncval'] = 1.000E-14
    base['saphiresolveinput']['header']['truncparam']['fttruncval'] = 1.000E-14
    base['saphiresolveinput']['header']['truncparam']['sizeval'] = 99
    base['saphiresolveinput']['header']['truncparam']['transrepl'] = test
    base['saphiresolveinput']['header']['truncparam']['transzones'] = test
    base['saphiresolveinput']['header']['truncparam']['translevel'] = 0
    base['saphiresolveinput']['header']['truncparam']['usedual'] = test
    base['saphiresolveinput']['header']['truncparam']['dualcutoff'] = 0.000E+00
    base['saphiresolveinput']['header']['workspacepair']['ph'] = 1
    base['saphiresolveinput']['header']['workspacepair']['mt'] = 1
    base['saphiresolveinput']['header']['iworkspacepair']['ph'] = 1
    base['saphiresolveinput']['header']['iworkspacepair']['mt'] = 1
    """sysgatelist"""
    base['saphiresolveinput']['sysgatelist'][0]['name'] = fault_tree.name
    base['saphiresolveinput']['sysgatelist'][0]['id'] = 139
    base['saphiresolveinput']['sysgatelist'][0]['gateid'] = int(fault_tree.top_gate.name.strip('"root'))
    base['saphiresolveinput']['sysgatelist'][0]['gateorig'] = int(fault_tree.top_gate.name.strip('root'))
    base['saphiresolveinput']['sysgatelist'][0]['gatepos'] = 0
    base['saphiresolveinput']['sysgatelist'][0]['eventid'] = 99996
    base['saphiresolveinput']['sysgatelist'][0]['gatecomp'] = int(fault_tree.top_gate.name.strip('root'))
    base['saphiresolveinput']['sysgatelist'][0]['comppos'] = 0
    base['saphiresolveinput']['sysgatelist'][0]['bddsuccess'] = test
    base['saphiresolveinput']['sysgatelist'][0]['done'] = test
    """faulttreelist"""
    base['saphiresolveinput']['faulttreelist'][0]['ftheader']['ftid'] = 139
    base['saphiresolveinput']['faulttreelist'][0]['ftheader']['gtid'] = int(fault_tree.top_gate.name.strip('root'))
    base['saphiresolveinput']['faulttreelist'][0]['ftheader']['evid'] = 99996
    base['saphiresolveinput']['faulttreelist'][0]['ftheader']['defflag'] = 0
    base['saphiresolveinput']['faulttreelist'][0]['ftheader']['numgates'] = len(fault_tree.gates)
    with open("output.json", "w") as f:
         json.dump(base, f, indent=4)

def write_info_OpenPRA_JSON_printer(fault_tree, printer, seed):
    """Writes the information about the setup for fault tree generation in OpenPRA Json format.

    Args:
        fault_tree: A full, valid, well-formed fault tree.
        printer: The output stream.
        seed: The seed of the pseudo-random number generator.
    """
    factors = fault_tree.factors
    printer('{')

def get_size_summary(fault_tree, printer):
    """Gathers information about the size of the fault tree.

    Args:
        fault_tree: A full, valid, well-formed fault tree.
        printer: The output stream.
    """
    gate_count = {'and': 0, 'or': 0, 'atleast': 0, 'not': 0, 'xor': 0}
    for gate in fault_tree.gates:
        gate_count[gate.operator] = gate_count[gate.operator] + 1

    printer('The number of basic events: ', len(fault_tree.basic_events))
    printer('The number of house events: ', len(fault_tree.house_events))
    printer('The number of CCF groups: ', len(fault_tree.ccf_groups))
    printer('The number of gates: ', len(fault_tree.gates))
    printer('    AND gates: ', gate_count['and'])
    printer('    OR gates: ', gate_count['or'])
    printer('    K/N gates: ', gate_count['atleast'])
    printer('    NOT gates: ', gate_count['not'])
    printer('    XOR gates: ', gate_count['xor'])


def calculate_complexity_factors(fault_tree):
    """Computes complexity factors of the generated fault tree.

    Args:
        fault_tree: A full, valid, well-formed fault tree.

    Returns:
        frac_b: fraction of basic events in arguments per gate
        common_b: fraction of common basic events in basic events per gate
        common_g: fraction of common gates in gates per gate
    """
    frac_b = 0
    common_b = 0
    common_g = 0
    for gate in fault_tree.gates:
        num_b_arguments = len(gate.b_arguments)
        num_g_arguments = len(gate.g_arguments)
        frac_b += num_b_arguments / (num_g_arguments + num_b_arguments)
        if gate.b_arguments:
            num_common_b = len([x for x in gate.b_arguments if x.is_common()])
            common_b += num_common_b / num_b_arguments
        if gate.g_arguments:
            num_common_g = len([x for x in gate.g_arguments if x.is_common()])
            common_g += num_common_g / num_g_arguments
    common_b /= len([x for x in fault_tree.gates if x.b_arguments])
    common_g /= len([x for x in fault_tree.gates if x.g_arguments])
    frac_b /= len(fault_tree.gates)
    return frac_b, common_b, common_g


def get_complexity_summary(fault_tree, printer):
    """Gathers information about the complexity factors of the fault tree.

    Args:
        fault_tree: A full, valid, well-formed fault tree.
        printer: The output stream.
    """
    frac_b, common_b, common_g = calculate_complexity_factors(fault_tree)
    shared_b = [x for x in fault_tree.basic_events if x.is_common()]
    shared_g = [x for x in fault_tree.gates if x.is_common()]
    printer('Basic events to gates ratio: ',
            (len(fault_tree.basic_events) / len(fault_tree.gates)))
    printer('The average number of gate arguments: ',
            (sum(x.num_arguments() for x in fault_tree.gates) /
             len(fault_tree.gates)))
    printer('The number of common basic events: ', len(shared_b))
    printer('The number of common gates: ', len(shared_g))
    printer('Percentage of common basic events per gate: ', common_b)
    printer('Percentage of common gates per gate: ', common_g)
    printer('Percentage of arguments that are basic events per gate: ', frac_b)
    if shared_b:
        printer('The avg. number of parents for common basic events: ',
                (sum(x.num_parents() for x in shared_b) / len(shared_b)))
    if shared_g:
        printer('The avg. number of parents for common gates: ',
                (sum(x.num_parents() for x in shared_g) / len(shared_g)))


def write_summary(fault_tree, printer):
    """Writes the summary of the generated fault tree.

    Args:
        fault_tree: A full, valid, well-formed fault tree.
        printer: The output stream.
    """
    printer('<!--\nThe generated fault tree has the following metrics:\n')
    get_size_summary(fault_tree, printer)
    get_complexity_summary(fault_tree, printer)
    printer('-->\n')

def write_summary_JSON(fault_tree, printer):
    """Writes the summary of the generated fault tree.

    Args:
        fault_tree: A full, valid, well-formed fault tree.
        printer: The output stream.
    """
    printer('<!--\nThe generated fault tree has the following metrics:\n')
    get_size_summary(fault_tree, printer)
    get_complexity_summary(fault_tree, printer)
    printer('-->\n')



def manage_cmd_args(argv=None):
    """Manages command-line description and arguments.

    Args:
        argv: An optional list containing the command-line arguments.
            If None, the command-line arguments from sys will be used.

    Returns:
        Arguments that are collected from the command line.

    Raises:
        ArgumentTypeError: There are problems with the arguments.
    """
    # #lizard forgives the function length
    parser = ap.ArgumentParser(description="Complex-Fault-Tree Generator",
                               formatter_class=ap.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--ft-name",
                        type=str,
                        help="name for the fault tree",
                        metavar="NCNAME",
                        default="Autogenerated")
    parser.add_argument("--root",
                        type=str,
                        help="name for the root gate",
                        default=str("root80000"),
                        metavar="NCNAME")
    parser.add_argument("--seed",
                        type=int,
                        default=123,
                        metavar="int",
                        help="seed for the PRNG")
    parser.add_argument("-b",
                        "--num-basic",
                        type=int,
                        help="# of basic events",
                        default=100,
                        metavar="int")
    parser.add_argument("-a",
                        "--num-args",
                        type=float,
                        default=3.0,
                        help="avg. # of gate arguments",
                        metavar="float")
    parser.add_argument("--weights-g",
                        type=str,
                        nargs="+",
                        metavar="float",
                        help="weights for [AND, OR, K/N, NOT, XOR] gates",
                        default=[1, 3, 0, 0, 0])
    parser.add_argument("--common-b",
                        type=float,
                        default=0.1,
                        metavar="float",
                        help="avg. %% of common basic events per gate")
    parser.add_argument("--common-g",
                        type=float,
                        default=0.1,
                        metavar="float",
                        help="avg. %% of common gates per gate")
    parser.add_argument("--parents-b",
                        type=float,
                        default=2,
                        metavar="float",
                        help="avg. # of parents for common basic events")
    parser.add_argument("--parents-g",
                        type=float,
                        default=2,
                        metavar="float",
                        help="avg. # of parents for common gates")
    parser.add_argument("-g",
                        "--num-gate",
                        type=int,
                        default=0,
                        metavar="int",
                        help="# of gates (discards parents-b/g and common-b/g)")
    parser.add_argument("--max-prob",
                        type=float,
                        default=0.001,
                        metavar="float",
                        help="maximum probability for basic events")
    parser.add_argument("--min-prob",
                        type=float,
                        default=0.00001,
                        metavar="float",
                        help="minimum probability for basic events")
    parser.add_argument("--num-house",
                        type=int,
                        help="# of house events",
                        default=0.0,
                        metavar="int")
    parser.add_argument("--num-ccf",
                        type=int,
                        help="# of ccf groups",
                        default=2,
                        metavar="int")
    parser.add_argument("--ccf-size",
                        type=int,
                        help="ccf max size, max in SAPHIRE is 8",
                        default=3,
                        metavar="int")
    parser.add_argument("--ccf-model",
                        type=str,
                        help="ccf model, user should use MGL or alpha-factor",
                        default="alpha-factor")
                        # metavar="int")
    parser.add_argument("-o",
                        "--out",
                        type=str,
                        metavar="path",
                        help="a file to write the fault tree")
    parser.add_argument("--aralia",
                        action="store_true",
                        help="apply the Aralia format to the output")
    parser.add_argument("--SAPHIRE_json_printer",
                        action="store_true",
                        help="apply the SAPHIRE JSON format to the output")
    parser.add_argument("--SAPHIRE_json_object",
                        action="store_true",
                        help="apply the SAPHIRE JSON format to the output")
    parser.add_argument("--OpenPRA_json_printer",
                        action="store_true",
                        help="apply the OpenPRA JSON format to the output")
    parser.add_argument("--nest",
                        action="store_true",
                        help="nest NOT connectives in Boolean formulae")
    args = parser.parse_args(argv)
    return args


def setup_factors(args):
    """Configures the fault generation by assigning factors.

    Args:
        args: Command-line arguments with values for factors.

    Returns:
        Fully initialized Factors object.

    Raises:
        ArgumentTypeError: Problems with the arguments.
        FactorError: Invalid setup for factors.
    """
    random.seed(args.seed)
    factors = Factors()
    factors.set_min_max_prob(args.min_prob, args.max_prob)
    factors.set_common_event_factors(args.common_b, args.common_g,
                                     args.parents_b, args.parents_g)
    factors.set_num_factors(args.num_args, args.num_basic, args.num_house,
                            args.num_ccf,args.ccf_model, args.ccf_size)
    factors.set_gate_weights([float(i) for i in args.weights_g])
    if args.num_gate:
        factors.constrain_num_gate(args.num_gate)
    factors.calculate()
    return factors


def main(argv=None):
    """The main function of the fault tree generator.

    Args:
        argv: An optional list containing the command-line arguments.
            If None, the command-line arguments from sys will be used.

    Raises:
        ArgumentTypeError: There are problems with the arguments.
        FactorError: Invalid setup for factors.
    """
    args = manage_cmd_args(argv)
    factors = setup_factors(args)
    fault_tree = generate_fault_tree(args.ft_name, args.root, factors)
    printer = get_printer(args.out)
    if args.aralia:
        fault_tree.to_aralia(printer)
    elif args.SAPHIRE_json_object:
         write_info_SAPHSOLVE_JSON_object(fault_tree, printer, args.seed)
         fault_tree.to_SAPHIRE_json_object(args.nest)
    elif args.OpenPRA_json_printer:
        write_info_OpenPRA_JSON_printer(fault_tree, printer, args.seed)
        fault_tree.to_OpenPRA_json_printer(printer, args.nest)
        #write_summary(fault_tree, printer)
    elif args.SAPHIRE_json_printer:
        write_info_JSON_printer(fault_tree, printer, args.seed)
        fault_tree.to_SAPHIRE_json_printer(printer, args.nest)
    else:
        write_info(fault_tree, printer, args.seed)
        write_summary(fault_tree, printer)
        fault_tree.to_xml(printer, args.nest)


def get_printer(file_path=None):
    """Returns printer to stream output."""
    destination = open(file_path, 'w') if file_path else sys.stdout

    def _print(*args):
        print(*args, file=destination, sep='')

    return _print


if __name__ == "__main__":
    try:
        main()
    except ap.ArgumentTypeError as err:
        print("Argument Error:\n" + str(err))
        sys.exit(2)
    except FactorError as err:
        print("Error in factors:\n" + str(err))
        sys.exit(1)
