{% include "Device/header_comments" %}
// Functions for the {{model_name}} model that can be compiled for both CPU and GPU
struct {{class_name}}Device
{
    static constexpr unsigned NUM_STATE_VARIABLES = {{ state_vars|length }}u;
    static constexpr unsigned NUM_PARAMETERS = {{ modifiable_parameters|length }}u;
{% include "Device/EvaluateYDerivatives" -%}
};

#endif // {% filter upper %}{{class_name}}DEVICE_HPP_{% endfilter %}
