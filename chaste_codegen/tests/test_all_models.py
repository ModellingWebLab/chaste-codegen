import logging

import pytest

from chaste_codegen.tests.test_codegen import get_models


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


chaste_all_normal_models = get_models(ref_folder='all_models_reference_models', type='Normal')
chaste_all_opt_models = get_models(ref_folder='all_models_reference_models', type='Opt')
chaste_all_cvode_models = get_models(ref_folder='all_models_reference_models', type='Cvode')
chaste_all_cvode_models_jacobian = get_models(ref_folder='all_models_reference_models', type='Cvode_with_jacobian')
chaste_all_BE = get_models(ref_folder='all_models_reference_models', type='BE')
chaste_all_RL = get_models(ref_folder='all_models_reference_models', type='RL')
chaste_all_RLopt = get_models(ref_folder='all_models_reference_models', type='RLopt')


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
    """ Check generation of Cvode models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_RL
    test_RL(tmp_path, model)


@pytest.mark.all_models
@pytest.mark.parametrize(('model'), chaste_all_RLopt)
def test_RLopt_all_models(tmp_path, model, request):
    """ Check generation of Cvode models against reference"""
    if request.config.option.markexpr != 'all_models':
        pytest.skip('Skip if not explicitly set to run all_models with -m all_models')
    from chaste_codegen.tests.test_codegen import test_RLopt
    test_RLopt(tmp_path, model)
