#include "{{file_name}}{{header_ext}}"
#include "ChasteCudaMacros.hpp"
{% include "Shared/kernels/EvaluateYDerivativesGPU"%}
{% include "Cvode/kernels/EvaluateAnalyticJacobianGPU" %}
{% include "Cvode/kernels/EvaluateSparseAnalyticJacobianGPU" %}
#include "ChasteCpuMacros.hpp"