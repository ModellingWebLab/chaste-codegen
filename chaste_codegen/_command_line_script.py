######################################################################
#                    For running as an executable                    #
######################################################################
import argparse
import os
from collections import OrderedDict

import chaste_codegen as cg
from chaste_codegen import LOGGER, CodegenError, load_model_with_conversions
from chaste_codegen._lookup_tables import DEFAULT_LOOKUP_PARAMETERS
from chaste_codegen._script_utils import write_file


# Link names to classes for converting code
# The fields in the order dict as as follows:
# (<command_line_tag> (<class name>, <default class postfix>, <default file postfix>, <can be used with modifiers>))

# pass --<command_line_tag> to select this model type

TRANSLATORS = OrderedDict(
    [('normal', (cg.NormalChasteModel, 'FromCellML', '', True, '')),
     ('cvode', (cg.CvodeChasteModel, 'FromCellMLCvode', 'Cvode', True, '')),
     ('cvode-data-clamp', (cg.CvodeChasteModel, 'FromCellMLCvodeDataClamp', 'CvodeDataClamp', True, '')),
     ('backward-euler', (cg.BackwardEulerModel, 'FromCellMLBackwardEuler', 'BackwardEuler', False, '')),
     ('rush-larsen', (cg.RushLarsenModel, 'FromCellMLRushLarsen', 'RushLarsen', False, '')),
     ('grl1', (cg.GeneralisedRushLarsenFirstOrderModel, 'FromCellMLGRL1', 'GRL1', False, '')),
     ('grl2', (cg.GeneralisedRushLarsenSecondOrderModel, 'FromCellMLGRL2', 'GRL2', False, '')),
     ('rush-larsen-labview', (cg.RushLarsenLabview, '', '', False,
                              ' in mastrcriptRT with added injection current(i_inj)')),
     ('rush-larsen-c', (cg.RushLarsenC, '', '', False, ' in C with added injection current(i_inj)'))])

TRANSLATORS_OPT = OrderedDict(
    [('normal', (cg.OptChasteModel, 'FromCellMLOpt', 'Opt', True, '')),
     ('cvode', (cg.OptCvodeChasteModel, 'FromCellMLCvodeOpt', 'CvodeOpt', True, '')),
     ('cvode-data-clamp', (cg.OptCvodeChasteModel, 'FromCellMLCvodeDataClampOpt', 'CvodeDataClampOpt', True, '')),
     ('backward-euler', (cg.BackwardEulerOptModel, 'FromCellMLBackwardEulerOpt', 'BackwardEulerOpt', False, '')),
     ('rush-larsen', (cg.RushLarsenOptModel, 'FromCellMLRushLarsenOpt', 'RushLarsenOpt', False, '')),
     ('grl1', (cg.GeneralisedRushLarsenFirstOrderModelOpt, 'FromCellMLGRL1Opt', 'GRL1', False, '')),
     ('grl2', (cg.GeneralisedRushLarsenSecondOrderModelOpt, 'FromCellMLGRL2Opt', 'GRL2', False, ''))])

TRANSLATORS_WITH_MODIFIERS = tuple('--' + t for t in TRANSLATORS if TRANSLATORS[t][3])


# Store extensions we can use and how to use them, based on extension of given outfile
EXTENSION_LOOKUP_FROM_OUTFILE = {'.cellml': ['.hpp', '.cpp'], '': ['.hpp', '.cpp'], '.cpp': ['.hpp', '.cpp'],
                                 '.hpp': ['.hpp', '.cpp'], '.c': ['.h', '.c'], '.h': ['.h', '.c']}

EXTENSION_LOOKUP_FROM_CONVERSION_TYPE = {cg.RushLarsenC: ['.h', '.c'], cg.RushLarsenLabview: [None, '.txt']}


def print_default_lookup_params():
    params = ''
    for param in DEFAULT_LOOKUP_PARAMETERS:
        params += '--lookup-table %s' % (" ".join(map(str, param)))
    return params


def skip_conversion(args):
    return args.rush_larsen_labview or args.rush_larsen_c


def process_command_line():
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
        group.add_argument('--' + k, help='Generate ' + k + ' model type' + TRANSLATORS[k][4], action='store_true')

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
    group.add_argument('--skip-singularity-fixes', action='store_true', default=False,
                       help="skip singularity fixes in Goldman-Hodgkin-Katz (GHK) equations.")

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
    lut_metavar = ("<metadata tag>", "min", "max", "step")
    group.add_argument('--lookup-table', nargs=4, default=None, action='append', metavar=lut_metavar,
                       help='Specify variable (using a metadata tag) and ranges for which to generate lookup tables '
                            '(optional). --lookup-table can be added multiple times to indicate multiple lookup tables'
                            '. Please note: Can only be used in combination with --opt. If the arguments are omitted, '
                            'following defaults will be used: %s.' % print_default_lookup_params())
    group.add_argument('--use-model-factory', action='store_true', default=False,
                       help='Make use of ModelFactoy method to allow creating models by name. '
                       'Requires ModelFactory.hpp/cpp found in the ApPredict project.')

    # process options
    args = parser.parse_args()

    if not os.path.isfile(args.cellml_file):
        raise CodegenError("Could not find cellml file %s " % args.cellml_file)
    if args.outfile is not None and args.output_dir is not None:
        raise CodegenError("-o and --output-dir cannot be used together!")
    if args.lookup_table and not args.opt:
        raise CodegenError("Can only use lookup tables in combination with --opt")

    # make sure --lookup-table entries are 1 string and 3 floats
    if args.lookup_table is None:
        args.lookup_table = DEFAULT_LOOKUP_PARAMETERS
    else:
        for _, lut in enumerate(args.lookup_table):
            lut_params_mgs = \
                'Lookup tables are expecting the following %s values: %s' % (len(lut_metavar), " ".join(lut_metavar))
            assert len(lut) == len(lut_metavar), lut_params_mgs
            try:  # first argument is a string
                float(lut[0])
                is_float = True
            except ValueError:
                is_float = False  # We are expecting this to be a string

            if is_float:
                raise CodegenError(lut_params_mgs)

            for i in range(1, len(lut)):  # next 3 arguments are floats
                try:
                    lut[i] = float(lut[i])
                except ValueError:
                    raise CodegenError(lut_params_mgs)

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
        raise CodegenError("-o cannot be used when multiple model types have been selected!")
    # Dynamically loadable models can only be built one at a time

    if args.dynamically_loadable and len(translators) > 1:
        raise CodegenError("Only one model type may be specified if creating a dynamic library!")

    if not args.show_outputs:
        # Load model once, not once per translator, but only if we're actually generating code
        model = load_model_with_conversions(args.cellml_file, use_modifiers=args.modifiers, quiet=args.quiet,
                                            skip_singularity_fixes=args.skip_singularity_fixes,
                                            skip_conversions=skip_conversion(args))

    if len(translators) > 1 and skip_conversion(args):
        raise CodegenError(('--rush-larsen-labview and --rush-larsen-c '
                            'cannot be used in combination with other model convertion types'))

    for translator in translators:
        # Make sure modifiers are only passed to models which can generate them
        args.use_modifiers = args.modifiers and translator[3]

        translator_class = translator[0]
        outfile_path, model_name_from_file, outfile_base, ext = \
            get_outfile_parts(args.outfile, args.output_dir, args.cellml_file, translator_class)

        ext = ext if ext else translator_class.DEFAULT_EXTENSIONS

        if args.cls_name is not None:
            args.class_name = args.cls_name
        else:
            args.class_name = ('Dynamic' if args.dynamically_loadable else 'Cell') + model_name_from_file +\
                translator[1]

        args.cellml_base = outfile_base
        if not args.outfile:
            outfile_base += translator[2]

        # generate code Based on parameters a different class of translator may be used
        get_files = []
        for ex in ext:
            if ex is not None:
                get_files.append(os.path.join(outfile_path, outfile_base + ex))

        if args.show_outputs:
            for file in get_files:
                print(file)
        else:
            with translator_class(model, outfile_base, header_ext=ext[0], **vars(args)) as chaste_model:
                chaste_model.generate_chaste_code()

                for file, code in zip(get_files, chaste_model.generated_code):
                    write_file(file, code)


def get_outfile_parts(outfile, output_dir, cellml_file, translator):
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
    if translator in EXTENSION_LOOKUP_FROM_CONVERSION_TYPE:
        ext = EXTENSION_LOOKUP_FROM_CONVERSION_TYPE[translator]
    else:
        ext = EXTENSION_LOOKUP_FROM_OUTFILE[outfile_extension]
    return outfile_path, model_name_from_file, outfile_base, ext


def chaste_codegen():
    try:
        process_command_line()
    except CodegenError as e:
        LOGGER.error(e, exc_info=False)
