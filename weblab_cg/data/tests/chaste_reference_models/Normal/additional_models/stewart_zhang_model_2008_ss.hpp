#ifndef CELLSTEWART_ZHANG_MODEL_2008_SSFROMCELLML_HPP_
#define CELLSTEWART_ZHANG_MODEL_2008_SSFROMCELLML_HPP_

//! @file
//! 
//! This source file was generated from CellML.
//! 
//! Model: stewart_zhang_model_2008
//! 
//! Processed by weblab_cg: https://github.com/ModellingWebLab/weblab-cg
//!     (translator: weblab_cg, model type: normal, options: )
//! on 2019-12-16 14:02:00
//! 
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractCardiacCell.hpp"

#include "AbstractStimulusFunction.hpp"

class Cellstewart_zhang_model_2008_ssFromCellML : public AbstractCardiacCell
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractCardiacCell >(*this);
        
    }
    
    // 
    // Settable parameters and readable variables
    // 
    
public:
    double GetIntracellularCalciumConcentration();
    Cellstewart_zhang_model_2008_ssFromCellML(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Cellstewart_zhang_model_2008_ssFromCellML();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);
    void EvaluateYDerivatives(double var_chaste_interface__environment__time, const std::vector<double>& rY, std::vector<double>& rDY);
};


// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Cellstewart_zhang_model_2008_ssFromCellML)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Cellstewart_zhang_model_2008_ssFromCellML * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }
        
        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Cellstewart_zhang_model_2008_ssFromCellML * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Cellstewart_zhang_model_2008_ssFromCellML(p_solver, p_stimulus);
        }
        
    }
    
}

#endif // CELLSTEWART_ZHANG_MODEL_2008_SSFROMCELLML_HPP_