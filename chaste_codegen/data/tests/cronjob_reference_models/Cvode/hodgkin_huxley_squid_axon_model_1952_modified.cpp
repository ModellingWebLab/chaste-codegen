#ifdef CHASTE_CVODE
//! @file
//!
//! This source file was generated from CellML by chaste_codegen version 0.0.1
//!
//! Model: hodgkin_huxley_squid_axon_model_1952_modified
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: normal)
//! on 2020-02-13 18:11:44
//!
//! <autogenerated>

#include "hodgkin_huxley_squid_axon_model_1952_modified.hpp"
#include <cmath>
#include <cassert>
#include <memory>
#include "Exception.hpp"
#include "OdeSystemInformation.hpp"
#include "RegularStimulus.hpp"
#include "HeartConfig.hpp"
#include "IsNan.hpp"
#include "MathsCustomFunctions.hpp"
    
    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvode::Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvode(boost::shared_ptr<AbstractIvpOdeSolver> pOdeSolver /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractCvodeCell(
                pOdeSolver,
                4,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        // 
        this->mpSystemInfo = OdeSystemInformation<Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvode>::Instance();
        Init();
        
    }

    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvode::~Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvode()
    {
    }
    
    double Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvode::GetIIonic(const std::vector<double>* pStateVariables)
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
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, 0));
        // Units: millivolt; Initial value: -75.0
        double var_chaste_interface__sodium_channel_m_gate__m = NV_Ith_S(rY, 1);
        // Units: dimensionless; Initial value: 0.05
        double var_chaste_interface__sodium_channel_h_gate__h = NV_Ith_S(rY, 2);
        // Units: dimensionless; Initial value: 0.6
        double var_chaste_interface__potassium_channel_n_gate__n = NV_Ith_S(rY, 3);
        // Units: dimensionless; Initial value: 0.325
        
        const double var_leakage_current__g_L = 0.29999999999999999; // milliS_per_cm2
        const double var_membrane__E_R = -75.0; // millivolt
        const double var_leakage_current__E_L = 10.613 + var_membrane__E_R; // millivolt
        const double var_leakage_current__i_L = (-var_leakage_current__E_L + var_chaste_interface__membrane__V) * var_leakage_current__g_L; // microA_per_cm2
        const double var_potassium_channel__E_K = -12.0 + var_membrane__E_R; // millivolt
        const double var_potassium_channel__g_K = 36.0; // milliS_per_cm2
        const double var_potassium_channel__i_K = pow(var_chaste_interface__potassium_channel_n_gate__n, 4.0) * (-var_potassium_channel__E_K + var_chaste_interface__membrane__V) * var_potassium_channel__g_K; // microA_per_cm2
        const double var_sodium_channel__E_Na = 115.0 + var_membrane__E_R; // millivolt
        const double var_sodium_channel__g_Na = 120.0; // milliS_per_cm2
        const double var_sodium_channel__i_Na = pow(var_chaste_interface__sodium_channel_m_gate__m, 3.0) * (-var_sodium_channel__E_Na + var_chaste_interface__membrane__V) * var_sodium_channel__g_Na * var_chaste_interface__sodium_channel_h_gate__h; // microA_per_cm2
        const double var_chaste_interface__i_ionic = var_leakage_current__i_L + var_potassium_channel__i_K + var_sodium_channel__i_Na; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        if (made_new_cvode_vector)
        {
            DeleteVector(rY);
        }
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvode::EvaluateYDerivatives(double var_chaste_interface__environment__time, const N_Vector rY, N_Vector rDY)
    {
        // Inputs:
        // Time units: millisecond
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, 0));
        // Units: millivolt; Initial value: -75.0
        double var_chaste_interface__sodium_channel_m_gate__m = NV_Ith_S(rY, 1);
        // Units: dimensionless; Initial value: 0.05
        double var_chaste_interface__sodium_channel_h_gate__h = NV_Ith_S(rY, 2);
        // Units: dimensionless; Initial value: 0.6
        double var_chaste_interface__potassium_channel_n_gate__n = NV_Ith_S(rY, 3);
        // Units: dimensionless; Initial value: 0.325
        
        
        // Mathematics
        double d_dt_chaste_interface_var_membrane__V;
        const double var_potassium_channel_n_gate__alpha_n = -0.01 * (65.0 + var_chaste_interface__membrane__V) / (-1.0 + exp(-6.5 - 0.10000000000000001 * var_chaste_interface__membrane__V)); // per_millisecond
        const double var_potassium_channel_n_gate__beta_n = 0.125 * exp(0.9375 + 0.012500000000000001 * var_chaste_interface__membrane__V); // per_millisecond
        const double d_dt_chaste_interface_var_potassium_channel_n_gate__n = (1.0 - var_chaste_interface__potassium_channel_n_gate__n) * var_potassium_channel_n_gate__alpha_n - var_potassium_channel_n_gate__beta_n * var_chaste_interface__potassium_channel_n_gate__n; // 1 / millisecond
        const double var_sodium_channel_h_gate__alpha_h = 0.070000000000000007 * exp(-3.75 - 0.050000000000000003 * var_chaste_interface__membrane__V); // per_millisecond
        const double var_sodium_channel_h_gate__beta_h = 1.0 / (1.0 + exp(-4.5 - 0.10000000000000001 * var_chaste_interface__membrane__V)); // per_millisecond
        const double d_dt_chaste_interface_var_sodium_channel_h_gate__h = (1.0 - var_chaste_interface__sodium_channel_h_gate__h) * var_sodium_channel_h_gate__alpha_h - var_sodium_channel_h_gate__beta_h * var_chaste_interface__sodium_channel_h_gate__h; // 1 / millisecond
        const double var_sodium_channel_m_gate__alpha_m = -0.10000000000000001 * (50.0 + var_chaste_interface__membrane__V) / (-1.0 + exp(-5.0 - 0.10000000000000001 * var_chaste_interface__membrane__V)); // per_millisecond
        const double var_sodium_channel_m_gate__beta_m = 4.0 * exp(-4.166666666666667 - 0.055555555555555552 * var_chaste_interface__membrane__V); // per_millisecond
        const double d_dt_chaste_interface_var_sodium_channel_m_gate__m = (1.0 - var_chaste_interface__sodium_channel_m_gate__m) * var_sodium_channel_m_gate__alpha_m - var_sodium_channel_m_gate__beta_m * var_chaste_interface__sodium_channel_m_gate__m; // 1 / millisecond

        if (mSetVoltageDerivativeToZero)
        {
            d_dt_chaste_interface_var_membrane__V = 0.0;
        }
        else
        {
            const double var_leakage_current__g_L = 0.29999999999999999; // milliS_per_cm2
            const double var_membrane__Cm = 1.0; // microF_per_cm2
            const double var_membrane__E_R = -75.0; // millivolt
            const double var_leakage_current__E_L = 10.613 + var_membrane__E_R; // millivolt
            const double var_leakage_current__i_L = (-var_leakage_current__E_L + var_chaste_interface__membrane__V) * var_leakage_current__g_L; // microA_per_cm2
            const double var_membrane__i_Stim_converter = GetIntracellularAreaStimulus(var_chaste_interface__environment__time); // uA_per_cm2
            const double var_membrane__i_Stim = var_membrane__i_Stim_converter; // microA_per_cm2
            const double var_potassium_channel__E_K = -12.0 + var_membrane__E_R; // millivolt
            const double var_potassium_channel__g_K = 36.0; // milliS_per_cm2
            const double var_potassium_channel__i_K = pow(var_chaste_interface__potassium_channel_n_gate__n, 4.0) * (-var_potassium_channel__E_K + var_chaste_interface__membrane__V) * var_potassium_channel__g_K; // microA_per_cm2
            const double var_sodium_channel__E_Na = 115.0 + var_membrane__E_R; // millivolt
            const double var_sodium_channel__g_Na = 120.0; // milliS_per_cm2
            const double var_sodium_channel__i_Na = pow(var_chaste_interface__sodium_channel_m_gate__m, 3.0) * (-var_sodium_channel__E_Na + var_chaste_interface__membrane__V) * var_sodium_channel__g_Na * var_chaste_interface__sodium_channel_h_gate__h; // microA_per_cm2
            d_dt_chaste_interface_var_membrane__V = (-var_leakage_current__i_L - var_membrane__i_Stim - var_potassium_channel__i_K - var_sodium_channel__i_Na) / var_membrane__Cm; // millivolt / millisecond
        }
        
        NV_Ith_S(rDY,0) = d_dt_chaste_interface_var_membrane__V;
        NV_Ith_S(rDY,1) = d_dt_chaste_interface_var_sodium_channel_m_gate__m;
        NV_Ith_S(rDY,2) = d_dt_chaste_interface_var_sodium_channel_h_gate__h;
        NV_Ith_S(rDY,3) = d_dt_chaste_interface_var_potassium_channel_n_gate__n;
    }

template<>
void OdeSystemInformation<Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvode>::Initialise(void)
{
    this->mSystemName = "hodgkin_huxley_squid_axon_model_1952_modified";
    this->mFreeVariableName = "time";
    this->mFreeVariableUnits = "millisecond";

    // NV_Ith_S(rY,0):
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("millivolt");
    this->mInitialConditions.push_back(-75.0);

    // NV_Ith_S(rY,1):
    this->mVariableNames.push_back("sodium_channel_m_gate__m");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.05);

    // NV_Ith_S(rY,2):
    this->mVariableNames.push_back("sodium_channel_h_gate__h");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.6);

    // NV_Ith_S(rY,3):
    this->mVariableNames.push_back("potassium_channel_n_gate__n");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.325);

    this->mInitialised = true;
}


// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvode)
#endif // CHASTE_CVODE
