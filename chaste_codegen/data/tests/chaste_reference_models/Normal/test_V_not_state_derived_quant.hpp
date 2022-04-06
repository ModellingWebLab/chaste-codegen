#ifndef CELLTEST_V_NOT_STATE_DERIVED_QUANTFROMCELLML_HPP_
#define CELLTEST_V_NOT_STATE_DERIVED_QUANTFROMCELLML_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: component_with_units
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: Normal)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractStimulusFunction.hpp"
#include "AbstractCardiacCell.hpp"

class Celltest_V_not_state_derived_quantFromCellML : public AbstractCardiacCell
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

    Celltest_V_not_state_derived_quantFromCellML(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Celltest_V_not_state_derived_quantFromCellML();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);
    void EvaluateYDerivatives(double var_chaste_interface__membrane__time_converted, const std::vector<double>& rY, std::vector<double>& rDY);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__membrane__time_converted, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Celltest_V_not_state_derived_quantFromCellML)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Celltest_V_not_state_derived_quantFromCellML * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Celltest_V_not_state_derived_quantFromCellML * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Celltest_V_not_state_derived_quantFromCellML(p_solver, p_stimulus);
        }

    }

}

#endif // CELLTEST_V_NOT_STATE_DERIVED_QUANTFROMCELLML_HPP_