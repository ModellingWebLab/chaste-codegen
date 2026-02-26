{% include "Shared/kernels/header_comments" %}
{% include "Shared/kernels/includes" %}
#include "ChasteCudaMacros.hpp"

{% include "Shared/kernels/EvaluateYDerivativesDevice"%}

{% include "Cvode/kernels/EvaluateAnalyticJacobianDevice" %}

{% include "Cvode/kernels/EvaluateSparseAnalyticJacobianDevice" %}

{% include "Shared/kernels/footer" %}