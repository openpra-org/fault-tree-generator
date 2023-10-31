def main(argv=None):
    """The main function of the fault tree generator_old.

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