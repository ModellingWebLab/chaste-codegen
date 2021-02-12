#ifndef CELLGRANDI_PASQUALINI_BERS_2010_SSFROMCELLMLRUSHLARSEN_HPP_
#define CELLGRANDI_PASQUALINI_BERS_2010_SSFROMCELLMLRUSHLARSEN_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: grandi_pasqualini_bers_2010
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: RushLarsen)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractStimulusFunction.hpp"
#include "AbstractRushLarsenCardiacCell.hpp"

class Cellgrandi_pasqualini_bers_2010_ssFromCellMLRushLarsen : public AbstractRushLarsenCardiacCell
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractRushLarsenCardiacCell >(*this);
        
    }

    //
    // Settable parameters and readable variables
    //

public:

    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
    double GetIntracellularCalciumConcentration();
    Cellgrandi_pasqualini_bers_2010_ssFromCellMLRushLarsen(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Cellgrandi_pasqualini_bers_2010_ssFromCellMLRushLarsen();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);
    void EvaluateEquations(double var_chaste_interface__environment__time, std::vector<double> &rDY, std::vector<double> &rAlphaOrTau, std::vector<double> &rBetaOrInf);
    void ComputeOneStepExceptVoltage(const std::vector<double> &rDY, const std::vector<double> &rAlphaOrTau, const std::vector<double> &rBetaOrInf);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Cellgrandi_pasqualini_bers_2010_ssFromCellMLRushLarsen)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Cellgrandi_pasqualini_bers_2010_ssFromCellMLRushLarsen * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Cellgrandi_pasqualini_bers_2010_ssFromCellMLRushLarsen * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Cellgrandi_pasqualini_bers_2010_ssFromCellMLRushLarsen(p_solver, p_stimulus);
        }

    }

}

#endif // CELLGRANDI_PASQUALINI_BERS_2010_SSFROMCELLMLRUSHLARSEN_HPP_