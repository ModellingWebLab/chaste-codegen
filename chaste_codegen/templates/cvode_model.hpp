#ifdef CHASTE_CVODE
{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "{{base_class}}.hpp"
#include "HostDeviceMacros.hpp"
#include "MathsCustomFunctions.hpp"
#include "StimulusEvaluatorCuda.hpp"
#include "ChasteCvodeMacros.hpp"
{% include "Shared/hpp/class_declaration" %}
    static constexpr unsigned TOTAL_SIZE = {{ state_vars|length }}u;
    static constexpr unsigned NNZ = {{ sparse_nnz }}u;
    static inline const int sparse_rowptr[] = { {{ sparse_rowptr|join(", ") }} };
    static inline const int sparse_colind[] = { {{ sparse_colind|join(", ") }} };
{% include "Shared/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> pOdeSolver /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Shared/hpp/destructor_verify_state_variables_GetIIonic" %}
    void EvaluateYDerivatives(double {{free_variable.var_name}}, const {{vector_decl}} rY, {{vector_decl}} rDY);
    {% if not lookup_parameters is defined%}template<typename ValueType>
    DEVICE
    static void EvaluateYDerivativesDevice(ValueType {{free_variable.var_name}}, const ValueType* rY, ValueType* rDY, const ValueType mSetVoltageDerivativeToZero, const ValueType mFixedVoltage, const ValueType* mParameters, const ValueType capacitance, const DeviceStimulusFunctor<ValueType> stim);{% endif %}
    {%- if derived_quantities|length > 0 %}
    {{vector_decl}} ComputeDerivedQuantities(double {{free_variable.var_name}}, const {{vector_decl}} & rY);
    {%- endif %}
    {%- if jacobian_equations|length > 0 %}
    void EvaluateAnalyticJacobian(double {{free_variable.var_name}}, {{vector_decl}} rY, {{vector_decl}} rDY, CHASTE_CVODE_DENSE_MATRIX rJacobian, {{vector_decl}} rTmp1, {{vector_decl}} rTmp2, {{vector_decl}} rTmp3);
    {% if not lookup_parameters is defined %}template<typename ValueType>
    DEVICE
    static void EvaluateAnalyticJacobianDevice(ValueType {{free_variable.var_name}}, const ValueType *rY, ValueType *rDY, ValueType *rJacobian, ValueType *rTmp1, ValueType *rTmp2, ValueType *rTmp3, const unsigned nvars, const ValueType mSetVoltageDerivativeToZero, const ValueType mFixedVoltage, const ValueType *mParameters, const ValueType capacitance, const DeviceStimulusFunctor<ValueType> stim);
    template<typename ValueType>
    DEVICE
    static void EvaluateSparseAnalyticJacobianDevice(ValueType {{free_variable.var_name}}, const ValueType *rY, ValueType *rDY, ValueType *rJacobian, ValueType *rTmp1, ValueType *rTmp2, ValueType *rTmp3, const unsigned nvars, const ValueType mSetVoltageDerivativeToZero, const ValueType mFixedVoltage, const ValueType *mParameters, const ValueType capacitance, const DeviceStimulusFunctor<ValueType> stim);{% endif %}
    {%- endif %}
{% include "Shared/hpp/CHASTE_CLASS_EXPORT" %}
#include "ChasteCpuMacros.hpp"
#endif // CHASTE_CVODE