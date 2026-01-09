{%- include "Shared/cpp/header_comments" %} 
#include <cmath>
#include "StimulusEvaluatorCuda.hpp"   // DeviceStimulusFunctor (+ includes StimulusDescriptor)

{# The functor template for GPU use. It pulls in the small method fragments
   you created under BE/cpp (ComputeJacobian, ComputeResidual,
   UpdateTransmembranePotential, ComputeOneStepExceptVoltagehelpers). #}

template<typename value_type>
struct {{ class_name }}
{
    using value_type_t = value_type;
    static constexpr unsigned TOTAL_SIZE = {{ state_vars|length }}u;
    static constexpr unsigned NONLINEAR_SIZE = {{ nonlinear_state_vars|length }}u;

    {% include "BE/cpp/FunctorComputeOneStepExceptVoltageHelpers" %} {# (file contains SolveClosedFormVars, FillInitialGuess, ScatterSolution) #}

    {% include "BE/cpp/FunctorComputeResidual" %}

    {% include "BE/cpp/FunctorComputeJacobian" %}

    {% include "BE/cpp/FunctorUpdateTransmembranePotential" %}
};
