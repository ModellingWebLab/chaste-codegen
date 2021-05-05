{% include "Shared/cpp/header_comments" %}
#include "CardiacNewtonSolver.hpp"
{% with %}{% set base_class = base_class ~ "<"~nonlinear_state_vars|length~">" %}{% include "Shared/cpp/includes" %}{% endwith %}
{% include "Shared/cpp/lookup_tables" %}
{% include "Shared/cpp/UseCellMLDefaultStimulus" %}
{% include "Shared/cpp/GetIntracellularCalciumConcentration" %}
{% include "BE/cpp/constructor_declaration" %}
{% include "Shared/cpp/constructor_body" %}
{% include "Shared/cpp/destructor" %}
{% include "Shared/cpp/GetLookupTableCollection" %}
{% include "Shared/cpp/VerifyStateVariables" %}
{% include "Shared/cpp/GetIIonic" %}
{% include "BE/cpp/ComputeResidual" %}
{% include "BE/cpp/ComputeJacobian" %}
{% include "BE/cpp/UpdateTransmembranePotential" %}
{% include "BE/cpp/ComputeOneStepExceptVoltage" %}
{%- include "Shared/cpp/ComputeDerivedQuantities" %}
{% include "Shared/cpp/OdeSystemInformation" %}
{% include "Shared/cpp/CHASTE_CLASS_EXPORT" %}