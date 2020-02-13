#ifdef CHASTE_CVODE
#ifndef CELLVISWANATHAN_MODEL_1999_EPIFROMCELLMLCVODE_HPP_
#define CELLVISWANATHAN_MODEL_1999_EPIFROMCELLMLCVODE_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version 0.0.1
//!
//! Model: viswanathan_model_1999_epi
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: CVODE )
//! on 2020-02-13 18:15:08
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractCvodeCell.hpp"

#include "AbstractStimulusFunction.hpp"

class Cellviswanathan_model_1999_epiFromCellMLCvode : public AbstractCvodeCell
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractCvodeCell >(*this);
        
    }
    
    // 
    // Settable parameters and readable variables
    // 
    
public:
    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
    double GetIntracellularCalciumConcentration();
    Cellviswanathan_model_1999_epiFromCellMLCvode(boost::shared_ptr<AbstractIvpOdeSolver> pOdeSolver /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Cellviswanathan_model_1999_epiFromCellMLCvode();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);
    void EvaluateYDerivatives(double var_chaste_interface__environment__time_converted, const N_Vector rY, N_Vector rDY);
};


// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Cellviswanathan_model_1999_epiFromCellMLCvode)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Cellviswanathan_model_1999_epiFromCellMLCvode * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }
        
        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Cellviswanathan_model_1999_epiFromCellMLCvode * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Cellviswanathan_model_1999_epiFromCellMLCvode(p_solver, p_stimulus);
        }
        
    }
    
}

#endif // CELLVISWANATHAN_MODEL_1999_EPIFROMCELLMLCVODE_HPP_
#endif // CHASTE_CVODE

