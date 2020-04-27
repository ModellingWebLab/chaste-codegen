{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "AbstractCardiacCell.hpp"
{% with %}{% set base_class = "AbstractCardiacCell" %}{% include "Shared/hpp/class_declaration" %}{% endwith %}
{% include "Shared/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Shared/hpp/destructor_verify_state_variables_GetIIonic" %}
    void EvaluateYDerivatives(double {{free_variable.var_name}}, const std::vector<double>& rY, std::vector<double>& rDY);
{% include "Shared/hpp/ComputeDerivedQuantities" %}
{% include "Shared/hpp/CHASTE_CLASS_EXPORT" %}
