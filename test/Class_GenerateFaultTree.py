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