import pytest

import chaste_codegen as cg
from chaste_codegen.tests.test_codegen import get_models


chaste_all_normal_models = get_models(ref_folder='all_models_reference_models', type='Normal')
chaste_all_opt_models = get_models(ref_folder='all_models_reference_models', type='Opt')
chaste_all_cvode_models = get_models(ref_folder='all_models_reference_models', type='Cvode')
chaste_all_cvode_models_jacobian = get_models(ref_folder='all_models_reference_models', type='Cvode_with_jacobian')
chaste_all_cvode_opt_models = get_models(ref_folder='all_models_reference_models', type='Cvode_opt')
chaste_all_cvode_opt_models_with_jacobians = get_models(ref_folder='all_models_reference_models',
                                                        type='Cvode_opt_with_jacobian')
chaste_all_BE = get_models(ref_folder='all_models_reference_models', type='BE')
chaste_all_BEopt = get_models(ref_folder='all_models_reference_models', type='BEopt')
chaste_all_RL = get_models(ref_folder='all_models_reference_models', type='RL')
chaste_all_RLopt = get_models(ref_folder='all_models_reference_models', type='RLopt')
chaste_all_GRL1 = get_models(ref_folder='all_models_reference_models', type='GRL1')
chaste_all_GRL1Opt = get_models(ref_folder='all_models_reference_models', type='GRL1Opt')
chaste_all_GRL2 = get_models(ref_folder='all_models_reference_models', type='GRL2')
chaste_all_GRL2Opt = get_models(ref_folder='all_models_reference_models', type='GRL2Opt')
chaste_CVODE_DATA_CLAMP = get_models(ref_folder='all_models_reference_models', type='CVODE_DATA_CLAMP')
chaste_CVODE_DATA_CLAMP_OPT = get_models(ref_folder='all_models_reference_models', type='CVODE_DATA_CLAMP_OPT')


cg.__version__ = "(version omitted as unimportant)"
cg.chaste_model.TIME_STAMP = "(date omitted as unimportant)"


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_cvode_opt_models_with_jacobians)
def test_Cvode_opt_jacobian(tmp_path, model, request):
    """ Check generation of Cvode models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_Cvode_opt_jacobian
    test_Cvode_opt_jacobian(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_cvode_opt_models)
def test_Cvode_opt(tmp_path, model, request):
    """ Check generation of Cvode models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_Cvode_opt
    test_Cvode_opt(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_normal_models)
def test_Normal_all_models(tmp_path, model, request):
    """ Check generation of Normal models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_Normal
    test_Normal(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_opt_models)
def test_Opt_all_models(tmp_path, model, request):
    """ Check generation of Opt models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_Opt
    test_Opt(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_cvode_models)
def test_Cvode_all_models(tmp_path, model, request):
    """ Check generation of Cvode models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_Cvode
    test_Cvode(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_cvode_models_jacobian)
def test_Cvode_jacobian_all_models(tmp_path, model, request):
    """ Check generation of Cvode models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_Cvode_jacobian
    test_Cvode_jacobian(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_BEopt)
def test_BEopt_all_models(tmp_path, model, request):
    """ Check generation of Cvode models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_BEopt
    test_BEopt(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_BE)
def test_BE_all_models(tmp_path, model, request):
    """ Check generation of Cvode models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_BE
    test_BE(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_RL)
def test_RL_all_models(tmp_path, model, request):
    """ Check generation of Rush Larsen models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_RL
    test_RL(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_RLopt)
def test_RLopt_all_models(tmp_path, model, request):
    """ Check generation of Rush Larsen Opt models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_RLopt
    test_RLopt(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_GRL1)
def test_GRL1_all_models(tmp_path, model, request):
    """ Check generation of Generalised Rush Larsen First order models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_GRL1
    test_GRL1(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_GRL1Opt)
def test_GRL1Opt_all_models(tmp_path, model, request):
    """ Check generation of Generalised Rush Larsen First order optimised models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_GRL1Opt
    test_GRL1Opt(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_GRL2)
def test_GRL2_all_models(tmp_path, model, request):
    """ Check generation of Generalised Rush Larsen Second order models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_GRL2
    test_GRL2(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_GRL2Opt)
def test_GRL2Opt_all_models(tmp_path, model, request):
    """ Check generation of Generalised Rush Larsen Second order optimised models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_GRL2Opt
    test_GRL2Opt(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_CVODE_DATA_CLAMP)
def test_CVODE_DATA_CLAMP_all_models(tmp_path, model, request):
    """ Check generation of CVODE Data Clamp models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_CVODE_DATA_CLAMP
    test_CVODE_DATA_CLAMP(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_CVODE_DATA_CLAMP_OPT)
def test_CVODE_DATA_CLAMP_OPT_all_models(tmp_path, model, request):
    """ Check generation of CVODE with Data Clamp opt models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_CVODE_DATA_CLAMP_OPT
    test_CVODE_DATA_CLAMP_OPT(tmp_path, model)
