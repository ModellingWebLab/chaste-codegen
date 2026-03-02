{% include "Shared/kernels/header_comments" %}
{% include "Shared/kernels/includes" %}


{% include "BE/kernels/ComputeOneStepExceptVoltageDevice" %} {# (file contains SolveClosedFormVars, FillInitialGuess, ScatterSolution) #}

{% if nonlinear_state_vars|length > 0 -%}
{% include "BE/kernels/ComputeResidualDevice" %}

{% include "BE/kernels/ComputeJacobianDevice" %}
{%- endif %}

{% include "BE/kernels/UpdateTransmembranePotentialDevice" %}

{% include "Shared/kernels/footer" %}