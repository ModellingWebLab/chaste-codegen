#ifdef CHASTE_CVODE
{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "AbstractCvodeCell.hpp"

class {{class_name}} : public AbstractCvodeCell{%- if dynamically_loadable %}, public AbstractDynamicallyLoadableEntity{%- endif %}
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractCvodeCell >(*this);
{% include "Shared/hpp/AbstractDynamicallyLoadableEntity" %}
    }
{% include "Cvode/hpp/public" %}