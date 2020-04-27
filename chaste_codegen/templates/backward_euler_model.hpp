{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "AbstractBackwardEulerCardiacCell.hpp"
{% with %}{% set base_class = "AbstractBackwardEulerCardiacCell<"~nonlinear_state_vars|length~">" %}{% include "Shared/hpp/class_declaration" %}{% endwith %}
{% include "Shared/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Shared/hpp/destructor_verify_state_variables_GetIIonic" %}
    {%- if nonlinear_state_vars|length > 0 %}void ComputeResidual(double {{free_variable.var_name}}, const double rCurrentGuess[{{nonlinear_state_vars|length}}], double rResidual[{{nonlinear_state_vars|length}}]);
    void ComputeJacobian(double {{free_variable.var_name}}, const double rCurrentGuess[{{nonlinear_state_vars|length}}], double rJacobian[{{nonlinear_state_vars|length}}][{{nonlinear_state_vars|length}}]);{% endif -%}
protected:
    void UpdateTransmembranePotential(double {{free_variable.var_name}});
    void ComputeOneStepExceptVoltage(double {{free_variable.var_name}});
{% include "Shared/hpp/ComputeDerivedQuantities" %}
{% include "Shared/hpp/CHASTE_CLASS_EXPORT" %}