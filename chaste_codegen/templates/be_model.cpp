{% include "Shared/cpp/header_comments" %}
{% include "Shared/cpp/includes" %}
#include "CardiacNewtonSolver.hpp"
{% include "Shared/cpp/UseCellMLDefaultStimulus" %}
{% include "Shared/cpp/GetIntracellularCalciumConcentration" %}
{% include "BE/cpp/constructor" %}
{% include "Shared/cpp/destructor" %}
{% include "Shared/cpp/VerifyStateVariables" %}
{% include "Shared/cpp/GetIIonic" %}
{% include "BE/cpp/ComputeResidual" %}
{% include "BE/cpp/ComputeJacobian" %}
{% include "BE/cpp/UpdateTransmembranePotential" %}
{% include "BE/cpp/ComputeOneStepExceptVoltage" %}
{%- include "Shared/cpp/ComputeDerivedQuantities" %}
{% include "Shared/cpp/OdeSystemInformation" %}
{% include "Shared/cpp/CHASTE_CLASS_EXPORT" %}