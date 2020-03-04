#ifdef CHASTE_CVODE
{% include "Normal/cpp/header_comments" %}
{% include "Normal/cpp/includes" %}
{% include "Normal/cpp/UseCellMLDefaultStimulus" %}
{% include "Cvode/cpp/GetIntracellularCalciumConcentration" %}{% include "Cvode/cpp/constructor" %}
{% include "Normal/cpp/destructor" %}
{% include "Cvode/cpp/VerifyStateVariables" %}
{% include "Cvode/cpp/GetIIonic" %}
{% include "Cvode/cpp/EvaluateYDerivatives" %}{% include "Cvode/cpp/ComputeDerivedQuantities" %}{% include "Cvode/cpp/EvaluateAnalyticJacobian" %}
{% include "Cvode/cpp/OdeSystemInformation" %}
{% include "Normal/cpp/CHASTE_CLASS_EXPORT" %}#endif // CHASTE_CVODE
