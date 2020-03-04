{% include "Normal/hpp/header_comments" %}
{% include "Normal/hpp/includes" %}
{% include "Normal/hpp/class_def" %}
{% include "Normal/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Normal/hpp/destructor_verify_state_variables_GetIIonic" %}
    void EvaluateYDerivatives(double {{free_variable.var_name}}, const std::vector<double>& rY, std::vector<double>& rDY);
    {%- if derived_quantities|length > 0 %}
    std::vector<double> ComputeDerivedQuantities(double {{free_variable.var_name}}, const std::vector<double> & rY);
    {%- endif %}
};
{% include "Normal/hpp/CHASTE_CLASS_EXPORT" %}
