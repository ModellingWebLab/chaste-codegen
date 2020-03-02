import logging
import pytest
from chaste_codegen.tests.test_codegen import get_models

# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


chaste_all_normal_models = get_models(ref_folder='cronjob_reference_models', type='Normal')
chaste_all_opt_models = get_models(ref_folder='cronjob_reference_models', type='Opt')
chaste_all_cvode_models = get_models(ref_folder='cronjob_reference_models', type='Cvode')
chaste_all_cvode_models_jacobian = get_models(ref_folder='cronjob_reference_models', type='Cvode_with_jacobian')


@pytest.mark.cronjob
@pytest.mark.normal
@pytest.mark.parametrize(('model'), chaste_all_normal_models)
def test_Normal_cronjob(tmp_path, model, request):
    """ Check generation of Normal models against reference"""
    if request.config.option.markexpr != 'cronjob and normal' and\
            request.config.option.markexpr != 'normal and cronjob':
        pytest.skip('Skip if not explicitly set to run cronjob with -m "cronjob and normal"')
    from chaste_codegen.tests.test_codegen import test_Normal
    test_Normal(tmp_path, model)


@pytest.mark.cronjob
@pytest.mark.opt
@pytest.mark.parametrize(('model'), chaste_all_opt_models)
def test_Opt_cronjob(tmp_path, model, request):
    """ Check generation of Opt models against reference"""
    if request.config.option.markexpr != 'cronjob and opt' and request.config.option.markexpr != 'opt and cronjob':
        pytest.skip('Skip if not explicitly set to run cronjob with -m "cronjob and opt"')
    from chaste_codegen.tests.test_codegen import test_Opt
    test_Opt(tmp_path, model)


@pytest.mark.cronjob
@pytest.mark.cvode
@pytest.mark.parametrize(('model'), chaste_all_cvode_models)
def test_Cvode_cronjob(tmp_path, model, request):
    """ Check generation of Cvode models against reference"""
    if request.config.option.markexpr != 'cronjob and cvode' and request.config.option.markexpr != 'cvode and cronjob':
        pytest.skip('Skip if not explicitly set to run cronjob with -m "cronjob and cvode"')
    from chaste_codegen.tests.test_codegen import test_Cvode
    test_Cvode(tmp_path, model)


@pytest.mark.cronjob
@pytest.mark.cvode_jacobian
@pytest.mark.parametrize(('model'), chaste_all_cvode_models_jacobian)
def test_Cvode_jacobian_cronjob(tmp_path, model, request):
    """ Check generation of Cvode models against reference"""
    if request.config.option.markexpr != 'cronjob and cvode_jacobian' and\
            request.config.option.markexpr != 'cvode_jacobian and cronjob':
        pytest.skip('Skip if not explicitly set to run cronjob with -m "cronjob and cvode_jacobian"')
    from chaste_codegen.tests.test_codegen import test_Cvode_jacobian
    test_Cvode_jacobian(tmp_path, model)
