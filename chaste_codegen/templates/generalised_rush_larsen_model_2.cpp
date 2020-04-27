{% include "Shared/cpp/header_comments" %}
{% include "Shared/cpp/includes" %}
{% include "Shared/cpp/UseCellMLDefaultStimulus" %}
{% include "Shared/cpp/GetIntracellularCalciumConcentration" %}
{% with %}{% set base_class = "AbstractGeneralizedRushLarsenCardiacCell" %}{% include "RL/cpp/constructor" %}{% endwith %}
{% include "Shared/cpp/destructor" %}
{% include "Shared/cpp/VerifyStateVariables" %}
{% include "Shared/cpp/GetIIonic" %}
{% include "GRL2/cpp/UpdateTransmembranePotential" %}
{% include "GRL2/cpp/ComputeOneStepExceptVoltage" %}
{% include "GRL/cpp/EvaluateYDerivative_EvaluatePartialDerivative" %}
{%- include "Shared/cpp/ComputeDerivedQuantities" %}
{% include "Shared/cpp/OdeSystemInformation" %}
{% include "Shared/cpp/CHASTE_CLASS_EXPORT" %}