#ifndef CELLESPINOSA_MODEL_1998_NORMALFROMCELLMLBACKWARDEULER_HPP_
#define CELLESPINOSA_MODEL_1998_NORMALFROMCELLMLBACKWARDEULER_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version 0.0.1
//!
//! Model: espinosa_model_1998_normal
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>


#include "AbstractStimulusFunction.hpp"
#include "AbstractBackwardEulerCardiacCell.hpp"

class Cellespinosa_model_1998_normalFromCellMLBackwardEuler : public AbstractBackwardEulerCardiacCell<13>
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractBackwardEulerCardiacCell<13> >(*this);
        
    }

    //
    // Settable parameters and readable variables
    //

public:

    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
    double GetIntracellularCalciumConcentration();
    Cellespinosa_model_1998_normalFromCellMLBackwardEuler(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Cellespinosa_model_1998_normalFromCellMLBackwardEuler();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);void ComputeResidual(double var_chaste_interface__environment__time_converted, const double rCurrentGuess[13], double rResidual[13]);
    void ComputeJacobian(double var_chaste_interface__environment__time_converted, const double rCurrentGuess[13], double rJacobian[13][13]);protected:
    void UpdateTransmembranePotential(double var_chaste_interface__environment__time_converted);
    void ComputeOneStepExceptVoltage(double var_chaste_interface__environment__time_converted);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time_converted, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Cellespinosa_model_1998_normalFromCellMLBackwardEuler)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Cellespinosa_model_1998_normalFromCellMLBackwardEuler * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Cellespinosa_model_1998_normalFromCellMLBackwardEuler * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Cellespinosa_model_1998_normalFromCellMLBackwardEuler(p_solver, p_stimulus);
        }

    }

}

#endif // CELLESPINOSA_MODEL_1998_NORMALFROMCELLMLBACKWARDEULER_HPP_