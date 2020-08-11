#ifndef CELLMATSUOKA_MODEL_2003FROMCELLMLBACKWARDEULER_HPP_
#define CELLMATSUOKA_MODEL_2003FROMCELLMLBACKWARDEULER_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version 0.4.0
//!
//! Model: matsuoka_model_2003
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: BackwardEuler)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractStimulusFunction.hpp"
#include "AbstractBackwardEulerCardiacCell.hpp"

class Cellmatsuoka_model_2003FromCellMLBackwardEuler : public AbstractBackwardEulerCardiacCell<25>
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractBackwardEulerCardiacCell<25> >(*this);
        
    }

    //
    // Settable parameters and readable variables
    //

public:

    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
    Cellmatsuoka_model_2003FromCellMLBackwardEuler(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Cellmatsuoka_model_2003FromCellMLBackwardEuler();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);void ComputeResidual(double var_chaste_interface__environment__time, const double rCurrentGuess[25], double rResidual[25]);
    void ComputeJacobian(double var_chaste_interface__environment__time, const double rCurrentGuess[25], double rJacobian[25][25]);protected:
    void UpdateTransmembranePotential(double var_chaste_interface__environment__time);
    void ComputeOneStepExceptVoltage(double var_chaste_interface__environment__time);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Cellmatsuoka_model_2003FromCellMLBackwardEuler)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Cellmatsuoka_model_2003FromCellMLBackwardEuler * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Cellmatsuoka_model_2003FromCellMLBackwardEuler * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Cellmatsuoka_model_2003FromCellMLBackwardEuler(p_solver, p_stimulus);
        }

    }

}

#endif // CELLMATSUOKA_MODEL_2003FROMCELLMLBACKWARDEULER_HPP_