#ifndef CELLBEELER_REUTER_MODEL_1977FROMCELLMLGRL1OPT_HPP_
#define CELLBEELER_REUTER_MODEL_1977FROMCELLMLGRL1OPT_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: beeler_reuter_model_1977
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: GeneralizedRushLarsenFirstOrderOpt)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractStimulusFunction.hpp"
#include "AbstractGeneralizedRushLarsenCardiacCell.hpp"

class Cellbeeler_reuter_model_1977FromCellMLGRL1Opt : public AbstractGeneralizedRushLarsenCardiacCell
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractGeneralizedRushLarsenCardiacCell >(*this);
        
    }

    //
    // Settable parameters and readable variables
    //

public:

    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
    double GetIntracellularCalciumConcentration();
    Cellbeeler_reuter_model_1977FromCellMLGRL1Opt(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Cellbeeler_reuter_model_1977FromCellMLGRL1Opt();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);
    void UpdateTransmembranePotential(double var_chaste_interface__environment__time);
    void ComputeOneStepExceptVoltage(double var_chaste_interface__environment__time);
    
    double EvaluateYDerivative0(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative0(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative1(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative1(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative2(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative2(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative3(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative3(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative4(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative4(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative5(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative5(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative6(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative6(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative7(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative7(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Cellbeeler_reuter_model_1977FromCellMLGRL1Opt)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Cellbeeler_reuter_model_1977FromCellMLGRL1Opt * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Cellbeeler_reuter_model_1977FromCellMLGRL1Opt * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Cellbeeler_reuter_model_1977FromCellMLGRL1Opt(p_solver, p_stimulus);
        }

    }

}

#endif // CELLBEELER_REUTER_MODEL_1977FROMCELLMLGRL1OPT_HPP_