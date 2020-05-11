######################################################################
#                    For running as an executable                    #
######################################################################
import argparse
import os
from collections import OrderedDict

import cellmlmanip

import chaste_codegen as cg
from chaste_codegen._script_utils import write_file


# Link names to classes for converting code
TRANSLATORS = OrderedDict([('Chaste', cg.NormalChasteModel),
                           ('ChasteOpt', cg.OptChasteModel),
                           ('CVODE', cg.CvodeChasteModel),
                           ('CVODEWithDataClamp', cg.CvodeWithDataClampModel),
                           ('BackwardsEuler', cg.BackwardEulerModel),
                           ('RushLarsen', cg.RushLarsenModel),
                           ('RushLarsenOpt', cg.RushLarsenOptModel),
                           ('GeneralisedRushLarsen1', cg.GeneralisedRushLarsenFirstOrderModel),
                           ('GeneralisedRushLarsen1Opt', cg.GeneralisedRushLarsenFirstOrderModelOpt),
                           ('GeneralisedRushLarsen2', cg.GeneralisedRushLarsenSecondOrderModel),
                           ('GeneralisedRushLarsen2Opt', cg.GeneralisedRushLarsenSecondOrderModelOpt)])

TRANSLATORS_WITH_MODIFIERS = ('Chaste', 'ChasteOpt', 'CVODE', 'CVODEWithDataClamp')


def chaste_codegen():
    # Store extensions we can use and how to use them, based on extension of given outfile
    extension_lookup = {'.cellml': ['.hpp', '.cpp'], '': ['.hpp', '.cpp'], '.cpp': ['.hpp', '.cpp'],
                        '.hpp': ['.hpp', '.cpp'], '.c': ['.h', '.c'], '.h': ['.h', '.c']}

    # add options for command line interface
    parser = argparse.ArgumentParser(description='Chaste code generation for cellml.')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=cg.__version__))
    parser.add_argument('cellml_file', metavar='cellml_file', help='The cellml file or URI to convert to chaste code')
    parser.add_argument('-t', '--translate-type', choices=list(TRANSLATORS.keys()),
                        default='Chaste', metavar='TYPE', dest='translator_class',
                        help='the type of code to output [default: Chaste].  '
                        'Choices: ' + str(list(TRANSLATORS.keys())))
    parser.add_argument('-o', dest='outfile', metavar='OUTFILE', default=None,
                        help='write program code to OUTFILE '
                             '[default action is to use the input filename with a different extension] '
                             'NOTE: expects provided OUTFILE to have an extension relevant to code being generated '
                             '(e.g. for CHASTE/C++ code: .cpp, .c, .hpp, or .h)')

    group = parser.add_argument_group('Transformations', 'These options control which transformations '
                                      '(typically optimisations) are applied in the generated code')
    group.add_argument('--use-analytic-jacobian', dest='use_analytic_jacobian', default=False,
                       action='store_true', help='use a symbolic Jacobian calculated by SymPy '
                       '(--use-analytic-jacobian can only be used in combination with -t CVODE)')

    group = parser.add_argument_group('Generated code options')
    group.add_argument('-c', default=None, dest='class_name',
                       help='explicitly set the name of the generated class')

    group = parser.add_argument_group('Chaste options', description='Options specific to Chaste code output')
    group.add_argument('-y', '--dll', '--dynamically-loadable', dest='dynamically_loadable',
                       action='store_true', default=False,
                       help='add code to allow the model to be compiled to a shared library and dynamically loaded ')
    group.add_argument('--use-modifiers', dest='use_modifiers',
                       action='store_true', default=False,
                       help='add modifier functions for metadata-annotated variables (except time & stimulus) '
                       'for use in sensitivity analysis. Only works with one of the following translator types (-t): ' +
                       str(TRANSLATORS_WITH_MODIFIERS))

    # process options
    args = parser.parse_args()
    # Check option combinations
    if args.use_analytic_jacobian and not args.translator_class == 'CVODE':
        parser.error('--use-analytic-jacobian can only be used in combination with -t CVODE')
    if args.use_modifiers and args.translator_class not in TRANSLATORS_WITH_MODIFIERS:
        parser.error('--use-modifiers can only be used with one of the following translator types ' +

                     str(TRANSLATORS_WITH_MODIFIERS))

    model = cellmlmanip.load_model(args.cellml_file)
    outfile = args.outfile if args.outfile is not None else os.path.basename(args.cellml_file)
    outfile_path = os.path.dirname(outfile)
    model_file_base_parts = os.path.splitext(os.path.basename(args.cellml_file))
    out_file_base_parts = os.path.splitext(os.path.basename(outfile))
    model_name_from_file = model_file_base_parts[0]
    outfile_base = out_file_base_parts[0]
    outfile_extension = out_file_base_parts[1] if len(out_file_base_parts) > 1 else ''

    if args.class_name is None:
        args.class_name = ('Dynamic' if args.dynamically_loadable else 'Cell') + model_name_from_file + 'FromCellML'

    ext = extension_lookup[outfile_extension]
    # generate code Based on parameters a different class of translator may be used
    chaste_model = TRANSLATORS[args.translator_class](model, outfile_base, header_ext=ext[0], **vars(args))
    chaste_model.generate_chaste_code()

    # Write generated files
    hpp_gen_file_path = \
        os.path.join(outfile_path, outfile_base + ext[0])
    cpp_gen_file_path = \
        os.path.join(outfile_path, outfile_base + ext[1])
    write_file(hpp_gen_file_path, chaste_model.generated_hpp)
    write_file(cpp_gen_file_path, chaste_model.generated_cpp)
