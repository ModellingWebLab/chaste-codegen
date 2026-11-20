{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "{{base_class}}.hpp"
{%- if has_device_code %}
#include "CardiacCellDeviceData.hpp"

// GPU solvers for this model, defined in {{file_name}}Device.cu
{%- for value_type in ['float', 'double'] %}
void {{class_name}}SolveOnDevice(const CardiacCellDeviceData<{{value_type}}>& rData);
{%- endfor %}{% endif %}
{% include "Shared/hpp/class_declaration" %}
{% include "Shared/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Shared/hpp/destructor_verify_state_variables_GetIIonic" %}
    void EvaluateYDerivatives(double {{free_variable.var_name}}, const {{vector_decl}} rY, {{vector_decl}} rDY);
{%- if has_device_code %}{% for value_type in ['float', 'double'] %}
    static void SolveOnDevice(const CardiacCellDeviceData<{{value_type}}>& rData)
    {
        {{class_name}}SolveOnDevice(rData);
    }
{%- endfor %}{% endif %}
{% include "Shared/hpp/ComputeDerivedQuantities" %}
{% include "Shared/hpp/CHASTE_CLASS_EXPORT" %}