#ifdef CHASTE_CVODE
{% include "Shared/hpp/header_comments" %}
{% include "Shared/hpp/includes" %}
#include "AbstractCvodeCell.hpp"
{% with %}{% set base_class = "AbstractCvodeCell" %}{% include "Shared/hpp/class_declaration" %}{% endwith %}
{% include "Cvode/hpp/public" %}