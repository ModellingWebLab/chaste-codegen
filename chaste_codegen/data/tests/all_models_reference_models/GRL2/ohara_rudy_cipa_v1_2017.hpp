#ifndef CELLOHARA_RUDY_CIPA_V1_2017FROMCELLMLGRL2_HPP_
#define CELLOHARA_RUDY_CIPA_V1_2017FROMCELLMLGRL2_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: ohara_rudy_cipa_v1_2017
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

class Cellohara_rudy_cipa_v1_2017FromCellMLGRL2 : public AbstractGeneralizedRushLarsenCardiacCell
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
    Cellohara_rudy_cipa_v1_2017FromCellMLGRL2(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Cellohara_rudy_cipa_v1_2017FromCellMLGRL2();
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
    double EvaluateYDerivative8(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative8(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative9(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative9(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative10(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative10(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative11(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative11(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative12(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative12(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative13(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative13(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative14(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative14(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative15(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative15(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative16(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative16(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative17(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative17(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative18(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative18(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative19(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative19(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative20(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative20(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative21(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative21(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative22(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative22(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative23(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative23(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative24(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative24(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative25(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative25(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative26(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative26(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative27(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative27(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative28(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative28(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative29(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative29(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative30(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative30(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative31(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative31(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative32(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative32(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative33(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative33(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative34(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative34(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative35(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative35(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative36(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative36(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative37(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative37(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative38(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative38(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative39(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative39(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative40(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative40(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative41(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative41(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative42(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative42(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative43(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative43(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative44(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative44(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative45(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative45(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative46(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative46(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative47(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative47(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Cellohara_rudy_cipa_v1_2017FromCellMLGRL2)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Cellohara_rudy_cipa_v1_2017FromCellMLGRL2 * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Cellohara_rudy_cipa_v1_2017FromCellMLGRL2 * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Cellohara_rudy_cipa_v1_2017FromCellMLGRL2(p_solver, p_stimulus);
        }

    }

}

#endif // CELLOHARA_RUDY_CIPA_V1_2017FROMCELLMLGRL2_HPP_