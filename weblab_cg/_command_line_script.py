######################################################################
#                    For running as an executable                    #
######################################################################
import argparse
import os
import cellmlmanip
import weblab_cg as cg
from weblab_cg._script_utils import write_file


def chaste_codegen():
    # For now just one type of translator
    translators = ['Chaste']
    # Store extensions we can use and how to use them
    extension_lookup = {'Chaste': dict()}
    for key in ('.cpp', '.hpp', '.cellml', ''):
        extension_lookup['Chaste'][key] = ['.hpp', '.cpp']
    for key in ('.c', '.h'):
        extension_lookup['Chaste'][key] = ['.h', '.c']

    # add options for command line interface
    parser = argparse.ArgumentParser(description='Chaste code generation for cellml.')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=cg.__version__))
    parser.add_argument('cellml_file', metavar='cellml_file', help='The cellml file or URI to convert to chaste code')
    parser.add_argument('-t', '--translate-type', choices=translators,
                        default='Chaste', metavar='TYPE', dest='translator_type',
                        help="the type of code to output [default: Chaste].  "
                        "Choices: " + str(translators))
    parser.add_argument('-o', dest='outfile', metavar='OUTFILE', default=None,
                        help='write program code to OUTFILE '
                             '[default action is to use the input filename with a different extension] '
                             'NOTE: expects provided OUTFILE to have an extension relevant to code being generated '
                             '(e.g. for CHASTE/C++ code: .cpp, .c, .hpp, or .h)')

    group = parser.add_argument_group('Generated code options')
    group.add_argument('-c', '--class-name', default=None, dest='class_name',
                       help="explicitly set the name of the generated class")

    group = parser.add_argument_group('Chaste options', description='Options specific to Chaste code output')
    group.add_argument('-y', '--dll', '--dynamically-loadable', dest='dynamically_loadable',
                       action='store_true', default=False,
                       help='add code to allow the model to be compiled to a shared library and dynamically loaded '
                             '(only works if -t Chaste is used)')
    group.add_argument('--expose-annotated-variables', dest='expose_annotated_variables',
                       action='store_true', default=False,
                       help="expose all oxmeta-annotated variables for access via the GetAnyVariable functionality")

    # process options
    args = parser.parse_args()

    model = cellmlmanip.load_model(args.cellml_file)
    model_type = cg.NormalChasteModel  # Based on parameters a different type of model may be generated
    outfile = args.outfile if args.outfile is not None else os.path.basename(args.cellml_file)
    outfile_path = os.path.dirname(outfile)
    model_file_base_parts = os.path.splitext(os.path.basename(args.cellml_file))
    out_file_base_parts = os.path.splitext(os.path.basename(outfile))
    model_name_from_file = model_file_base_parts[0]
    outfile_base = out_file_base_parts[0]
    outfile_extension = out_file_base_parts[1] if len(out_file_base_parts) > 1 else ''

    if args.class_name is None:
        args.class_name = ('Dynamic' if args.dynamically_loadable else 'Cell') + model_name_from_file + 'FromCellML'

    ext = extension_lookup[args.translator_type][outfile_extension]
    # generate code
    chaste_model = model_type(model, outfile_base, header_ext=ext[0], **vars(args))
    chaste_model.generate_chaste_code()

    # Write generated files
    hpp_gen_file_path = \
        os.path.join(outfile_path, outfile_base + ext[0])
    cpp_gen_file_path = \
        os.path.join(outfile_path, outfile_base + ext[1])
    write_file(hpp_gen_file_path, chaste_model.generated_hpp)
    write_file(cpp_gen_file_path, chaste_model.generated_cpp)
