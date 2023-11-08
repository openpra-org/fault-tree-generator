import random
import signal
from collections import deque

from fault_tree import FaultTree, CCFGroup
from fault_tree.event import Gate, BasicEvent, HouseEvent
from fault_tree.probability import PointEstimate


# Define a timeout handler function
def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")


class GenerativeFaultTree(FaultTree):
    """Specialization of a fault tree for generation purposes.

    The construction of fault tree members are handled through this object.
    It is assumed that no removal is going to happen after construction.

    Args:
        factors: The fault tree generation factors.
    """

    def __init__(self, name, factors, top_gate_name="root", timeout=None):
        """Generates a fault tree of specified complexity factor.

        Args:
            name: The name of the system described by the fault tree container.
            factors: Fully configured generation factors.
            top_gate_name: The name for the top gate.
            timeout: The maximum time allowed for the generation process.
        """
        # Set the timeout signal if a timeout is specified
        if timeout is not None:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

        try:
            super(GenerativeFaultTree, self).__init__(name)
            self.factors = factors
            self.construct_top_gate(top_gate_name)

            # Estimating the parameters
            num_gate = factors.get_num_gate()
            num_common_basic = factors.get_num_common_basic(num_gate)
            num_common_gate = factors.get_num_common_gate(num_gate)
            common_basic = [
                self.construct_basic_event() for _ in range(num_common_basic)
            ]
            common_gate = [self.construct_gate() for _ in range(num_common_gate)]

            # Container for not yet initialized gates
            # A deque is used to traverse the tree breadth-first
            gates_queue = deque()
            gates_queue.append(self.top_gate)
            while gates_queue:
                self.init_gates(gates_queue, common_basic, common_gate)

            assert (not [x for x in self.basic_events if x.is_orphan()])
            assert (not [
                x for x in self.gates
                if x.is_orphan() and x is not self.top_gate
            ])

            self.distribute_house_events()
            self.generate_ccf_groups()

        finally:
            # Disable the alarm after the operation is complete
            if timeout is not None:
                signal.alarm(0)

    def construct_top_gate(self, root_name="root"):
        """Constructs and assigns a new gate suitable for being a root.

        Args:
            root_name: Unique name for the root gate.
        """
        assert not self.top_gate and not self.top_gates
        operator = self.factors.get_random_operator()
        while operator in ("atleast", "not"):
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
        return gate

    def construct_basic_event(self):
        """Constructs a basic event with a unique identifier.

        Returns:
            A fully initialized basic event with a random probability.
        """
        basic_event = BasicEvent(
            "B" + str(len(self.basic_events) + 1),
            PointEstimate(value=random.uniform(self.factors.min_prob, self.factors.max_prob)))
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
        ccf_group = CCFGroup("CCF" + str(len(self.ccf_groups) + 1))
        self.ccf_groups.append(ccf_group)
        ccf_group.members = members
        ccf_group.prob = random.uniform(self.factors.min_prob,
                                        self.factors.max_prob)
        ccf_group.model = "MGL"
        levels = random.randint(2, len(members))
        ccf_group.factors = [random.uniform(0.1, 1) for _ in range(levels - 1)]
        return ccf_group

    def init_gates(self, gates_queue, common_basic, common_gate):
        """Initializes gates and other basic events.

        Args:
            gates_queue: A deque of gates to be initialized.
            common_basic: A list of common basic events.
            common_gate: A list of common gates.
        """
        while gates_queue:
            # Get an intermediate gate to initialize breadth-first
            gate = gates_queue.popleft()

            if gate.operator == "not":
                # "not" gates should have exactly one argument
                if gate.num_arguments() == 0:
                    gate.add_argument(self.choose_basic_event(random.random(), common_basic))
                continue  # Skip the rest of the loop for "not" gates





            max_tries = len(common_gate)  # the number of maximum tries
            num_tries = 0  # the number of tries to get a common gate

            ancestors = None

            num_arguments = self.factors.get_num_args(gate)
            while gate.num_arguments() < num_arguments:

                s_percent = random.random()  # sample percentage of gates
                s_common = random.random()  # sample the reuse frequency

                # Case when the number of basic events is already satisfied
                if len(self.basic_events) >= self.factors.num_basic:
                    s_common = 1  # use only common nodes

                if s_percent < self.factors.get_percent_gate():
                    # Create a new gate or use a common one
                    if s_common < self.factors.common_g:
                        # Lazy evaluation of ancestors
                        if not ancestors:
                            ancestors = gate.get_ancestors()

                        for random_gate in GenerativeFaultTree.candidate_gates(common_gate):
                            # if (random_gate is gate) or (random_gate in gate.g_arguments):
                            #     continue
                            #
                            # if not random_gate.g_arguments or random_gate not in ancestors:
                            #     if not random_gate.parents:
                            #         gates_queue.append(random_gate)
                            #     gate.add_argument(random_gate)
                            #     break
                            if (random_gate is not gate) and (random_gate not in gate.g_arguments) and (random_gate not in ancestors):
                                if not random_gate.parents:
                                    gates_queue.append(random_gate)
                                gate.add_argument(random_gate)
                                break
                    else:
                        new_gate = self.construct_gate()
                        gate.add_argument(new_gate)
                        gates_queue.append(new_gate)
                else:
                    # Choose a basic event that is not already a child of the gate
                    basic_event = self.choose_basic_event(s_common, common_basic)
                    if basic_event not in gate.b_arguments:
                        gate.add_argument(basic_event)

            # If the number of basic events has reached the desired count, exit the loop
            if len(self.basic_events) >= self.factors.num_basic and not gates_queue:
                break

        self.correct_for_exhaustion(gates_queue, common_gate)

    @staticmethod
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
            yield i

        single_parent = [x for x in common_gate if len(x.parents) == 1]
        random.shuffle(single_parent)
        for i in single_parent:
            yield i

        multi_parent = [x for x in common_gate if len(x.parents) > 1]
        random.shuffle(multi_parent)
        for i in multi_parent:
            yield i

    def correct_for_exhaustion(self, gates_queue, common_gate):
        """Corrects the generation for queue exhaustion.

        Corner case when not enough new basic events initialized,
        but there are no more intermediate gates to use
        due to a big ratio or just random accident.

        Args:
            gates_queue: A deque of gates to be initialized.
            common_gate: A list of common gates.
        """
        if gates_queue:
            return
        if len(self.basic_events) < self.factors.num_basic:
            # Initialize one more gate
            # by randomly choosing places in the fault tree.
            random_gate = random.choice(self.gates)
            while (random_gate.operator == "not" or random_gate.operator == "xor" or
                   random_gate in common_gate):
                random_gate = random.choice(self.gates)
            new_gate = self.construct_gate()
            random_gate.add_argument(new_gate)
            gates_queue.append(new_gate)

    def choose_basic_event(self, s_common, common_basic):
        """Creates a new basic event or uses a common one for gate arguments.

        Args:
            s_common: Sampled factor to choose common basic events.
            common_basic: A list of common basic events to choose from.

        Returns:
            Basic event argument for a gate.
        """
        if s_common >= self.factors.common_b or not common_basic:
            return self.construct_basic_event()

        orphans = [x for x in common_basic if not x.parents]
        if orphans:
            return random.choice(orphans)

        single_parent = [x for x in common_basic if len(x.parents) == 1]
        if single_parent:
            return random.choice(single_parent)

        return random.choice(common_basic)

    def distribute_house_events(self):
        """Distributes house events to already initialized gates."""
        while len(self.house_events) < self.factors.num_house:
            target_gate = random.choice(self.gates)
            if (target_gate is not self.top_gate and
                    target_gate.operator != "xor" and
                    target_gate.operator != "not"):
                target_gate.add_argument(self.construct_house_event())

    def generate_ccf_groups(self):
        """Creates CCF groups from the existing basic events.
        """
        if self.factors.num_ccf:
            members = self.basic_events[:]
            random.shuffle(members)
            first_mem = 0
            last_mem = 0
            while len(self.ccf_groups) < self.factors.num_ccf:
                max_args = int(2 * self.factors.num_args - 2)
                group_size = random.randint(2, max_args)
                last_mem = first_mem + group_size
                if last_mem > len(members):
                    break
                self.construct_ccf_group(members[first_mem:last_mem])
                first_mem = last_mem
            self.non_ccf_events = members[first_mem:]
