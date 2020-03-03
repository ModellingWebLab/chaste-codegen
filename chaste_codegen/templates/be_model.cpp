{% include "Normal/cpp/header_comments" %}
{% include "Normal/cpp/includes" %}
#include "CardiacNewtonSolver.hpp"
{% include "Normal/cpp/UseCellMLDefaultStimulus" %}
{% include "Normal/cpp/GetIntracellularCalciumConcentration" %}
{% include "BE/cpp/constructor" %}
{% include "Normal/cpp/destructor" %}
    
    {% if use_verify_state_variables %}
    void {{class_name}}::VerifyStateVariables()
    {
        /* We only expect CVODE to keep state variables to within its tolerances,
         * not exactly the bounds prescribed to each variable that are checked here.
         *
         * For 99.99% of paces this->mAbsTol works,
         * For 99.999% of paces 10*this->mAbsTol is fine,
         * but unfortunately 100x seems to be required on rare occasions for upstrokes.
         * This sounds bad, but is probably typically only 1e-5 or 1e-6.
         */
        const double tol = 100*this->mAbsTol;
        N_Vector rY = rGetStateVariables();
        {% for state_var in state_vars %}
        {%- if state_var.range_low != '' or  state_var.range_high != '' %}double {{ state_var.var }} = NV_Ith_S(rY,{{loop.index0}});
        // Units: {{state_var.units}}; Initial value: {{state_var.initial_value}}
        {% endif %}{%- endfor %}
        {% for state_var in state_vars %}
        {%- if state_var.range_low != '' or  state_var.range_high != '' %}if ({%- if state_var.range_low != '' %}{{ state_var.var }} < {{ state_var.range_low }} - tol{% endif %}{%- if state_var.range_low != '' and  state_var.range_high != '' %} || {% endif %}{%- if state_var.range_high != '' %}{{ state_var.var }} > {{ state_var.range_high }} + tol{% endif %})
        {
            EXCEPTION(DumpState("State variable {{ state_var.annotated_var_name }} has gone out of range. Check numerical parameters, for example time and space stepsizes, and/or solver tolerances"));
        }
        {% endif %}{%- endfor %}
    }

    {% endif %}{% include "Normal/cpp/GetIIonic" %}

    double {{class_name}}::ComputeResidual(double {{free_variable.var_name}}, const double rCurrentGuess[{{nonlinear_state_vars|length}}], double rResidual[{{nonlinear_state_vars|length}}])
    {
        // For state variable interpolation (SVI) we read in interpolated state variables,
        // otherwise for ionic current interpolation (ICI) we use the state variables of this model (node).
        N_Vector rY;
        bool made_new_cvode_vector = false;
        if (!pStateVariables)
        {
            rY = rGetStateVariables();
        }
        else
        {
            made_new_cvode_vector = true;
            rY = MakeNVector(*pStateVariables);
        }
        {% for state_var in state_vars %}
        {%- if state_var.in_ionic %}double {{ state_var.var }} = {% if loop.index0 == membrane_voltage_index %}(mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, {{loop.index0}}));{%- else %}NV_Ith_S(rY, {{loop.index0}});{%- endif %}
        // Units: {{state_var.units}}; Initial value: {{state_var.initial_value}}
        {% endif %}{%- endfor %}{% for ionic_var in ionic_vars %}
        const double {{ionic_var.lhs}} = {{ionic_var.rhs}}; // {{ionic_var.units}}
        {%- endfor %}

        const double i_ionic = var_chaste_interface__i_ionic;
        if (made_new_cvode_vector)
        {
            DeleteVector(rY);
        }
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    {%- if derived_quantities|length > 0 %}

    N_Vector {{class_name}}::ComputeDerivedQuantities(double {{free_variable.var_name}}, const N_Vector & rY)
    {
        // Inputs:
        // Time units: millisecond
        {% for state_var in state_vars %}
        {%- if state_var.in_derived_quant %}double {{ state_var.var }} = NV_Ith_S(rY,{{loop.index0}});
        // Units: {{state_var.units}}; Initial value: {{state_var.initial_value}}
        {% endif %}{%- endfor %}

        // Mathematics
        {%- for eq in derived_quantity_equations %}
        const double {{eq.lhs}} = {{eq.rhs}}; // {{eq.units}}
        {%- endfor %}

        N_Vector dqs = N_VNew_Serial({{derived_quantities|length}});
        {%- for quant in derived_quantities %}
        NV_Ith_S(dqs, {{loop.index0}}) = {{quant.var}};
        {%- endfor %}
        return dqs;
    }{% endif %}

    {%- if jacobian_equations|length > 0 %}

    void {{class_name}}::ComputeJacobian(double {{free_variable.var_name}}, const double rCurrentGuess[{{nonlinear_state_vars|length}}], double rJacobian[{{nonlinear_state_vars|length}}][{{nonlinear_state_vars|length}}])
    {
        {% for state_var in state_vars %}
        {%- if state_var.in_jacobian %}double {{ state_var.var }} = {% if loop.index0 == membrane_voltage_index %}(mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, {{loop.index0}}));{%- else %}NV_Ith_S(rY, {{loop.index0}});{%- endif %}
        // Units: {{state_var.units}}; Initial value: {{state_var.initial_value}}
        {% endif %}{%- endfor %}

        {% for equation in jacobian_equations %}
        const double {{equation.lhs}} = {{equation.rhs}};
        {%- endfor %}

        // Matrix entries{% for entry in jacobian_entries %}
        IJth(rJacobian, {{entry.i}}, {{entry.j}}) = {% if membrane_voltage_index == entry.i %}mSetVoltageDerivativeToZero ? 0.0 : ({{entry.entry}});{%- else %}{{entry.entry}};{%- endif %}
        {%- endfor %}
    }
    {%- endif %}

template<>
void OdeSystemInformation<{{class_name}}>::Initialise(void)
{
    this->mSystemName = "{{free_variable.system_name}}";
    this->mFreeVariableName = "{{free_variable.name}}";
    this->mFreeVariableUnits = "{{free_variable.units}}";

    {% for ode_info in ode_system_information %}// NV_Ith_S(rY,{{loop.index0}}):
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
