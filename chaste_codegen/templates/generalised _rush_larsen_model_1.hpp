{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "AbstractGeneralizedRushLarsenCardiacCell.hpp"

class {{class_name}} : public AbstractGeneralizedRushLarsenCardiacCell{%- if dynamically_loadable %}, public AbstractDynamicallyLoadableEntity{%- endif %}
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractGeneralizedRushLarsenCardiacCell >(*this);
{% include "Shared/hpp/AbstractDynamicallyLoadableEntity" %}
    }
    //
    // Settable parameters and readable variables
    //
public:
{% include "Shared/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Shared/hpp/destructor_verify_state_variables_GetIIonic" %}
    void UpdateTransmembranePotential(double {{free_variable.var_name}});
    void ComputeOneStepExceptVoltage(double {{free_variable.var_name}});
    {% for state_var in state_vars %}
    double EvaluateYDerivative{{loop.index0}}(double {{free_variable.var_name}}, std::vector<double>& rY);
    double EvaluatePartialDerivative{{loop.index0}}(double {{free_variable.var_name}}, std::vector<double>& rY, double delta, bool forceNumerical=false);
    {%- endfor %}
{% include "Shared/hpp/ComputeDerivedQuantities" %}
};
{% include "Shared/hpp/CHASTE_CLASS_EXPORT" %}
