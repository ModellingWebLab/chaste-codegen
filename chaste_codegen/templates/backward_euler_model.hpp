{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "{{base_class}}.hpp"
{% if not lookup_parameters is defined %}#include "{{ file_name }}Kernels.hpp"
#include "SolverBundles.cuh"{% endif %}
{% with %}{% set base_class = base_class ~ "<"~nonlinear_state_vars|length~">" %}{% include "Shared/hpp/class_declaration" %}{% endwith %}
public:
    {% if not lookup_parameters is defined %}template<typename ValueType> using CellFunctor = {{class_name}}Functor<ValueType>;
    template<typename ValueType> using Bundle = BackwardEulerBundle<CellFunctor<ValueType>, ValueType>;{% endif %}
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