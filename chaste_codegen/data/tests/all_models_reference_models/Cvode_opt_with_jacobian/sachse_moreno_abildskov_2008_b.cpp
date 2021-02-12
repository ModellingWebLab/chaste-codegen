#ifdef CHASTE_CVODE
//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: sachse_model_2007
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: AnalyticCvodeOpt)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "sachse_moreno_abildskov_2008_b.hpp"
#include <cmath>
#include <cassert>
#include <memory>
#include "Exception.hpp"
#include "Warnings.hpp"
#include "OdeSystemInformation.hpp"
#include "RegularStimulus.hpp"
#include "HeartConfig.hpp"
#include "IsNan.hpp"
#include "MathsCustomFunctions.hpp"

class Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables : public AbstractLookupTableCollection
{
public:
    static Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables* Instance()
    {
        if (mpInstance.get() == NULL)
        {
            mpInstance.reset(new Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables);
        }
        return mpInstance.get();
    }

    void FreeMemory()
    {

        mNeedsRegeneration.assign(mNeedsRegeneration.size(), true);
    }

    // Row lookup methods
    // using linear-interpolation



    ~Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables()
    {

    }

protected:
    Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables(const Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables&);
    Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables& operator= (const Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables&);
    Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables()
    {
        assert(mpInstance.get() == NULL);
        mKeyingVariableNames.resize(0);
        mNumberOfTables.resize(0);
        mTableMins.resize(0);
        mTableSteps.resize(0);
        mTableStepInverses.resize(0);
        mTableMaxs.resize(0);
        mNeedsRegeneration.resize(0);

        Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables::RegenerateTables();
    }

    void RegenerateTables()
    {
        AbstractLookupTableCollection::EventHandler::BeginEvent(AbstractLookupTableCollection::EventHandler::GENERATE_TABLES);

        AbstractLookupTableCollection::EventHandler::EndEvent(AbstractLookupTableCollection::EventHandler::GENERATE_TABLES);
    }

private:
    /** The single instance of the class */
    static std::shared_ptr<Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables> mpInstance;

};

std::shared_ptr<Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables> Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables::mpInstance;

    boost::shared_ptr<RegularStimulus> Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt::UseCellMLDefaultStimulus()
    {
        // Use the default stimulus specified by CellML metadata
        const double var_chaste_interface__I_stim__stim_duration_converted = 1.0; // millisecond
        const double var_chaste_interface__I_stim__stim_period_converted = 1000.0; // millisecond
        const double var_chaste_interface__I_stim__stim_start_converted = 100.0; // millisecond
        const double var_chaste_interface__I_stim__stim_amplitude_converted = 0.0001 * HeartConfig::Instance()->GetCapacitance() / NV_Ith_S(mParameters, 2); // uA_per_cm2
        boost::shared_ptr<RegularStimulus> p_cellml_stim(new RegularStimulus(
                -fabs(var_chaste_interface__I_stim__stim_amplitude_converted),
                var_chaste_interface__I_stim__stim_duration_converted,
                var_chaste_interface__I_stim__stim_period_converted,
                var_chaste_interface__I_stim__stim_start_converted
                ));
        mpIntracellularStimulus = p_cellml_stim;
        return p_cellml_stim;
    }

    Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt::Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt(boost::shared_ptr<AbstractIvpOdeSolver> pOdeSolver /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractCvodeCell(
                pOdeSolver,
                7,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        //
        this->mpSystemInfo = OdeSystemInformation<Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt>::Instance();
        Init();

        // We have a default stimulus specified in the CellML file metadata
        this->mHasDefaultStimulusFromCellML = true;
        mUseAnalyticJacobian = true;
        mHasAnalyticJacobian = true;
        
        NV_Ith_S(this->mParameters, 0) = 140.0; // (var_model_parameters__Ki) [millimolar]
        NV_Ith_S(this->mParameters, 1) = 5.0; // (var_model_parameters__Ko) [millimolar]
        NV_Ith_S(this->mParameters, 2) = 4.5000000000000001e-6; // (var_membrane__Cm) [microfarad]
        NV_Ith_S(this->mParameters, 3) = 5.4000000000000004e-9; // (var_I_Shkr__PShkr) [microlitre_per_second]
        NV_Ith_S(this->mParameters, 4) = 0.001; // (var_I_Kir__GKir) [microsiemens]
        NV_Ith_S(this->mParameters, 5) = 6.9e-6; // (var_I_b__Gb) [microsiemens]
        NV_Ith_S(this->mParameters, 6) = 295.0; // (var_model_parameters__T) [kelvin]
    }

    Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt::~Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt()
    {
    }

    AbstractLookupTableCollection* Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt::GetLookupTableCollection()
    {
        return Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt_LookupTables::Instance();
    }
    
    double Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt::GetIIonic(const std::vector<double>* pStateVariables)
    {
        // For state variable interpolation (SVI) we read in interpolated state variables,
        // otherwise for ionic current interpolation (ICI) we use the state variables of this model (node).
        N_Vector rY;
        bool made_new_cvode_vector = false;
        if (!pStateVariables)
        {
            rY = rGetStateVariables();
        }
        else
        {
            made_new_cvode_vector = true;
            rY = MakeNVector(*pStateVariables);
        }
        double var_chaste_interface__membrane__Vm = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, 0));
        // Units: millivolt; Initial value: -58.0
        double var_chaste_interface__I_Shkr__OShkr = NV_Ith_S(rY, 6);
        // Units: dimensionless; Initial value: 0.0
        
        const double var_I_b__I_b_converted = 0.001 * HeartConfig::Instance()->GetCapacitance() * NV_Ith_S(mParameters, 5) * var_chaste_interface__membrane__Vm / NV_Ith_S(mParameters, 2); // uA_per_cm2
        const double var_I_Kir__EK = 0.086113989637305696 * NV_Ith_S(mParameters, 6) * log(NV_Ith_S(mParameters, 1) / NV_Ith_S(mParameters, 0)); // millivolt
        const double var_I_Kir__I_Kir_converted = 3.1622776601683795e-5 * sqrt(NV_Ith_S(mParameters, 1)) * (-var_I_Kir__EK + var_chaste_interface__membrane__Vm) * HeartConfig::Instance()->GetCapacitance() * NV_Ith_S(mParameters, 4) / ((0.93999999999999995 + exp(14.631768953068592 * (-var_I_Kir__EK + var_chaste_interface__membrane__Vm) / NV_Ith_S(mParameters, 6))) * NV_Ith_S(mParameters, 2)); // uA_per_cm2
        const double var_I_Shkr__I_Shkr_converted = 1120.6077015643802 * (-NV_Ith_S(mParameters, 1) * exp(-11.612515042117931 * var_chaste_interface__membrane__Vm / NV_Ith_S(mParameters, 6)) + NV_Ith_S(mParameters, 0)) * HeartConfig::Instance()->GetCapacitance() * var_chaste_interface__I_Shkr__OShkr * NV_Ith_S(mParameters, 3) * var_chaste_interface__membrane__Vm / ((1.0 - exp(-11.612515042117931 * var_chaste_interface__membrane__Vm / NV_Ith_S(mParameters, 6))) * NV_Ith_S(mParameters, 2) * NV_Ith_S(mParameters, 6)); // uA_per_cm2
        const double var_chaste_interface__i_ionic = var_I_Kir__I_Kir_converted + var_I_Shkr__I_Shkr_converted + var_I_b__I_b_converted; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        if (made_new_cvode_vector)
        {
            DeleteVector(rY);
        }
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt::EvaluateYDerivatives(double var_chaste_interface__environment__time_converted, const N_Vector rY, N_Vector rDY)
    {
        // Inputs:
        // Time units: millisecond
        double var_chaste_interface__membrane__Vm = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, 0));
        // Units: millivolt; Initial value: -58.0
        double var_chaste_interface__I_Shkr__C0Shkr = NV_Ith_S(rY, 1);
        // Units: dimensionless; Initial value: 0.911
        double var_chaste_interface__I_Shkr__C1Shkr = NV_Ith_S(rY, 2);
        // Units: dimensionless; Initial value: 0.0857
        double var_chaste_interface__I_Shkr__C2Shkr = NV_Ith_S(rY, 3);
        // Units: dimensionless; Initial value: 0.00302
        double var_chaste_interface__I_Shkr__C3Shkr = NV_Ith_S(rY, 4);
        // Units: dimensionless; Initial value: 4.74e-05
        double var_chaste_interface__I_Shkr__C4Shkr = NV_Ith_S(rY, 5);
        // Units: dimensionless; Initial value: 2.79e-07
        double var_chaste_interface__I_Shkr__OShkr = NV_Ith_S(rY, 6);
        // Units: dimensionless; Initial value: 0.0

        // Mathematics
        double d_dt_chaste_interface_var_membrane__Vm;
        const double d_dt_chaste_interface_var_I_Shkr__OShkr = 0.076999999999999999 * var_chaste_interface__I_Shkr__C4Shkr - 0.017999999999999999 * var_chaste_interface__I_Shkr__OShkr; // 1 / millisecond
        const double var_I_Shkr__k_v = 2.0 * exp(-17.767148014440433 * var_chaste_interface__membrane__Vm / NV_Ith_S(mParameters, 6)); // first_order_rate_constant
        const double var_I_Shkr__kv = 30.0 * exp(14.864019253910952 * var_chaste_interface__membrane__Vm / NV_Ith_S(mParameters, 6)); // first_order_rate_constant
        const double d_dt_chaste_interface_var_I_Shkr__C0Shkr = 0.001 * var_chaste_interface__I_Shkr__C1Shkr * var_I_Shkr__k_v - 0.0040000000000000001 * var_chaste_interface__I_Shkr__C0Shkr * var_I_Shkr__kv; // 1 / millisecond
        const double d_dt_chaste_interface_var_I_Shkr__C1Shkr = 0.002 * var_chaste_interface__I_Shkr__C2Shkr * var_I_Shkr__k_v + 0.0040000000000000001 * var_chaste_interface__I_Shkr__C0Shkr * var_I_Shkr__kv - 0.001 * (3.0 * var_I_Shkr__kv + var_I_Shkr__k_v) * var_chaste_interface__I_Shkr__C1Shkr; // 1 / millisecond
        const double d_dt_chaste_interface_var_I_Shkr__C2Shkr = 0.0030000000000000001 * var_chaste_interface__I_Shkr__C1Shkr * var_I_Shkr__kv + 0.0030000000000000001 * var_chaste_interface__I_Shkr__C3Shkr * var_I_Shkr__k_v - 0.001 * (2.0 * var_I_Shkr__k_v + 2.0 * var_I_Shkr__kv) * var_chaste_interface__I_Shkr__C2Shkr; // 1 / millisecond
        const double d_dt_chaste_interface_var_I_Shkr__C3Shkr = 0.002 * var_chaste_interface__I_Shkr__C2Shkr * var_I_Shkr__kv + 0.0040000000000000001 * var_chaste_interface__I_Shkr__C4Shkr * var_I_Shkr__k_v - 0.001 * (3.0 * var_I_Shkr__k_v + var_I_Shkr__kv) * var_chaste_interface__I_Shkr__C3Shkr; // 1 / millisecond
        const double d_dt_chaste_interface_var_I_Shkr__C4Shkr = 0.017999999999999999 * var_chaste_interface__I_Shkr__OShkr + 0.001 * var_chaste_interface__I_Shkr__C3Shkr * var_I_Shkr__kv - 0.001 * (77.0 + 4.0 * var_I_Shkr__k_v) * var_chaste_interface__I_Shkr__C4Shkr; // 1 / millisecond

        if (mSetVoltageDerivativeToZero)
        {
            d_dt_chaste_interface_var_membrane__Vm = 0.0;
        }
        else
        {
            const double var_I_Kir__EK = 0.086113989637305696 * NV_Ith_S(mParameters, 6) * log(NV_Ith_S(mParameters, 1) / NV_Ith_S(mParameters, 0)); // millivolt
            d_dt_chaste_interface_var_membrane__Vm = 0.001 * (-NV_Ith_S(mParameters, 5) * var_chaste_interface__membrane__Vm - 1000.0 * GetIntracellularAreaStimulus(var_chaste_interface__environment__time_converted) * NV_Ith_S(mParameters, 2) / HeartConfig::Instance()->GetCapacitance() - 0.031622776601683791 * sqrt(NV_Ith_S(mParameters, 1)) * (-var_I_Kir__EK + var_chaste_interface__membrane__Vm) * NV_Ith_S(mParameters, 4) / (0.93999999999999995 + exp(14.631768953068592 * (-var_I_Kir__EK + var_chaste_interface__membrane__Vm) / NV_Ith_S(mParameters, 6))) - 1120607.7015643802 * (-NV_Ith_S(mParameters, 1) * exp(-11.612515042117931 * var_chaste_interface__membrane__Vm / NV_Ith_S(mParameters, 6)) + NV_Ith_S(mParameters, 0)) * var_chaste_interface__I_Shkr__OShkr * NV_Ith_S(mParameters, 3) * var_chaste_interface__membrane__Vm / ((1.0 - exp(-11.612515042117931 * var_chaste_interface__membrane__Vm / NV_Ith_S(mParameters, 6))) * NV_Ith_S(mParameters, 6))) / NV_Ith_S(mParameters, 2); // millivolt / millisecond
        }
        
        NV_Ith_S(rDY,0) = d_dt_chaste_interface_var_membrane__Vm;
        NV_Ith_S(rDY,1) = d_dt_chaste_interface_var_I_Shkr__C0Shkr;
        NV_Ith_S(rDY,2) = d_dt_chaste_interface_var_I_Shkr__C1Shkr;
        NV_Ith_S(rDY,3) = d_dt_chaste_interface_var_I_Shkr__C2Shkr;
        NV_Ith_S(rDY,4) = d_dt_chaste_interface_var_I_Shkr__C3Shkr;
        NV_Ith_S(rDY,5) = d_dt_chaste_interface_var_I_Shkr__C4Shkr;
        NV_Ith_S(rDY,6) = d_dt_chaste_interface_var_I_Shkr__OShkr;
    }

    void Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt::EvaluateAnalyticJacobian(double var_chaste_interface__environment__time_converted, N_Vector rY, N_Vector rDY, CHASTE_CVODE_DENSE_MATRIX rJacobian, N_Vector rTmp1, N_Vector rTmp2, N_Vector rTmp3)
    {
        double var_chaste_interface__membrane__Vm = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, 0));
        // Units: millivolt; Initial value: -58.0
        double var_chaste_interface__I_Shkr__C0Shkr = NV_Ith_S(rY, 1);
        // Units: dimensionless; Initial value: 0.911
        double var_chaste_interface__I_Shkr__C1Shkr = NV_Ith_S(rY, 2);
        // Units: dimensionless; Initial value: 0.0857
        double var_chaste_interface__I_Shkr__C2Shkr = NV_Ith_S(rY, 3);
        // Units: dimensionless; Initial value: 0.00302
        double var_chaste_interface__I_Shkr__C3Shkr = NV_Ith_S(rY, 4);
        // Units: dimensionless; Initial value: 4.74e-05
        double var_chaste_interface__I_Shkr__C4Shkr = NV_Ith_S(rY, 5);
        // Units: dimensionless; Initial value: 2.79e-07
        double var_chaste_interface__I_Shkr__OShkr = NV_Ith_S(rY, 6);
        // Units: dimensionless; Initial value: 0.0
        const double var_x0 = 1 / NV_Ith_S(mParameters, 2);
        const double var_x1 = 1 / NV_Ith_S(mParameters, 6);
        const double var_x2 = var_x1 * (-0.086113989637305696 * NV_Ith_S(mParameters, 6) * log(NV_Ith_S(mParameters, 1) / NV_Ith_S(mParameters, 0)) + var_chaste_interface__membrane__Vm);
        const double var_x3 = exp(14.631768953068592 * var_x2);
        const double var_x4 = 0.93999999999999995 + var_x3;
        const double var_x5 = sqrt(NV_Ith_S(mParameters, 1)) * NV_Ith_S(mParameters, 4);
        const double var_x6 = var_x1 * var_chaste_interface__membrane__Vm;
        const double var_x7 = exp(-11.612515042117931 * var_x6);
        const double var_x8 = 1.0 - var_x7;
        const double var_x9 = 1 / var_x8;
        const double var_x10 = var_x7 * NV_Ith_S(mParameters, 1);
        const double var_x11 = -var_x10 + NV_Ith_S(mParameters, 0);
        const double var_x12 = var_x11 * var_x9 * NV_Ith_S(mParameters, 3);
        const double var_x13 = 13013073.790729566 * var_chaste_interface__I_Shkr__OShkr * NV_Ith_S(mParameters, 3) * var_chaste_interface__membrane__Vm / pow(NV_Ith_S(mParameters, 6), 2);
        const double var_x14 = exp(-17.767148014440433 * var_x6);
        const double var_x15 = var_x1 * var_x14;
        const double var_x16 = 0.03553429602888087 * var_x15;
        const double var_x17 = exp(14.864019253910952 * var_x6);
        const double var_x18 = var_x1 * var_x17;
        const double var_x19 = 1.783682310469314 * var_x18 * var_chaste_interface__I_Shkr__C0Shkr;
        const double var_x20 = 0.12 * var_x17;
        const double var_x21 = 0.002 * var_x14;
        const double var_x22 = 0.07106859205776174 * var_x15;
        const double var_x23 = 0.089999999999999997 * var_x17;
        const double var_x24 = 0.0040000000000000001 * var_x14;
        const double var_x25 = 0.89184115523465701 * var_x18;
        const double var_x26 = 0.059999999999999998 * var_x17;
        const double var_x27 = 0.0060000000000000001 * var_x14;
        const double var_x28 = 0.44592057761732851 * var_x18;
        const double var_x29 = 0.14213718411552348 * var_x15 * var_chaste_interface__I_Shkr__C4Shkr;
        const double var_x30 = 0.029999999999999999 * var_x17;
        const double var_x31 = 0.0080000000000000002 * var_x14;
        
        // Matrix entries
        IJth(rJacobian, 0, 0) = mSetVoltageDerivativeToZero ? 0.0 : (0.001 * var_x0 * (-NV_Ith_S(mParameters, 5) - 0.031622776601683791 * var_x5 / var_x4 - var_x10 * var_x13 * var_x9 - 1120607.7015643802 * var_x1 * var_x12 * var_chaste_interface__I_Shkr__OShkr + var_x11 * var_x13 * var_x7 / pow(var_x8, 2) + 0.46269716089034085 * var_x2 * var_x3 * var_x5 / pow(var_x4, 2)));
        IJth(rJacobian, 1, 0) = -var_x19 - var_x16 * var_chaste_interface__I_Shkr__C1Shkr;
        IJth(rJacobian, 2, 0) = var_x19 + (var_x16 - 1.3377617328519855 * var_x18) * var_chaste_interface__I_Shkr__C1Shkr - var_x22 * var_chaste_interface__I_Shkr__C2Shkr;
        IJth(rJacobian, 3, 0) = (var_x22 - var_x25) * var_chaste_interface__I_Shkr__C2Shkr + 1.3377617328519855 * var_x18 * var_chaste_interface__I_Shkr__C1Shkr - 0.1066028880866426 * var_x15 * var_chaste_interface__I_Shkr__C3Shkr;
        IJth(rJacobian, 4, 0) = -var_x29 + var_x25 * var_chaste_interface__I_Shkr__C2Shkr + (-var_x28 + 0.1066028880866426 * var_x15) * var_chaste_interface__I_Shkr__C3Shkr;
        IJth(rJacobian, 5, 0) = var_x29 + var_x28 * var_chaste_interface__I_Shkr__C3Shkr;
        IJth(rJacobian, 1, 1) = -var_x20;
        IJth(rJacobian, 2, 1) = var_x20;
        IJth(rJacobian, 1, 2) = var_x21;
        IJth(rJacobian, 2, 2) = -var_x21 - var_x23;
        IJth(rJacobian, 3, 2) = var_x23;
        IJth(rJacobian, 2, 3) = var_x24;
        IJth(rJacobian, 3, 3) = -var_x24 - var_x26;
        IJth(rJacobian, 4, 3) = var_x26;
        IJth(rJacobian, 3, 4) = var_x27;
        IJth(rJacobian, 4, 4) = -var_x27 - var_x30;
        IJth(rJacobian, 5, 4) = var_x30;
        IJth(rJacobian, 4, 5) = var_x31;
        IJth(rJacobian, 5, 5) = -0.076999999999999999 - var_x31;
        IJth(rJacobian, 6, 5) = 0.076999999999999999;
        IJth(rJacobian, 0, 6) = mSetVoltageDerivativeToZero ? 0.0 : (-1120.6077015643802 * var_x0 * var_x12 * var_x6);
        IJth(rJacobian, 5, 6) = 0.017999999999999999;
        IJth(rJacobian, 6, 6) = -0.017999999999999999;
    }

    N_Vector Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt::ComputeDerivedQuantities(double var_chaste_interface__environment__time_converted, const N_Vector & rY)
    {
        // Inputs:
        // Time units: millisecond
        double var_chaste_interface__membrane__Vm = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, 0));
        // Units: millivolt; Initial value: -58.0
        double var_chaste_interface__I_Shkr__OShkr = NV_Ith_S(rY, 6);
        // Units: dimensionless; Initial value: 0.0
        
        // Mathematics
        const double var_I_Kir__aKir = 0.93999999999999995; // dimensionless
        const double var_I_Kir__bKir = 1.26; // dimensionless
        const double var_I_b__Eb = 0; // millivolt
        const double var_I_stim__I_stim_converted = -GetIntracellularAreaStimulus(var_chaste_interface__environment__time_converted); // uA_per_cm2
        const double var_I_b__I_b = (-var_I_b__Eb + var_chaste_interface__membrane__Vm) * NV_Ith_S(mParameters, 5); // nanoampere
        const double var_I_b__I_b_converted = 0.001 * HeartConfig::Instance()->GetCapacitance() * var_I_b__I_b / NV_Ith_S(mParameters, 2); // uA_per_cm2
        const double var_model_parameters__F = 96500.0; // coulomb_per_mole
        const double var_model_parameters__R = 8310.0; // millijoule_per_kelvin_mole
        const double var_I_Kir__EK = var_model_parameters__R * NV_Ith_S(mParameters, 6) * log(NV_Ith_S(mParameters, 1) / NV_Ith_S(mParameters, 0)) / var_model_parameters__F; // millivolt
        const double var_I_Kir__OKir = 1 / (var_I_Kir__aKir + exp((-var_I_Kir__EK + var_chaste_interface__membrane__Vm) * var_I_Kir__bKir * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 6)))); // dimensionless
        const double var_I_Kir__I_Kir = 0.031622776601683791 * sqrt(NV_Ith_S(mParameters, 1)) * (-var_I_Kir__EK + var_chaste_interface__membrane__Vm) * NV_Ith_S(mParameters, 4) * var_I_Kir__OKir; // nanoampere
        const double var_I_Kir__I_Kir_converted = 0.001 * HeartConfig::Instance()->GetCapacitance() * var_I_Kir__I_Kir / NV_Ith_S(mParameters, 2); // uA_per_cm2
        const double var_I_Shkr__I_Shkr = pow(var_model_parameters__F, 2) * (-NV_Ith_S(mParameters, 1) * exp(-var_chaste_interface__membrane__Vm * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 6))) + NV_Ith_S(mParameters, 0)) * var_chaste_interface__I_Shkr__OShkr * NV_Ith_S(mParameters, 3) * var_chaste_interface__membrane__Vm / ((1.0 - exp(-var_chaste_interface__membrane__Vm * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 6)))) * var_model_parameters__R * NV_Ith_S(mParameters, 6)); // nanoampere
        const double var_I_Shkr__I_Shkr_converted = 0.001 * HeartConfig::Instance()->GetCapacitance() * var_I_Shkr__I_Shkr / NV_Ith_S(mParameters, 2); // uA_per_cm2

        N_Vector dqs = N_VNew_Serial(5);
        NV_Ith_S(dqs, 0) = var_I_Shkr__I_Shkr_converted;
        NV_Ith_S(dqs, 1) = var_I_Kir__I_Kir_converted;
        NV_Ith_S(dqs, 2) = var_I_b__I_b_converted;
        NV_Ith_S(dqs, 3) = var_I_stim__I_stim_converted;
        NV_Ith_S(dqs, 4) = var_chaste_interface__environment__time_converted;
        return dqs;
    }

template<>
void OdeSystemInformation<Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt>::Initialise(void)
{
    this->mSystemName = "sachse_model_2007";
    this->mFreeVariableName = "time";
    this->mFreeVariableUnits = "millisecond";

    // NV_Ith_S(rY, 0):
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("millivolt");
    this->mInitialConditions.push_back(-58.0);

    // NV_Ith_S(rY, 1):
    this->mVariableNames.push_back("I_Shkr__C0Shkr");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.911);

    // NV_Ith_S(rY, 2):
    this->mVariableNames.push_back("I_Shkr__C1Shkr");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0857);

    // NV_Ith_S(rY, 3):
    this->mVariableNames.push_back("I_Shkr__C2Shkr");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.00302);

    // NV_Ith_S(rY, 4):
    this->mVariableNames.push_back("I_Shkr__C3Shkr");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(4.74e-05);

    // NV_Ith_S(rY, 5):
    this->mVariableNames.push_back("I_Shkr__C4Shkr");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(2.79e-07);

    // NV_Ith_S(rY, 6):
    this->mVariableNames.push_back("I_Shkr__OShkr");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0);

    // mParameters[0]:
    this->mParameterNames.push_back("cytosolic_potassium_concentration");
    this->mParameterUnits.push_back("millimolar");

    // mParameters[1]:
    this->mParameterNames.push_back("extracellular_potassium_concentration");
    this->mParameterUnits.push_back("millimolar");

    // mParameters[2]:
    this->mParameterNames.push_back("membrane_capacitance");
    this->mParameterUnits.push_back("microfarad");

    // mParameters[3]:
    this->mParameterNames.push_back("membrane_delayed_rectifier_potassium_current_conductance");
    this->mParameterUnits.push_back("microlitre_per_second");

    // mParameters[4]:
    this->mParameterNames.push_back("membrane_inward_rectifier_potassium_current_conductance");
    this->mParameterUnits.push_back("microsiemens");

    // mParameters[5]:
    this->mParameterNames.push_back("membrane_leakage_current_conductance");
    this->mParameterUnits.push_back("microsiemens");

    // mParameters[6]:
    this->mParameterNames.push_back("temperature");
    this->mParameterUnits.push_back("kelvin");

    // Derived Quantity index [0]:
    this->mDerivedQuantityNames.push_back("membrane_delayed_rectifier_potassium_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [1]:
    this->mDerivedQuantityNames.push_back("membrane_inward_rectifier_potassium_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [2]:
    this->mDerivedQuantityNames.push_back("membrane_leakage_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [3]:
    this->mDerivedQuantityNames.push_back("membrane_stimulus_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [4]:
    this->mDerivedQuantityNames.push_back("time");
    this->mDerivedQuantityUnits.push_back("millisecond");

    this->mInitialised = true;
}

// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeOpt)

#endif // CHASTE_CVODE
