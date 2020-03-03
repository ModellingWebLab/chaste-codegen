{% include "Normal/cpp/header_comments" %}
{% include "Normal/cpp/includes" %}
{% include "Normal/cpp/UseCellMLDefaultStimulus" %}
{% include "Normal/cpp/GetIntracellularCalciumConcentration" %}
{% include "Normal/cpp/constructor" %}
{% include "Normal/cpp/destructor" %}

    {% if use_verify_state_variables %}
    void {{class_name}}::VerifyStateVariables()
    {
        std::vector<double>& rY = rGetStateVariables();
        {% for state_var in state_vars %}
        {%- if state_var.range_low != '' or  state_var.range_high != '' %}double {{ state_var.var }} = rY[{{loop.index0}}];
        // Units: {{state_var.units}}; Initial value: {{state_var.initial_value}}
        {% endif %}{%- endfor %}
        {% for state_var in state_vars %}
        {%- if state_var.range_low != '' or  state_var.range_high != '' %}if ({%- if state_var.range_low != '' %}{{ state_var.var }} < {{ state_var.range_low }}{% endif %}{%- if state_var.range_low != '' and  state_var.range_high != '' %} || {% endif %}{%- if state_var.range_high != '' %}{{ state_var.var }} > {{ state_var.range_high }}{% endif %})
        {
            EXCEPTION(DumpState("State variable {{ state_var.annotated_var_name }} has gone out of range. Check numerical parameters, for example time and space stepsizes, and/or solver tolerances"));
        }
        {% endif %}{%- endfor %}
    }

    {% endif %}{% include "Normal/cpp/GetIIonic" %}

    void {{class_name}}::EvaluateYDerivatives(double {{free_variable.var_name}}, const std::vector<double>& rY, std::vector<double>& rDY)
    {
        // Inputs:
        // Time units: millisecond
        {%- for state_var in state_vars %}
        {% if state_var.in_y_deriv %}double {{ state_var.var }} = {% if loop.index0 == membrane_voltage_index %}(mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[{{loop.index0}}]);{%- else %}rY[{{loop.index0}}];{%- endif %}{%- endif %}
        // Units: {{state_var.units}}; Initial value: {{state_var.initial_value}}
        {%- endfor %}

        // Mathematics
        {% for deriv in y_derivative_equations %}{%- if deriv.is_voltage%}double {{deriv.lhs}};{%- endif %}{%- endfor %}
        {%- for deriv in y_derivative_equations %}{%- if not deriv.in_membrane_voltage %}
        const double {{deriv.lhs}} = {{deriv.rhs}}; // {{deriv.units}}{%- endif %}
        {%- endfor %}

        if (mSetVoltageDerivativeToZero)
        {
            {% for deriv in y_derivative_equations %}{%- if deriv.is_voltage%}{{deriv.lhs}} = 0.0;{%- endif %}{%- endfor %}
        }
        else
        {
            {%- for deriv in y_derivative_equations %}{% if deriv.in_membrane_voltage %}
            {% if not deriv.is_voltage%}const double {% endif %}{{deriv.lhs}} = {{deriv.rhs}}; // {{deriv.units}}{%- endif %}
            {%- endfor %}
        }
        {% for deriv in y_derivatives %}
        rDY[{{loop.index0}}] = {{deriv}};
        {%- endfor %}
    }
    {%- if derived_quantities|length > 0 %}

    std::vector<double> {{class_name}}::ComputeDerivedQuantities(double {{free_variable.var_name}}, const std::vector<double> & rY)
    {
        // Inputs:
        // Time units: millisecond
        {% for state_var in state_vars %}
        {%- if state_var.in_derived_quant %}double {{ state_var.var }} = rY[{{loop.index0}}];
        // Units: {{state_var.units}}; Initial value: {{state_var.initial_value}}
        {% endif %}{%- endfor %}

        // Mathematics
        {%- for eq in derived_quantity_equations %}
        const double {{eq.lhs}} = {{eq.rhs}}; // {{eq.units}}
        {%- endfor %}

        std::vector<double> dqs({{derived_quantities|length}});
        {%- for quant in derived_quantities %}
        dqs[{{loop.index0}}] = {{quant.var}};
        {%- endfor %}
        return dqs;
    }{% endif %}

template<>
void OdeSystemInformation<{{class_name}}>::Initialise(void)
{
    this->mSystemName = "{{free_variable.system_name}}";
    this->mFreeVariableName = "{{free_variable.name}}";
    this->mFreeVariableUnits = "{{free_variable.units}}";

    {% for ode_info in ode_system_information %}// rY[{{loop.index0}}]:
    this->mVariableNames.push_back("{{ode_info.name}}");
    this->mVariableUnits.push_back("{{ode_info.units}}");
    this->mInitialConditions.push_back({{ode_info.initial_value}});

    {% endfor %}{% for param in modifiable_parameters %}// mParameters[{{loop.index0}}]:
    this->mParameterNames.push_back("{{param["name"]}}");
    this->mParameterUnits.push_back("{{param["units"]}}");

    {% endfor %}{% for param in derived_quantities %}// Derived Quantity index [{{loop.index0}}]:
    this->mParameterNames.push_back("{{param["name"]}}");
    this->mParameterUnits.push_back("{{param["units"]}}");

    {% endfor %}{% for attr in named_attributes %}
    this->mAttributes["{{attr["name"]}}"] = {{attr["value"]}};
    {% endfor %}this->mInitialised = true;
}


// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT({{class_name}})
{% if dynamically_loadable %}extern "C"
{
    AbstractCardiacCellInterface* MakeCardiacCell(
            boost::shared_ptr<AbstractIvpOdeSolver> pSolver,
            boost::shared_ptr<AbstractStimulusFunction> pStimulus)
    {
        return new {{class_name}}(pSolver, pStimulus);
    }

}{%- endif %}
