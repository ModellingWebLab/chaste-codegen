#ifdef CHASTE_CVODE
{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "AbstractCvodeCellWithDataClamp.hpp"

class {{class_name}} : public AbstractCvodeCellWithDataClamp{%- if dynamically_loadable %}, public AbstractDynamicallyLoadableEntity{%- endif %}
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractCvodeCellWithDataClamp >(*this);
{% include "Shared/hpp/AbstractDynamicallyLoadableEntity" %}
    }
{% include "Cvode/hpp/public" %}