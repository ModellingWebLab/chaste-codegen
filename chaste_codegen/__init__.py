"""
Main module for cardiac Chaste code generation
"""
import logging

from cellmlmanip.transpiler import Transpiler

from ._chaste_printer import ChastePrinter  # noqa
#
# Load constants and version information
#
from ._config import (  # noqa
    DATA_DIR,
    MODULE_DIR,
    TEMPLATE_SUBDIR,
    __version__,
    __version_int__,
    version,
)
from ._load_template import load_template  # noqa
#
# Load and expose public classes and functions
#
from ._math_functions import RealFunction  # noqa
from ._math_functions import (
    abs_,
    acos_,
    cos_,
    exp_,
    sin_,
    sqrt_,
)
from .backward_euler_model import BackwardEulerModel  # noqa
from .chaste_model import ChasteModel  # noqa
from .cvode_chaste_model import CvodeChasteModel  # noqa
from .cvode_with_data_clamp_model import CvodeWithDataClampeModel  # noqa
from .generalised_rush_larsen_1_model import GeneralisedRushLarsenFirstOrderModel  # noqa
from .generalised_rush_larsen_1_opt_model import GeneralisedRushLarsenFirstOrderModelOpt  # noqa
from .generalised_rush_larsen_2_model import GeneralisedRushLarsenSecondOrderModel  # noqa
from .generalised_rush_larsen_2_opt_model import GeneralisedRushLarsenSecondOrderModelOpt  # noqa
from .normal_chaste_model import NormalChasteModel  # noqa
from .opt_chaste_model import OptChasteModel  # noqa
from .rush_larsen_model import RushLarsenModel  # noqa
from .rush_larsen_opt_model import RushLarsenOptModel  # noqa


# Configure logging
logging.basicConfig()
del(logging)

# Set transpiler to prodcue our custom classes in order to avoid premature simplification/canonisation
Transpiler.set_mathml_handler('exp', exp_)
Transpiler.set_mathml_handler('abs', abs_)
Transpiler.set_mathml_handler('acos', acos_)
Transpiler.set_mathml_handler('cos', cos_)
Transpiler.set_mathml_handler('sqrt', sqrt_)
Transpiler.set_mathml_handler('sin', sin_)
