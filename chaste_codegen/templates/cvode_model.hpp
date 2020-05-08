#ifdef CHASTE_CVODE
{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "{{base_class}}.hpp"
{% include "Shared/hpp/class_declaration" %}
{% include "Shared/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> pOdeSolver /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Shared/hpp/destructor_verify_state_variables_GetIIonic" %}
    void EvaluateYDerivatives(double {{free_variable.var_name}}, const {{vector_decl}} rY, {{vector_decl}} rDY);
    {%- if derived_quantities|length > 0 %}
    {{vector_decl}} ComputeDerivedQuantities(double {{free_variable.var_name}}, const {{vector_decl}} & rY);
    {%- endif %}
    {%- if jacobian_equations|length > 0 %}
    void EvaluateAnalyticJacobian(double {{free_variable.var_name}}, {{vector_decl}} rY, {{vector_decl}} rDY, CHASTE_CVODE_DENSE_MATRIX rJacobian, {{vector_decl}} rTmp1, {{vector_decl}} rTmp2, {{vector_decl}} rTmp3);
    {%- endif %}
{% include "Shared/hpp/CHASTE_CLASS_EXPORT" %}
#endif // CHASTE_CVODE