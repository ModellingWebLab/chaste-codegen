#ifndef CELLDIFRANCESCO_NOBLE_MODEL_1985FROMCELLMLGRL2_HPP_
#define CELLDIFRANCESCO_NOBLE_MODEL_1985FROMCELLMLGRL2_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: difrancesco_noble_model_1985
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: GeneralizedRushLarsenSecondOrder)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractStimulusFunction.hpp"
#include "AbstractGeneralizedRushLarsenCardiacCell.hpp"

class Celldifrancesco_noble_model_1985FromCellMLGRL2 : public AbstractGeneralizedRushLarsenCardiacCell
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
    Celldifrancesco_noble_model_1985FromCellMLGRL2(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Celldifrancesco_noble_model_1985FromCellMLGRL2();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);
    void UpdateTransmembranePotential(double var_chaste_interface__environment__time_converted);
    void ComputeOneStepExceptVoltage(double var_chaste_interface__environment__time_converted);
    
    double EvaluateYDerivative0(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative0(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative1(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative1(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative2(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative2(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative3(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative3(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative4(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative4(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative5(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative5(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative6(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative6(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative7(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative7(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative8(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative8(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative9(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative9(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative10(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative10(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative11(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative11(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative12(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative12(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative13(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative13(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative14(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative14(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative15(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative15(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time_converted, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Celldifrancesco_noble_model_1985FromCellMLGRL2)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Celldifrancesco_noble_model_1985FromCellMLGRL2 * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Celldifrancesco_noble_model_1985FromCellMLGRL2 * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Celldifrancesco_noble_model_1985FromCellMLGRL2(p_solver, p_stimulus);
        }

    }

}

#endif // CELLDIFRANCESCO_NOBLE_MODEL_1985FROMCELLMLGRL2_HPP_