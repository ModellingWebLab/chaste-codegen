"""
Main module for cardiac Chaste code generation
"""
from cellmlmanip.parser import Transpiler

from ._chaste_printer import ChastePrinter  # noqa
#
# Load constants and version information
#
from ._config import (  # noqa
    DATA_DIR,
    LOGGER,
    MODULE_DIR,
    TEMPLATE_SUBDIR,
    CodegenError,
    __version__,
    __version_int__,
    version,
)
from ._labview_printer import LabviewPrinter  # noqa
from ._load_template import load_template  # noqa
#
# Load and expose public classes and functions
#
from ._math_functions import (  # noqa
    RealFunction,
    abs_,
    acos_,
    cos_,
    exp_,
    sin_,
    sqrt_,
    subs_math_func_placeholders,
)
from .backward_euler_model import BackwardEulerModel  # noqa
from .backward_euler_opt_model import BackwardEulerOptModel  # noqa
from .chaste_model import ChasteModel  # noqa
from .cvode_chaste_model import CvodeChasteModel  # noqa
from .cvode_opt_chaste_model import OptCvodeChasteModel  # noqa
from .generalised_rush_larsen_1_model import GeneralisedRushLarsenFirstOrderModel  # noqa
from .generalised_rush_larsen_1_opt_model import GeneralisedRushLarsenFirstOrderModelOpt  # noqa
from .generalised_rush_larsen_2_model import GeneralisedRushLarsenSecondOrderModel  # noqa
from .generalised_rush_larsen_2_opt_model import GeneralisedRushLarsenSecondOrderModelOpt  # noqa
from .model_with_conversions import add_conversions, load_model_with_conversions  # noqa
from .normal_chaste_model import NormalChasteModel  # noqa
from .opt_chaste_model import OptChasteModel  # noqa
from .rush_larsen_c import RushLarsenC  # noqa
from .rush_larsen_labview import RushLarsenLabview  # noqa
from .rush_larsen_model import RushLarsenModel  # noqa
from .rush_larsen_opt_model import RushLarsenOptModel  # noqa


# Set transpiler to prodcue our custom classes in order to avoid premature simplification/canonisation
Transpiler.set_mathml_handler('exp', exp_)
Transpiler.set_mathml_handler('abs', abs_)
Transpiler.set_mathml_handler('acos', acos_)
Transpiler.set_mathml_handler('cos', cos_)
Transpiler.set_mathml_handler('sqrt', sqrt_)
Transpiler.set_mathml_handler('sin', sin_)
