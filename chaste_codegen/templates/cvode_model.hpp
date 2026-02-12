#ifdef CHASTE_CVODE
{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "{{base_class}}.hpp"
#include "HostDeviceMacros.hpp"
#include "StimulusEvaluatorCuda.hpp"
#include "MathsCustomFunctions.hpp"
{% include "Shared/hpp/class_declaration" %}
    static constexpr unsigned TOTAL_SIZE = {{ state_vars|length }}u;
{% include "Shared/hpp/DefaultStimulus_IntracellularCalciumConcentration" %}
    {{class_name}}(boost::shared_ptr<AbstractIvpOdeSolver> pOdeSolver /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
{% include "Shared/hpp/destructor_verify_state_variables_GetIIonic" %}
    void EvaluateYDerivatives(double {{free_variable.var_name}}, const {{vector_decl}} rY, {{vector_decl}} rDY);
    //template<typename ValueType>
    //DEVICE
    //static void EvaluateYDerivativesDevice(ValueType {{free_variable.var_name}}, const ValueType* rY, ValueType* rDY, ValueType mSetVoltageDerivativeToZero, ValueType mFixedVoltage, ValueType *mParameters, ValueType capacitance);
    {% if not lookup_parameters is defined%}
    {% set body %}
    template<typename ValueType>
    DEVICE
    static void EvaluateYDerivativesDevice(ValueType {{free_variable.var_name}}, const ValueType *rY, ValueType *rDY, const ValueType mSetVoltageDerivativeToZero, const ValueType mFixedVoltage, const ValueType *mParameters, const ValueType capacitance, const DeviceStimulusFunctor<ValueType> stim)
    {
        // Inputs:
        // Time units: millisecond
        {%- for state_var in state_vars %}
        {% if state_var.in_y_deriv %}ValueType {{ state_var.var }} = {{state_var.rY_lookup}};
        // Units: {{state_var.units}}; Initial value: {{state_var.initial_value}}
        {%- endif %}{%- endfor %}

        // Mathematics
        {% for deriv in y_derivative_equations %}{%- if deriv.is_voltage%}ValueType {{deriv.lhs}};{%- endif %}{%- endfor %}
        {%- for deriv in y_derivative_equations %}{%- if deriv.in_eqs_excl_voltage %}
        const ValueType {{deriv.lhs}} = {{deriv.rhs}}; // {{deriv.units}}{%- endif %}
        {%- endfor %}

        if (mSetVoltageDerivativeToZero)
        {
            {% for deriv in y_derivative_equations %}{%- if deriv.is_voltage%}{{deriv.lhs}} = 0.0;{%- endif %}{%- endfor %}
        }
        else
        {
        {% for deriv in y_derivative_equations %}{% if not deriv.in_eqs_excl_voltage %}{% if deriv.is_data_clamp_current is defined and deriv.is_data_clamp_current %}    // Special handling of data clamp current here
            // (we want to save expense of calling the interpolation method if possible.)
            ValueType {{ deriv.lhs }} = 0.0;
            if (mDataClampIsOn)
            {
                {{deriv.lhs}} = {{deriv.rhs}}; // {{deriv.units}}
            }{% else %}    {% if not deriv.is_voltage%}const ValueType {% endif %}{{deriv.lhs}} = {{deriv.rhs}}; // {{deriv.units}}{% endif %}
        {% endif %}{%- endfor %}}
        {% for deriv in y_derivatives %}
        rDY[{{loop.index0}}] = {{deriv}};
        {%- endfor %}
    }
    {% endset %}
    {{ body
   | replace('this->', '')
   | replace('HeartConfig::Instance()->GetCapacitance()', 'capacitance')
   | replace('GetIntracellularAreaStimulus', 'stim')
   | regex_replace('Signum\\s*\\(([^)]+)\\)', 'SignumDevice<ValueType>(\\1)')
   | regex_replace('pow\\s*\\(([^,]+),\\s*([^)]+)\\)', 'PowDevice<ValueType>(\\1, \\2)')
   | regex_replace('fabs\\s*\\(([^)]+)\\)', 'AbsDevice<ValueType>(\\1)')
   | regex_replace('(?<![\\w>])(-?\\d+\\.\\d+(?:[eE][+-]?\\d+)?)',
                   'static_cast<ValueType>(\\1)')
   | regex_replace('NV_Ith_S\\(\\s*([A-Za-z_]\\w*)\\s*,\\s*(\\d+)\\s*\\)', '\\1[\\2]')
    }}
    {%endif%}
    {%- if derived_quantities|length > 0 %}
    {{vector_decl}} ComputeDerivedQuantities(double {{free_variable.var_name}}, const {{vector_decl}} & rY);
    {%- endif %}
    {%- if jacobian_equations|length > 0 %}
    void EvaluateAnalyticJacobian(double {{free_variable.var_name}}, {{vector_decl}} rY, {{vector_decl}} rDY, CHASTE_CVODE_DENSE_MATRIX rJacobian, {{vector_decl}} rTmp1, {{vector_decl}} rTmp2, {{vector_decl}} rTmp3);
    //template<typename ValueType>
    //DEVICE
    //static void EvaluateAnalyticJacobianDevice(ValueType {{free_variable.var_name}}, ValueType *rY, ValueType *rDY, ValueType *rJacobian, ValueType *rTmp1, ValueType *rTmp2, ValueType *rTmp3, unsigned nvars, ValueType mSetVoltageDerivativeToZero, ValueType mFixedVoltage, ValueType *mParameters, ValueType capacitance);
    {% if not lookup_parameters is defined%}{% set body %}
    template<typename ValueType>
    DEVICE
    static void EvaluateAnalyticJacobianDevice(ValueType {{free_variable.var_name}}, const ValueType *rY, ValueType *rDY, ValueType *rJacobian, ValueType *rTmp1, ValueType *rTmp2, ValueType *rTmp3, const unsigned nvars, const ValueType mSetVoltageDerivativeToZero, const ValueType mFixedVoltage, const ValueType *mParameters, const ValueType capacitance, const DeviceStimulusFunctor<ValueType> stim)
    {
        {% for state_var in state_vars %}
        {%- if state_var.in_jacobian %}ValueType {{ state_var.var }} = {{state_var.rY_lookup}};
        // Units: {{state_var.units}}; Initial value: {{state_var.initial_value}}
        {% endif %}{%- endfor %}
        {% for equation in jacobian_equations %}const ValueType {{equation.lhs}} = {{equation.rhs}};
        {% endfor %}
        // Matrix entries{% for entry in jacobian_entries %}
        rJacobian[ {{entry.j}} * nvars + {{entry.i}} ] = {% if membrane_voltage_index == entry.i %}mSetVoltageDerivativeToZero ? 0.0 : ({{entry.entry}});{%- else %}{{entry.entry}};{%- endif %}
        {%- endfor %}
    }
    {% endset %}
    {{ body
   | replace('this->', '')
   | replace('HeartConfig::Instance()->GetCapacitance()', 'capacitance')
   | replace('GetIntracellularAreaStimulus', 'stim')
   | regex_replace('Signum\\s*\\(([^)]+)\\)', 'SignumDevice<ValueType>(\\1)')
   | regex_replace('pow\\s*\\(([^,]+),\\s*([^)]+)\\)', 'PowDevice<ValueType>(\\1, \\2)')
   | regex_replace('fabs\\s*\\(([^)]+)\\)', 'AbsDevice<ValueType>(\\1)')
   | regex_replace('(?<![\\w>])(-?\\d+\\.\\d+(?:[eE][+-]?\\d+)?)',
                   'static_cast<ValueType>(\\1)')
   | regex_replace('NV_Ith_S\\(\\s*([A-Za-z_]\\w*)\\s*,\\s*(\\d+)\\s*\\)', '\\1[\\2]')
    }}{% endif -%}
    {%- endif %}
{% include "Shared/hpp/CHASTE_CLASS_EXPORT" %}
#endif // CHASTE_CVODE