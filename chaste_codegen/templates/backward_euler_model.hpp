{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "{{base_class}}.hpp"
{% if not lookup_parameters is defined %}//#include "BackwardEulerKernels.cuh"
template<typename CellType, typename ValueType>
class BackwardEulerKernelLauncher; // We forward declare so that we do not expose threadIdx and blockIdx to c++ compiler
#include "StimulusEvaluatorCuda.hpp"   // DeviceStimulusFunctor (+ includes StimulusDescriptor){% endif %}
{% with %}{% set base_class = base_class ~ "<"~nonlinear_state_vars|length~">" %}{% include "Shared/hpp/class_declaration" %}{% endwith %}
public:
    {% if not lookup_parameters is defined %}template<typename ValueType> using SolverKernelLauncher = BackwardEulerKernelLauncher<{{class_name}}, ValueType>;
    static constexpr unsigned TOTAL_SIZE = {{ state_vars|length }}u;
    static constexpr unsigned NONLINEAR_SIZE = {{ nonlinear_state_vars|length }}u;{% endif %}
{% include "Shared/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Shared/hpp/destructor_verify_state_variables_GetIIonic" %}
    {%- if nonlinear_state_vars|length > 0 %}void ComputeResidual(double {{free_variable.var_name}}, const double rCurrentGuess[{{nonlinear_state_vars|length}}], double rResidual[{{nonlinear_state_vars|length}}]);
    void ComputeJacobian(double {{free_variable.var_name}}, const double rCurrentGuess[{{nonlinear_state_vars|length}}], double rJacobian[{{nonlinear_state_vars|length}}][{{nonlinear_state_vars|length}}]);
    
    {% if not lookup_parameters is defined %}template<typename ValueType>
    DEVICE
    static void ComputeResidualDevice(ValueType {{free_variable.var_name}}, const ValueType rCurrentGuess[NONLINEAR_SIZE], const ValueType rY[], ValueType rResidual[NONLINEAR_SIZE], ValueType mDt, const ValueType mParameters[], bool mSetVoltageDerivativeToZero, ValueType mFixedVoltage, ValueType capacitance, const DeviceStimulusFunctor<ValueType> stim);

    template<typename ValueType>
    DEVICE
    static void ComputeJacobianDevice(ValueType {{free_variable.var_name}}, const ValueType rCurrentGuess[NONLINEAR_SIZE], const ValueType rY[], ValueType rJacobian[NONLINEAR_SIZE][NONLINEAR_SIZE], ValueType mDt, const ValueType mParameters[], bool mSetVoltageDerivativeToZero, ValueType mFixedVoltage, ValueType capacitance, const DeviceStimulusFunctor<ValueType> stim);{% endif %}

{% endif -%}

    {% if not lookup_parameters is defined %}template<typename ValueType>
    DEVICE
    static void UpdateTransmembranePotentialDevice(ValueType {{free_variable.var_name}}, ValueType rY[], ValueType mDt, const ValueType mParameters[], bool mSetVoltageDerivativeToZero, ValueType mFixedVoltage, DeviceStimulusFunctor<ValueType> stim, ValueType capacitance);

    template<typename ValueType>
    DEVICE
    static void SolveClosedFormVarsDevice(ValueType rY[TOTAL_SIZE], ValueType mDt, const ValueType mParameters[], bool mSetVoltageDerivativeToZero, ValueType mFixedVoltage, ValueType capacitance);
    
    {%- if nonlinear_state_vars|length > 0 %}template<typename ValueType>
    DEVICE
    static void FillInitialGuessDevice(ValueType _guess[NONLINEAR_SIZE], const ValueType rY[TOTAL_SIZE]);
    
    template<typename ValueType>
    DEVICE
    static void ScatterSolutionDevice(const ValueType _guess[NONLINEAR_SIZE], ValueType rY[TOTAL_SIZE]);{% endif %}{% endif %}

protected:
    void UpdateTransmembranePotential(double {{free_variable.var_name}});
    void ComputeOneStepExceptVoltage(double {{free_variable.var_name}});
{% include "Shared/hpp/ComputeDerivedQuantities" %}
{% include "Shared/hpp/CHASTE_CLASS_EXPORT" %}
{# As CHASTE_CLASS_EXPORT defines our closing bracket for our class, and also the end of the double include guard for this file,
    we cannot easily add our extra includes below within the double include guard. Hence we should ensure anything included below
    also has its own double include guard (or is ok to be included multiple times). #}

{% if not lookup_parameters is defined %}
#ifdef __CUDACC__
    #include "{{ file_name }}Kernels.hpp"
    #include "BackwardEulerKernels.hpp"
#endif{% endif %}