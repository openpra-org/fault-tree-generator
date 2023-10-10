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