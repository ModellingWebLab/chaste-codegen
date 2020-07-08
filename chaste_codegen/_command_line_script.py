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
TRANSLATORS = OrderedDict([('normal', (cg.NormalChasteModel, 'FromCellML', '')),
                           ('opt', (cg.OptChasteModel, 'FromCellMLOpt', 'Opt')),
                           ('cvode', (cg.CvodeChasteModel, 'FromCellMLCvode', 'Cvode')),
                           ('cvode-data-clamp', (cg.CvodeWithDataClampModel, 'CvodeDataClamp', 'CvodeDataClamp')),
                           ('backward-euler', (cg.BackwardEulerModel, 'FromCellMLBackwardEuler', 'BackwardEuler')),
                           ('rush-larsen', (cg.RushLarsenModel, 'FromCellMLRushLarsen', 'RushLarsen')),
                           ('rush-larsen-opt', (cg.RushLarsenOptModel, 'FromCellMLRushLarsen', 'RushLarsen')),
                           ('grl1', (cg.GeneralisedRushLarsenFirstOrderModel, 'FromCellMLGRL1', 'GRL1')),
                           ('grl1-opt', (cg.GeneralisedRushLarsenFirstOrderModelOpt, 'FromCellMLGRL1', 'GRL1')),
                           ('grl2', (cg.GeneralisedRushLarsenSecondOrderModel, 'FromCellMLGRL2', 'GRL2')),
                           ('grl1-opt', (cg.GeneralisedRushLarsenSecondOrderModelOpt, 'FromCellMLGRL2', 'GRL2'))])

TRANSLATORS_WITH_MODIFIERS = ('--normal', '--ChasteOpt', '--cvode', '--cvode-data-clamp')


# Store extensions we can use and how to use them, based on extension of given outfile
EXTENSION_LOOKUP = {'.cellml': ['.hpp', '.cpp'], '': ['.hpp', '.cpp'], '.cpp': ['.hpp', '.cpp'],
                    '.hpp': ['.hpp', '.cpp'], '.c': ['.h', '.c'], '.h': ['.h', '.c']}

def chaste_codegen():
    # add options for command line interface
    parser = argparse.ArgumentParser(description='Chaste code generation for cellml.')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=cg.__version__))
    parser.add_argument('cellml_file', metavar='cellml_file', help='The cellml file or URI to convert to chaste code')

    group = parser.add_argument_group('ModelTypes', 'The different types of solver models for which code that can be generated')
    for k in TRANSLATORS:
        group.add_argument('--' + k, help='Generate ' + k + ' model type', action='store_true')

    group = parser.add_argument_group('Transformations', 'These options control which transformations '
                                      '(typically optimisations) are applied in the generated code')
    group.add_argument('-j', '--use-analytic-jacobian', dest='use_analytic_jacobian', default=False,
                       action='store_true', help='use a symbolic Jacobian calculated by SymPy '
                       '(--use-analytic-jacobian only works in combination with --cvode and is ignored for other model types)')

    group = parser.add_argument_group('Generated code options')
    group.add_argument('-o', dest='outfile', metavar='OUTFILE', default=None,
                        help='write program code to OUTFILE '
                             '[default action is to use the input filename with a different extension] '
                             'NOTE: expects provided OUTFILE to have an extension relevant to code being generated '
                             '(e.g. for CHASTE/C++ code: .cpp, .c, .hpp, or .h)')
    group.add_argument('-c', default=None, dest='cls_name',
                       help='explicitly set the name of the generated class')

    group = parser.add_argument_group('Chaste options', description='Options specific to Chaste code output')
    group.add_argument('-y', '--dll', '--dynamically-loadable', dest='dynamically_loadable',
                       action='store_true', default=False,
                       help='add code to allow the model to be compiled to a shared library and dynamically loaded ')
    group.add_argument('-m', '--use-modifiers', dest='modifiers',
                       action='store_true', default=False,
                       help='add modifier functions for metadata-annotated variables (except time & stimulus) '
                       'for use in sensitivity analysis. Only works with one of the following model types: ' +
                       str(TRANSLATORS_WITH_MODIFIERS) + ' and is ignored for others')

    # process options
    args = parser.parse_args()

    #model = cellmlmanip.load_model(args.cellml_file)
    for model_type in TRANSLATORS:
        use_translator_class = getattr(args, model_type)
        if use_translator_class:
            # Make sure modifiers are only passed to models which can generate them
            args.use_modifiers = args.modifiers if model_type in TRANSLATORS_WITH_MODIFIERS else False
            
            translator_class = TRANSLATORS[model_type][0]
            outfile_path, model_name_from_file, outfile_base, ext = get_outfile_parts(args.outfile if args.outfile is not None else args.cellml_file, args.cellml_file)
            args.class_name = args.cls_name if args.cls_name is not None else ('Dynamic' if args.dynamically_loadable else 'Cell') + model_name_from_file + TRANSLATORS[model_type][1]
            if not args.outfile:
                outfile_base += TRANSLATORS[model_type][2]
            
            model = cellmlmanip.load_model(args.cellml_file)
            # generate code Based on parameters a different class of translator may be used
            #cg.ChasteModel(model, outfile_base, header_ext=ext[0], **vars(args))
            chaste_model = translator_class(model, outfile_base, header_ext=ext[0], **vars(args))
            chaste_model.generate_chaste_code()

            # Write generated files
            hpp_gen_file_path = \
                os.path.join(outfile_path, outfile_base + ext[0])
            cpp_gen_file_path = \
                os.path.join(outfile_path, outfile_base + ext[1])
            write_file(hpp_gen_file_path, chaste_model.generated_hpp)
            write_file(cpp_gen_file_path, chaste_model.generated_cpp)

def get_outfile_parts(outfile, cellml_file):
    outfile_path = os.path.dirname(outfile)
    model_file_base_parts = os.path.splitext(os.path.basename(cellml_file))
    out_file_base_parts = os.path.splitext(os.path.basename(outfile))
    model_name_from_file = model_file_base_parts[0]
    outfile_base = out_file_base_parts[0]
    outfile_extension = out_file_base_parts[1] if len(out_file_base_parts) > 1 else ''
    ext = EXTENSION_LOOKUP[outfile_extension]
    return outfile_path, model_name_from_file, outfile_base, ext