#ifdef CHASTE_CVODE
//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: sachse_model_2007
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: CvodeCellWithDataClamp)
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


    boost::shared_ptr<RegularStimulus> Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeDataClamp::UseCellMLDefaultStimulus()
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

    Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeDataClamp::Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeDataClamp(boost::shared_ptr<AbstractIvpOdeSolver> pOdeSolver /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractCvodeCellWithDataClamp(
                pOdeSolver,
                7,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        //
        this->mpSystemInfo = OdeSystemInformation<Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeDataClamp>::Instance();
        Init();

        // We have a default stimulus specified in the CellML file metadata
        this->mHasDefaultStimulusFromCellML = true;
        
        NV_Ith_S(this->mParameters, 0) = 140.0; // (var_model_parameters__Ki) [millimolar]
        NV_Ith_S(this->mParameters, 1) = 5.0; // (var_model_parameters__Ko) [millimolar]
        NV_Ith_S(this->mParameters, 2) = 4.5000000000000001e-6; // (var_membrane__Cm) [microfarad]
        NV_Ith_S(this->mParameters, 3) = 0.0; // (var_membrane_data_clamp_current_conductance) [dimensionless]
        NV_Ith_S(this->mParameters, 4) = 5.4000000000000004e-9; // (var_I_Shkr__PShkr) [microlitre_per_second]
        NV_Ith_S(this->mParameters, 5) = 0.001; // (var_I_Kir__GKir) [microsiemens]
        NV_Ith_S(this->mParameters, 6) = 6.9e-6; // (var_I_b__Gb) [microsiemens]
        NV_Ith_S(this->mParameters, 7) = 295.0; // (var_model_parameters__T) [kelvin]
    }

    Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeDataClamp::~Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeDataClamp()
    {
    }

    
    double Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeDataClamp::GetIIonic(const std::vector<double>* pStateVariables)
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
        
        const double var_I_Kir__aKir = 0.93999999999999995; // dimensionless
        const double var_I_Kir__bKir = 1.26; // dimensionless
        const double var_I_b__Eb = 0; // millivolt
        const double var_I_b__I_b = (-var_I_b__Eb + var_chaste_interface__membrane__Vm) * NV_Ith_S(mParameters, 6); // nanoampere
        const double var_I_b__I_b_converted = 0.001 * HeartConfig::Instance()->GetCapacitance() * var_I_b__I_b / NV_Ith_S(mParameters, 2); // uA_per_cm2
        const double var_model_parameters__F = 96500.0; // coulomb_per_mole
        const double var_model_parameters__R = 8310.0; // millijoule_per_kelvin_mole
        const double var_I_Kir__EK = var_model_parameters__R * NV_Ith_S(mParameters, 7) * log(NV_Ith_S(mParameters, 1) / NV_Ith_S(mParameters, 0)) / var_model_parameters__F; // millivolt
        const double var_I_Kir__OKir = 1 / (var_I_Kir__aKir + exp((-var_I_Kir__EK + var_chaste_interface__membrane__Vm) * var_I_Kir__bKir * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 7)))); // dimensionless
        const double var_I_Kir__I_Kir = 0.031622776601683791 * sqrt(NV_Ith_S(mParameters, 1)) * (-var_I_Kir__EK + var_chaste_interface__membrane__Vm) * NV_Ith_S(mParameters, 5) * var_I_Kir__OKir; // nanoampere
        const double var_I_Kir__I_Kir_converted = 0.001 * HeartConfig::Instance()->GetCapacitance() * var_I_Kir__I_Kir / NV_Ith_S(mParameters, 2); // uA_per_cm2
        const double var_I_Shkr__I_Shkr = pow(var_model_parameters__F, 2) * (-NV_Ith_S(mParameters, 1) * exp(-var_chaste_interface__membrane__Vm * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 7))) + NV_Ith_S(mParameters, 0)) * var_chaste_interface__I_Shkr__OShkr * NV_Ith_S(mParameters, 4) * var_chaste_interface__membrane__Vm / ((1.0 - exp(-var_chaste_interface__membrane__Vm * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 7)))) * var_model_parameters__R * NV_Ith_S(mParameters, 7)); // nanoampere
        const double var_I_Shkr__I_Shkr_converted = 0.001 * HeartConfig::Instance()->GetCapacitance() * var_I_Shkr__I_Shkr / NV_Ith_S(mParameters, 2); // uA_per_cm2
        const double var_chaste_interface__i_ionic = var_I_Kir__I_Kir_converted + var_I_Shkr__I_Shkr_converted + var_I_b__I_b_converted; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        if (made_new_cvode_vector)
        {
            DeleteVector(rY);
        }
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeDataClamp::EvaluateYDerivatives(double var_chaste_interface__environment__time_converted, const N_Vector rY, N_Vector rDY)
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
        const double var_I_Shkr__k_o = 18.0; // first_order_rate_constant
        const double var_I_Shkr__k_v0 = 2.0; // first_order_rate_constant
        const double var_I_Shkr__ko = 77.0; // first_order_rate_constant
        const double var_I_Shkr__OShkr_orig_deriv = var_chaste_interface__I_Shkr__C4Shkr * var_I_Shkr__ko - var_chaste_interface__I_Shkr__OShkr * var_I_Shkr__k_o; // 1 / second
        const double d_dt_chaste_interface_var_I_Shkr__OShkr = 0.001 * var_I_Shkr__OShkr_orig_deriv; // 1 / millisecond
        const double var_I_Shkr__kv0 = 30.0; // first_order_rate_constant
        const double var_I_Shkr__z_v = -1.53; // dimensionless
        const double var_I_Shkr__zv = 1.28; // dimensionless
        const double var_model_parameters__F = 96500.0; // coulomb_per_mole
        const double var_model_parameters__R = 8310.0; // millijoule_per_kelvin_mole
        const double var_I_Shkr__k_v = var_I_Shkr__k_v0 * exp(var_I_Shkr__z_v * var_chaste_interface__membrane__Vm * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 7))); // first_order_rate_constant
        const double var_I_Shkr__kv = var_I_Shkr__kv0 * exp(var_I_Shkr__zv * var_chaste_interface__membrane__Vm * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 7))); // first_order_rate_constant
        const double var_I_Shkr__C0Shkr_orig_deriv = var_chaste_interface__I_Shkr__C1Shkr * var_I_Shkr__k_v - 4.0 * var_chaste_interface__I_Shkr__C0Shkr * var_I_Shkr__kv; // 1 / second
        const double d_dt_chaste_interface_var_I_Shkr__C0Shkr = 0.001 * var_I_Shkr__C0Shkr_orig_deriv; // 1 / millisecond
        const double var_I_Shkr__C1Shkr_orig_deriv = -(3.0 * var_I_Shkr__kv + var_I_Shkr__k_v) * var_chaste_interface__I_Shkr__C1Shkr + 2.0 * var_chaste_interface__I_Shkr__C2Shkr * var_I_Shkr__k_v + 4.0 * var_chaste_interface__I_Shkr__C0Shkr * var_I_Shkr__kv; // 1 / second
        const double d_dt_chaste_interface_var_I_Shkr__C1Shkr = 0.001 * var_I_Shkr__C1Shkr_orig_deriv; // 1 / millisecond
        const double var_I_Shkr__C2Shkr_orig_deriv = -(2.0 * var_I_Shkr__k_v + 2.0 * var_I_Shkr__kv) * var_chaste_interface__I_Shkr__C2Shkr + 3.0 * var_chaste_interface__I_Shkr__C1Shkr * var_I_Shkr__kv + 3.0 * var_chaste_interface__I_Shkr__C3Shkr * var_I_Shkr__k_v; // 1 / second
        const double d_dt_chaste_interface_var_I_Shkr__C2Shkr = 0.001 * var_I_Shkr__C2Shkr_orig_deriv; // 1 / millisecond
        const double var_I_Shkr__C3Shkr_orig_deriv = -(3.0 * var_I_Shkr__k_v + var_I_Shkr__kv) * var_chaste_interface__I_Shkr__C3Shkr + 2.0 * var_chaste_interface__I_Shkr__C2Shkr * var_I_Shkr__kv + 4.0 * var_chaste_interface__I_Shkr__C4Shkr * var_I_Shkr__k_v; // 1 / second
        const double d_dt_chaste_interface_var_I_Shkr__C3Shkr = 0.001 * var_I_Shkr__C3Shkr_orig_deriv; // 1 / millisecond
        const double var_I_Shkr__C4Shkr_orig_deriv = var_chaste_interface__I_Shkr__C3Shkr * var_I_Shkr__kv + var_chaste_interface__I_Shkr__OShkr * var_I_Shkr__k_o - (4.0 * var_I_Shkr__k_v + var_I_Shkr__ko) * var_chaste_interface__I_Shkr__C4Shkr; // 1 / second
        const double d_dt_chaste_interface_var_I_Shkr__C4Shkr = 0.001 * var_I_Shkr__C4Shkr_orig_deriv; // 1 / millisecond

        if (mSetVoltageDerivativeToZero)
        {
            d_dt_chaste_interface_var_membrane__Vm = 0.0;
        }
        else
        {
            const double var_I_Kir__aKir = 0.93999999999999995; // dimensionless
            const double var_I_Kir__bKir = 1.26; // dimensionless
            const double var_I_b__Eb = 0; // millivolt
            const double var_I_stim__I_stim_converted = -GetIntracellularAreaStimulus(var_chaste_interface__environment__time_converted); // uA_per_cm2
            const double var_I_stim__I_stim = 1000.0 * var_I_stim__I_stim_converted * NV_Ith_S(mParameters, 2) / HeartConfig::Instance()->GetCapacitance(); // nanoampere
            const double var_I_b__I_b = (-var_I_b__Eb + var_chaste_interface__membrane__Vm) * NV_Ith_S(mParameters, 6); // nanoampere
            const double var_I_Kir__EK = var_model_parameters__R * NV_Ith_S(mParameters, 7) * log(NV_Ith_S(mParameters, 1) / NV_Ith_S(mParameters, 0)) / var_model_parameters__F; // millivolt
            const double var_I_Kir__OKir = 1 / (var_I_Kir__aKir + exp((-var_I_Kir__EK + var_chaste_interface__membrane__Vm) * var_I_Kir__bKir * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 7)))); // dimensionless
            const double var_I_Kir__I_Kir = 0.031622776601683791 * sqrt(NV_Ith_S(mParameters, 1)) * (-var_I_Kir__EK + var_chaste_interface__membrane__Vm) * NV_Ith_S(mParameters, 5) * var_I_Kir__OKir; // nanoampere
            const double var_I_Shkr__I_Shkr = pow(var_model_parameters__F, 2) * (-NV_Ith_S(mParameters, 1) * exp(-var_chaste_interface__membrane__Vm * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 7))) + NV_Ith_S(mParameters, 0)) * var_chaste_interface__I_Shkr__OShkr * NV_Ith_S(mParameters, 4) * var_chaste_interface__membrane__Vm / ((1.0 - exp(-var_chaste_interface__membrane__Vm * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 7)))) * var_model_parameters__R * NV_Ith_S(mParameters, 7)); // nanoampere
            const double var_membrane__Vm_orig_deriv = (-var_I_Kir__I_Kir - var_I_Shkr__I_Shkr - var_I_b__I_b + var_I_stim__I_stim) / NV_Ith_S(mParameters, 2); // millivolt / second
            d_dt_chaste_interface_var_membrane__Vm = 0.001 * var_membrane__Vm_orig_deriv; // millivolt / millisecond
        }
        
        NV_Ith_S(rDY,0) = d_dt_chaste_interface_var_membrane__Vm;
        NV_Ith_S(rDY,1) = d_dt_chaste_interface_var_I_Shkr__C0Shkr;
        NV_Ith_S(rDY,2) = d_dt_chaste_interface_var_I_Shkr__C1Shkr;
        NV_Ith_S(rDY,3) = d_dt_chaste_interface_var_I_Shkr__C2Shkr;
        NV_Ith_S(rDY,4) = d_dt_chaste_interface_var_I_Shkr__C3Shkr;
        NV_Ith_S(rDY,5) = d_dt_chaste_interface_var_I_Shkr__C4Shkr;
        NV_Ith_S(rDY,6) = d_dt_chaste_interface_var_I_Shkr__OShkr;
    }

    N_Vector Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeDataClamp::ComputeDerivedQuantities(double var_chaste_interface__environment__time_converted, const N_Vector & rY)
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
        const double var_I_b__I_b = (-var_I_b__Eb + var_chaste_interface__membrane__Vm) * NV_Ith_S(mParameters, 6); // nanoampere
        const double var_I_b__I_b_converted = 0.001 * HeartConfig::Instance()->GetCapacitance() * var_I_b__I_b / NV_Ith_S(mParameters, 2); // uA_per_cm2
        // Special handling of data clamp current here
        // (we want to save expense of calling the interpolation method if possible.)
        double var_chaste_interface__membrane_data_clamp_current = 0.0;
        if (mDataClampIsOn)
        {
            var_chaste_interface__membrane_data_clamp_current = (-GetExperimentalVoltageAtTimeT(var_chaste_interface__environment__time_converted) + var_chaste_interface__membrane__Vm) * NV_Ith_S(mParameters, 3); // uA_per_cm2
        }
        const double var_model_parameters__F = 96500.0; // coulomb_per_mole
        const double var_model_parameters__R = 8310.0; // millijoule_per_kelvin_mole
        const double var_I_Kir__EK = var_model_parameters__R * NV_Ith_S(mParameters, 7) * log(NV_Ith_S(mParameters, 1) / NV_Ith_S(mParameters, 0)) / var_model_parameters__F; // millivolt
        const double var_I_Kir__OKir = 1 / (var_I_Kir__aKir + exp((-var_I_Kir__EK + var_chaste_interface__membrane__Vm) * var_I_Kir__bKir * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 7)))); // dimensionless
        const double var_I_Kir__I_Kir = 0.031622776601683791 * sqrt(NV_Ith_S(mParameters, 1)) * (-var_I_Kir__EK + var_chaste_interface__membrane__Vm) * NV_Ith_S(mParameters, 5) * var_I_Kir__OKir; // nanoampere
        const double var_I_Kir__I_Kir_converted = 0.001 * HeartConfig::Instance()->GetCapacitance() * var_I_Kir__I_Kir / NV_Ith_S(mParameters, 2); // uA_per_cm2
        const double var_I_Shkr__I_Shkr = pow(var_model_parameters__F, 2) * (-NV_Ith_S(mParameters, 1) * exp(-var_chaste_interface__membrane__Vm * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 7))) + NV_Ith_S(mParameters, 0)) * var_chaste_interface__I_Shkr__OShkr * NV_Ith_S(mParameters, 4) * var_chaste_interface__membrane__Vm / ((1.0 - exp(-var_chaste_interface__membrane__Vm * var_model_parameters__F / (var_model_parameters__R * NV_Ith_S(mParameters, 7)))) * var_model_parameters__R * NV_Ith_S(mParameters, 7)); // nanoampere
        const double var_I_Shkr__I_Shkr_converted = 0.001 * HeartConfig::Instance()->GetCapacitance() * var_I_Shkr__I_Shkr / NV_Ith_S(mParameters, 2); // uA_per_cm2

        N_Vector dqs = N_VNew_Serial(6);
        NV_Ith_S(dqs, 0) = var_chaste_interface__membrane_data_clamp_current;
        NV_Ith_S(dqs, 1) = var_I_Shkr__I_Shkr_converted;
        NV_Ith_S(dqs, 2) = var_I_Kir__I_Kir_converted;
        NV_Ith_S(dqs, 3) = var_I_b__I_b_converted;
        NV_Ith_S(dqs, 4) = var_I_stim__I_stim_converted;
        NV_Ith_S(dqs, 5) = var_chaste_interface__environment__time_converted;
        return dqs;
    }

template<>
void OdeSystemInformation<Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeDataClamp>::Initialise(void)
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
    this->mParameterNames.push_back("membrane_data_clamp_current_conductance");
    this->mParameterUnits.push_back("dimensionless");

    // mParameters[4]:
    this->mParameterNames.push_back("membrane_delayed_rectifier_potassium_current_conductance");
    this->mParameterUnits.push_back("microlitre_per_second");

    // mParameters[5]:
    this->mParameterNames.push_back("membrane_inward_rectifier_potassium_current_conductance");
    this->mParameterUnits.push_back("microsiemens");

    // mParameters[6]:
    this->mParameterNames.push_back("membrane_leakage_current_conductance");
    this->mParameterUnits.push_back("microsiemens");

    // mParameters[7]:
    this->mParameterNames.push_back("temperature");
    this->mParameterUnits.push_back("kelvin");

    // Derived Quantity index [0]:
    this->mDerivedQuantityNames.push_back("membrane_data_clamp_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [1]:
    this->mDerivedQuantityNames.push_back("membrane_delayed_rectifier_potassium_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [2]:
    this->mDerivedQuantityNames.push_back("membrane_inward_rectifier_potassium_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [3]:
    this->mDerivedQuantityNames.push_back("membrane_leakage_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [4]:
    this->mDerivedQuantityNames.push_back("membrane_stimulus_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [5]:
    this->mDerivedQuantityNames.push_back("time");
    this->mDerivedQuantityUnits.push_back("millisecond");

    this->mInitialised = true;
}

// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Cellsachse_moreno_abildskov_2008_bFromCellMLCvodeDataClamp)

#endif // CHASTE_CVODE
