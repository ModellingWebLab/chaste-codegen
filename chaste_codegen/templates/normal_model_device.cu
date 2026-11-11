{% include "Device/file_comments" %}

#include "{{file_name}}Device.hpp"
#include "ForwardEulerDeviceSolver.hpp"
{% for value_type in ['float', 'double'] %}
void {{class_name}}SolveOnDevice(const CardiacCellDeviceData<{{value_type}}>& rData)
{
    SolveCellsForwardEulerOnDevice<{{class_name}}Device, {{value_type}}>(rData);
}
{% endfor %}