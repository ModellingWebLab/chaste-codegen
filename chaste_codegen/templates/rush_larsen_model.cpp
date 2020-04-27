{% include "Shared/cpp/header_comments" %}
{% include "Shared/cpp/includes" %}
{% include "Shared/cpp/UseCellMLDefaultStimulus" %}
{% include "Shared/cpp/GetIntracellularCalciumConcentration" %}
{% with %}{% set base_class = "AbstractRushLarsenCardiacCell" %}{% include "RL/cpp/constructor" %}{% endwith %}
{% include "Shared/cpp/destructor" %}
{% include "Shared/cpp/VerifyStateVariables" %}
{% include "Shared/cpp/GetIIonic" %}
{% include "RL/cpp/EvaluateEquations" %}
{% include "RL/cpp/ComputeOneStepExceptVoltage" %}
{%- include "Shared/cpp/ComputeDerivedQuantities" %}
{% include "Shared/cpp/OdeSystemInformation" %}
{% include "Shared/cpp/CHASTE_CLASS_EXPORT" %}