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