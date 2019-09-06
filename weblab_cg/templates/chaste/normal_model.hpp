{% filter upper %}#ifndef {{class_name}}FROMCELLML_HPP_
#define {{class_name}}FROMCELLML_HPP_{% endfilter %}

//! @file
//! 
//! This source file was generated from CellML.
//! 
//! Model: {{model_name_from_file}}
//! 
//! Processed by webalab_cg - CellML Tools in Python
//!     (translators: , webalab_cg: , options: normal)
//! on {{generation_date}}
//! 
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractCardiacCell.hpp"
#include "AbstractDynamicallyLoadableEntity.hpp"
#include "AbstractStimulusFunction.hpp"

class {{class_name}}FromCellML : public AbstractCardiacCell, public AbstractDynamicallyLoadableEntity
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractCardiacCell >(*this);
        archive & boost::serialization::base_object<AbstractDynamicallyLoadableEntity>(*this);
    }
    
    // 
    // Settable parameters and readable variables
    // 
    
public:
	{%- if not cellml_default_stimulus_equations is none %}
    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
	{%- endif %}
	{%- if use_get_intracellular_calcium_concentration %}
    double GetIntracellularCalciumConcentration();
	{%- endif %}
    {class_name}}FromCellML(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~{{class_name}}FromCellML();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);
    void EvaluateYDerivatives(double var_chaste_interface__environment__time, const std::vector<double>& rY, std::vector<double>& rDY);
};


// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT({{class_name}}FromCellML)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const {{class_name}}FromCellML * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }
        
        template<class Archive>
        inline void load_construct_data(
            Archive & ar, {{class_name}}FromCellML * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t){{class_name}}FromCellML(p_solver, p_stimulus);
        }
        
    }
    
}

#endif // {% filter upper %}{{class_name}}FROMCELLML_HPP_{% endfilter %}
