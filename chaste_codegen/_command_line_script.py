######################################################################
#                    For running as an executable                    #
######################################################################
import argparse
import os
from collections import OrderedDict

import chaste_codegen as cg
from chaste_codegen._script_utils import write_file
from chaste_codegen.model_with_conversions import load_model_with_conversions


# Link names to classes for converting code
# The fields in the order dict as as follows:
# (<name of model type>, <default calss name postfix>, <default file name prostfix>, <can be used with modifiers>)
# pass --name_of_model_type to select this model type
TRANSLATORS = OrderedDict(
    [('normal', (cg.NormalChasteModel, 'FromCellML', '', True)),
     ('cvode', (cg.CvodeChasteModel, 'FromCellMLCvode', 'Cvode', True)),
     ('cvode-data-clamp', (cg.CvodeWithDataClampModel, 'FromCellMLCvodeDataClamp', 'CvodeDataClamp', True)),
     ('backward-euler', (cg.BackwardEulerModel, 'FromCellMLBackwardEuler', 'BackwardEuler', False)),
     ('rush-larsen', (cg.RushLarsenModel, 'FromCellMLRushLarsen', 'RushLarsen', False)),
     ('grl1', (cg.GeneralisedRushLarsenFirstOrderModel, 'FromCellMLGRL1', 'GRL1', False)),
     ('grl2', (cg.GeneralisedRushLarsenSecondOrderModel, 'FromCellMLGRL2', 'GRL2', False))])

TRANSLATORS_OPT = OrderedDict(
    [('normal', (cg.OptChasteModel, 'FromCellMLOpt', 'Opt', True)),
     ('cvode', (cg.OptCvodeChasteModel, 'FromCellMLCvodeOpt', 'CvodeOpt', True)),
     ('rush-larsen', (cg.RushLarsenOptModel, 'FromCellMLRushLarsenOpt', 'RushLarsenOpt', False)),
     ('grl1', (cg.GeneralisedRushLarsenFirstOrderModelOpt, 'FromCellMLGRL1Opt', 'GRL1', False)),
     ('grl2', (cg.GeneralisedRushLarsenSecondOrderModelOpt, 'FromCellMLGRL2Opt', 'GRL2', False))])

TRANSLATORS_WITH_MODIFIERS = tuple('--' + t for t in TRANSLATORS if TRANSLATORS[t][3])


# Store extensions we can use and how to use them, based on extension of given outfile
EXTENSION_LOOKUP = {'.cellml': ['.hpp', '.cpp'], '': ['.hpp', '.cpp'], '.cpp': ['.hpp', '.cpp'],
                    '.hpp': ['.hpp', '.cpp'], '.c': ['.h', '.c'], '.h': ['.h', '.c']}


def chaste_codegen():
    # add options for command line interface
    parser = argparse.ArgumentParser(description='Chaste code generation for cellml.')
    # Options for added pycml backwards compatibility, these are now always on
    parser.add_argument('--Wu', '--warn-on-units-errors', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-A', '--fully-automatic', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--expose-annotated-variables', action='store_true', help=argparse.SUPPRESS)

    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=cg.__version__))
    parser.add_argument('cellml_file', metavar='cellml_file', help='The cellml file or URI to convert to chaste code')

    group = parser.add_argument_group('ModelTypes', 'The different types of solver approach for which code can be '
                                      'generated; if no model type is set, "normal" models are generated')

    for k in TRANSLATORS:
        group.add_argument('--' + k, help='Generate ' + k + ' model type', action='store_true')

    group = parser.add_argument_group('Transformations', 'These options control which transformations '
                                      '(typically optimisations) are applied in the generated code')
    group.add_argument('-j', '--use-analytic-jacobian', dest='use_analytic_jacobian', default=False,
                       action='store_true', help='use a symbolic Jacobian calculated by SymPy '
                       '(--use-analytic-jacobian only works in combination with --cvode'
                       ' and is ignored for other model types)')

    group = parser.add_argument_group('Generated code options')
    group.add_argument('-o', dest='outfile', metavar='OUTFILE', default=None,
                       help='write program code to OUTFILE '
                            '[default action is to use the input filename with a different extension] '
                            'NOTE: expects provided OUTFILE to have an extension relevant to code being generated '
                            '(e.g. for CHASTE/C++ code: .cpp, .c, .hpp, or .h)')
    group.add_argument('--output-dir', action='store', help="directory to place output files in", default=None)
    group.add_argument('--show-outputs', action='store_true', default=False,
                       help="don't actually generate code, just show what files would be generated, one per line")

    group.add_argument('-c', default=None, dest='cls_name',
                       help='explicitly set the name of the generated class')
    group.add_argument('-q', '--quiet', action='store_true', default=False,
                       help="quiet operation, don't print informational messages to screen")

    group = parser.add_argument_group('Chaste options', description='Options specific to Chaste code output')
    group.add_argument('-y', '--dll', '--dynamically-loadable', dest='dynamically_loadable',
                       action='store_true', default=False,
                       help='add code to allow the model to be compiled to a shared library and dynamically loaded ')
    group.add_argument('--opt', action='store_true', default=False,
                       help="apply default optimisations to all generated code")
    group.add_argument('-m', '--use-modifiers', dest='modifiers',
                       action='store_true', default=False,
                       help='add modifier functions for metadata-annotated variables (except time & stimulus) '
                       'for use in sensitivity analysis. Only works with one of the following model types and is '
                       'ignored for others: ' +
                       str(TRANSLATORS_WITH_MODIFIERS))

    # process options
    args = parser.parse_args()
    if not os.path.isfile(args.cellml_file):
        raise ValueError("Could not find cellml file %s " % args.cellml_file)
    if args.outfile is not None and args.output_dir is not None:
        raise ValueError("-o and --output-dir cannot be used together!")

    # if no model type is set assume normal
    args.normal = args.normal or not any([getattr(args, model_type.replace('-', '_')) for model_type in TRANSLATORS])

    # create list of translators to apply
    translators = []
    for model_type in TRANSLATORS:
        use_translator_class = getattr(args, model_type.replace('-', '_'))
        if use_translator_class:
            # if -o or dynamically_loadable is selected with opt, only convert opt model type
            if not args.opt or (not args.outfile and not args.dynamically_loadable):
                translators.append(TRANSLATORS[model_type])
            if args.opt and model_type in TRANSLATORS_OPT:
                translators.append(TRANSLATORS_OPT[model_type])

    # An outfile cannot be set with multiple translations
    if args.outfile and len(translators) > 1:
        raise ValueError("-o cannot be used when multiple model types have been selected!")
    # Dynamically loadable models can only be built one at a time

    if args.dynamically_loadable and len(translators) > 1:
        raise ValueError("Only one model type may be specified if creating a dynamic library!")

    if not args.show_outputs:
        # Load model once, not once per translator, but only if we're actually generating code
        model = load_model_with_conversions(args.cellml_file, use_modifiers=args.modifiers, quiet=args.quiet)

    for translator in translators:
        # Make sure modifiers are only passed to models which can generate them
        args.use_modifiers = args.modifiers and translator[3]

        translator_class = translator[0]
        outfile_path, model_name_from_file, outfile_base, ext = \
            get_outfile_parts(args.outfile, args.output_dir, args.cellml_file)
        if args.cls_name is not None:
            args.class_name = args.cls_name
        else:
            args.class_name = ('Dynamic' if args.dynamically_loadable else 'Cell') + model_name_from_file +\
                translator[1]

        if not args.outfile:
            outfile_base += translator[2]

        # generate code Based on parameters a different class of translator may be used
        hpp_gen_file_path = os.path.join(outfile_path, outfile_base + ext[0])
        cpp_gen_file_path = os.path.join(outfile_path, outfile_base + ext[1])
        if args.show_outputs:
            print(cpp_gen_file_path)
            print(hpp_gen_file_path)
        else:
            with translator_class(model, outfile_base, header_ext=ext[0], **vars(args)) as chaste_model:
                chaste_model.generate_chaste_code()

                # Write generated files
                write_file(hpp_gen_file_path, chaste_model.generated_hpp)
                write_file(cpp_gen_file_path, chaste_model.generated_cpp)


def get_outfile_parts(outfile, output_dir, cellml_file):
    if outfile is None:
        outfile = cellml_file

    if output_dir is None:
        outfile_path = os.path.dirname(os.path.abspath(outfile))
    else:
        outfile_path = os.path.abspath(output_dir)

    model_file_base_parts = os.path.splitext(os.path.basename(cellml_file))
    out_file_base_parts = os.path.splitext(os.path.basename(outfile))
    model_name_from_file = model_file_base_parts[0]
    outfile_base = out_file_base_parts[0]
    outfile_extension = out_file_base_parts[1] if len(out_file_base_parts) > 1 else ''
    ext = EXTENSION_LOOKUP[outfile_extension]
    return outfile_path, model_name_from_file, outfile_base, ext
