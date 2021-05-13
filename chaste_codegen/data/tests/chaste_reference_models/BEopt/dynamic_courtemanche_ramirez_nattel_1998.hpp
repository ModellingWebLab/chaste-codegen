#ifndef DYNAMICCOURTEMANCHE_RAMIREZ_NATTEL_1998FROMCELLMLBACKWARDEULEROPT_HPP_
#define DYNAMICCOURTEMANCHE_RAMIREZ_NATTEL_1998FROMCELLMLBACKWARDEULEROPT_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: courtemanche_1998
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: BackwardEulerOpt)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractDynamicallyLoadableEntity.hpp"
#include "AbstractStimulusFunction.hpp"
#include "AbstractBackwardEulerCardiacCell.hpp"

class Dynamiccourtemanche_ramirez_nattel_1998FromCellMLBackwardEulerOpt : public AbstractBackwardEulerCardiacCell<8>, public AbstractDynamicallyLoadableEntity
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractBackwardEulerCardiacCell<8> >(*this);
        archive & boost::serialization::base_object<AbstractDynamicallyLoadableEntity>(*this);
    }

    //
    // Settable parameters and readable variables
    //

private:
    static AbstractBackwardEulerCardiacCell<8>* CreateMethod(boost::shared_ptr<AbstractIvpOdeSolver> p_solver, boost::shared_ptr<AbstractStimulusFunction> p_stimulus);
    static bool registered;
public:

    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
    double GetIntracellularCalciumConcentration();
    Dynamiccourtemanche_ramirez_nattel_1998FromCellMLBackwardEulerOpt(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Dynamiccourtemanche_ramirez_nattel_1998FromCellMLBackwardEulerOpt();
    AbstractLookupTableCollection* GetLookupTableCollection();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);void ComputeResidual(double var_chaste_interface__environment__time, const double rCurrentGuess[8], double rResidual[8]);
    void ComputeJacobian(double var_chaste_interface__environment__time, const double rCurrentGuess[8], double rJacobian[8][8]);protected:
    void UpdateTransmembranePotential(double var_chaste_interface__environment__time);
    void ComputeOneStepExceptVoltage(double var_chaste_interface__environment__time);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Dynamiccourtemanche_ramirez_nattel_1998FromCellMLBackwardEulerOpt)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Dynamiccourtemanche_ramirez_nattel_1998FromCellMLBackwardEulerOpt * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Dynamiccourtemanche_ramirez_nattel_1998FromCellMLBackwardEulerOpt * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Dynamiccourtemanche_ramirez_nattel_1998FromCellMLBackwardEulerOpt(p_solver, p_stimulus);
        }

    }

}

#endif // DYNAMICCOURTEMANCHE_RAMIREZ_NATTEL_1998FROMCELLMLBACKWARDEULEROPT_HPP_