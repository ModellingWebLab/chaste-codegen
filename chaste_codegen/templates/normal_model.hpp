{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "AbstractCardiacCell.hpp"

class {{class_name}} : public AbstractCardiacCell{%- if dynamically_loadable %}, public AbstractDynamicallyLoadableEntity{%- endif %}
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractCardiacCell >(*this);
{% include "Shared/hpp/AbstractDynamicallyLoadableEntity" %}
    }

    //
    // Settable parameters and readable variables
    //

public:
{% include "Shared/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Shared/hpp/destructor_verify_state_variables_GetIIonic" %}
    void EvaluateYDerivatives(double {{free_variable.var_name}}, const std::vector<double>& rY, std::vector<double>& rDY);
{% include "Shared/hpp/ComputeDerivedQuantities" %}
};
{% include "Shared/hpp/CHASTE_CLASS_EXPORT" %}
