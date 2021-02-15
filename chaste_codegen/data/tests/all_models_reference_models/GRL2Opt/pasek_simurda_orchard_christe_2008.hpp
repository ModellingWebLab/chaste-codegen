#ifndef CELLPASEK_SIMURDA_ORCHARD_CHRISTE_2008FROMCELLMLGRL2OPT_HPP_
#define CELLPASEK_SIMURDA_ORCHARD_CHRISTE_2008FROMCELLMLGRL2OPT_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: pasek_model_2008
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: GeneralizedRushLarsenSecondOrderOpt)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractStimulusFunction.hpp"
#include "AbstractGeneralizedRushLarsenCardiacCell.hpp"

class Cellpasek_simurda_orchard_christe_2008FromCellMLGRL2Opt : public AbstractGeneralizedRushLarsenCardiacCell
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
    Cellpasek_simurda_orchard_christe_2008FromCellMLGRL2Opt(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Cellpasek_simurda_orchard_christe_2008FromCellMLGRL2Opt();
    AbstractLookupTableCollection* GetLookupTableCollection();
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
    double EvaluateYDerivative16(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative16(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative17(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative17(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative18(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative18(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative19(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative19(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative20(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative20(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative21(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative21(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative22(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative22(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative23(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative23(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative24(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative24(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative25(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative25(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative26(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative26(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative27(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative27(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative28(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative28(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative29(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative29(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative30(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative30(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative31(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative31(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative32(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative32(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative33(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative33(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative34(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative34(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative35(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative35(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative36(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative36(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative37(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative37(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative38(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative38(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative39(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative39(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative40(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative40(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative41(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative41(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative42(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative42(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative43(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative43(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative44(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative44(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative45(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative45(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative46(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative46(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative47(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative47(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative48(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative48(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative49(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative49(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative50(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative50(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative51(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative51(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative52(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative52(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative53(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative53(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative54(double var_chaste_interface__environment__time_converted, std::vector<double>& rY);
    double EvaluatePartialDerivative54(double var_chaste_interface__environment__time_converted, std::vector<double>& rY, double delta, bool forceNumerical=false);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time_converted, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Cellpasek_simurda_orchard_christe_2008FromCellMLGRL2Opt)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Cellpasek_simurda_orchard_christe_2008FromCellMLGRL2Opt * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Cellpasek_simurda_orchard_christe_2008FromCellMLGRL2Opt * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Cellpasek_simurda_orchard_christe_2008FromCellMLGRL2Opt(p_solver, p_stimulus);
        }

    }

}

#endif // CELLPASEK_SIMURDA_ORCHARD_CHRISTE_2008FROMCELLMLGRL2OPT_HPP_