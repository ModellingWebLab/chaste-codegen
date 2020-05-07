{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "AbstractGeneralizedRushLarsenCardiacCell.hpp"
{% with %}{% set base_class = "AbstractGeneralizedRushLarsenCardiacCell" %}{% include "Shared/hpp/class_declaration" %}{% endwith %}
{% include "Shared/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Shared/hpp/destructor_verify_state_variables_GetIIonic" %}
    void UpdateTransmembranePotential(double {{free_variable.var_name}});
    void ComputeOneStepExceptVoltage(double {{free_variable.var_name}});
    {% for state_var in state_vars %}
    double EvaluateYDerivative{{loop.index0}}(double {{free_variable.var_name}}, {{vector_decl}} rY);
    double EvaluatePartialDerivative{{loop.index0}}(double {{free_variable.var_name}}, {{vector_decl}} rY, double delta, bool forceNumerical=false);
    {%- endfor %}
{% include "Shared/hpp/ComputeDerivedQuantities" %}
{% include "Shared/hpp/CHASTE_CLASS_EXPORT" %}