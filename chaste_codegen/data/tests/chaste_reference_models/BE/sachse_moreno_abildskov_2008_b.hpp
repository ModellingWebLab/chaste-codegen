#ifndef CELLSACHSE_MORENO_ABILDSKOV_2008_BFROMCELLMLBACKWARDEULER_HPP_
#define CELLSACHSE_MORENO_ABILDSKOV_2008_BFROMCELLMLBACKWARDEULER_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: sachse_model_2007
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

class Cellsachse_moreno_abildskov_2008_bFromCellMLBackwardEuler : public AbstractBackwardEulerCardiacCell<6>
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractBackwardEulerCardiacCell<6> >(*this);
        
    }

    //
    // Settable parameters and readable variables
    //


private:
const bool is_concentration[7] = {false, false, false, false, false, false, false};
const bool is_probability[7] = {false, false, false, false, false, false, false};
public:

    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
    Cellsachse_moreno_abildskov_2008_bFromCellMLBackwardEuler(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Cellsachse_moreno_abildskov_2008_bFromCellMLBackwardEuler();
    void VerifyStateVariables();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);void ComputeResidual(double var_chaste_interface__environment__time_converted, const double rCurrentGuess[6], double rResidual[6]);
    void ComputeJacobian(double var_chaste_interface__environment__time_converted, const double rCurrentGuess[6], double rJacobian[6][6]);protected:
    void UpdateTransmembranePotential(double var_chaste_interface__environment__time_converted);
    void ComputeOneStepExceptVoltage(double var_chaste_interface__environment__time_converted);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time_converted, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Cellsachse_moreno_abildskov_2008_bFromCellMLBackwardEuler)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Cellsachse_moreno_abildskov_2008_bFromCellMLBackwardEuler * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Cellsachse_moreno_abildskov_2008_bFromCellMLBackwardEuler * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Cellsachse_moreno_abildskov_2008_bFromCellMLBackwardEuler(p_solver, p_stimulus);
        }

    }

}

#endif // CELLSACHSE_MORENO_ABILDSKOV_2008_BFROMCELLMLBACKWARDEULER_HPP_