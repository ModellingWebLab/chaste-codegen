#ifdef CHASTE_CVODE
{% include "Shared/cpp/header_comments" %}
{% include "Shared/cpp/includes" %}
{% include "Shared/cpp/UseCellMLDefaultStimulus" %}
{% include "Cvode/cpp/GetIntracellularCalciumConcentration" %}{% include "Cvode/cpp/constructor" %}
{% include "Shared/cpp/destructor" %}
{% include "Cvode/cpp/VerifyStateVariables" %}
{% include "Cvode/cpp/GetIIonic" %}
{% include "Cvode/cpp/EvaluateYDerivatives" %}{% include "Cvode/cpp/ComputeDerivedQuantities" %}{% include "Cvode/cpp/EvaluateAnalyticJacobian" %}
{% include "Cvode/cpp/OdeSystemInformation" %}
{% include "Shared/cpp/CHASTE_CLASS_EXPORT" %}#endif // CHASTE_CVODE
