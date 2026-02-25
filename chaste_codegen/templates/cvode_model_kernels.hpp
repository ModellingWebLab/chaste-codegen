#include "{{file_name}}{{header_ext}}"
#include "ChasteCudaMacros.hpp"
{% include "Shared/kernels/EvaluateYDerivativesDevice"%}
{% include "Cvode/kernels/EvaluateAnalyticJacobianDevice" %}
{% include "Cvode/kernels/EvaluateSparseAnalyticJacobianDevice" %}
#include "ChasteCpuMacros.hpp"