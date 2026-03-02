{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "{{base_class}}.hpp"

{% if not lookup_parameters is defined -%}
#if USING_DEVICE_COMPILER
template<typename CellType, typename ValueType>
class BackwardEulerKernelLauncher; // Forward declare to hide CUDA-specifics from standard C++ compiler
#endif
{%- endif %}
{% with %}{% set base_class = base_class ~ "<" ~ nonlinear_state_vars|length ~ ">" %}{% include "Shared/hpp/class_declaration" %}{% endwith %}
{% if not lookup_parameters is defined -%}
#if USING_DEVICE_COMPILER
    template<typename ValueType> using SolverKernelLauncher = BackwardEulerKernelLauncher<{{class_name}}, ValueType>;
    static constexpr unsigned TOTAL_SIZE = {{ state_vars|length }}u;
    static constexpr unsigned NONLINEAR_SIZE = {{ nonlinear_state_vars|length }}u;
#endif{%- endif %}
{% include "Shared/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> /* unused */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Shared/hpp/destructor_verify_state_variables_GetIIonic" %}
    {% if nonlinear_state_vars|length > 0 -%}
    void ComputeResidual(double {{free_variable.var_name}}, const double rCurrentGuess[{{nonlinear_state_vars|length}}], double rResidual[{{nonlinear_state_vars|length}}]);
    void ComputeJacobian(double {{free_variable.var_name}}, const double rCurrentGuess[{{nonlinear_state_vars|length}}], double rJacobian[{{nonlinear_state_vars|length}}][{{nonlinear_state_vars|length}}]);
    {%- endif %} {# nonlinear_state_vars #}

#if USING_DEVICE_COMPILER
    {% if not lookup_parameters is defined -%}{# only generate kernels for non opt models -#}
    {% if nonlinear_state_vars|length > 0 -%}
    template<typename ValueType>
    DEVICE
    static void ComputeResidualDevice(ValueType {{free_variable.var_name}}, const ValueType rCurrentGuess[NONLINEAR_SIZE], const ValueType rY[], ValueType rResidual[NONLINEAR_SIZE], ValueType mDt, const ValueType mParameters[], bool mSetVoltageDerivativeToZero, ValueType mFixedVoltage, ValueType capacitance, const DeviceStimulusFunctor<ValueType> stim);

    template<typename ValueType>
    DEVICE
    static void ComputeJacobianDevice(ValueType {{free_variable.var_name}}, const ValueType rCurrentGuess[NONLINEAR_SIZE], const ValueType rY[], ValueType rJacobian[NONLINEAR_SIZE][NONLINEAR_SIZE], ValueType mDt, const ValueType mParameters[], bool mSetVoltageDerivativeToZero, ValueType mFixedVoltage, ValueType capacitance, const DeviceStimulusFunctor<ValueType> stim);
    {%- endif %} {# nonlinear_state_vars #}
    template<typename ValueType>
    DEVICE
    static void UpdateTransmembranePotentialDevice(ValueType {{free_variable.var_name}}, ValueType rY[], ValueType mDt, const ValueType mParameters[], bool mSetVoltageDerivativeToZero, ValueType mFixedVoltage, DeviceStimulusFunctor<ValueType> stim, ValueType capacitance);

    template<typename ValueType>
    DEVICE
    static void SolveClosedFormVarsDevice(ValueType rY[TOTAL_SIZE], ValueType mDt, const ValueType mParameters[], bool mSetVoltageDerivativeToZero, ValueType mFixedVoltage, ValueType capacitance);
    
    {% if nonlinear_state_vars|length > 0 -%}
    template<typename ValueType>
    DEVICE
    static void FillInitialGuessDevice(ValueType _guess[NONLINEAR_SIZE], const ValueType rY[TOTAL_SIZE]);
    
    template<typename ValueType>
    DEVICE
    static void ScatterSolutionDevice(const ValueType _guess[NONLINEAR_SIZE], ValueType rY[TOTAL_SIZE]);
    {%- endif %}  {# nonlinear_state_vars #}
    {%- endif %}  {# lookup_parameters #}
#endif
protected:
    void UpdateTransmembranePotential(double {{free_variable.var_name}});
    void ComputeOneStepExceptVoltage(double {{free_variable.var_name}});
{% include "Shared/hpp/ComputeDerivedQuantities" -%}

{% include "Shared/hpp/CHASTE_CLASS_EXPORT" %}

{% if not lookup_parameters is defined -%}
#if USING_DEVICE_COMPILER
    #include "{{ file_name }}Kernels.hpp"
    #include "BackwardEulerKernels.hpp"
#endif
{%- endif %}