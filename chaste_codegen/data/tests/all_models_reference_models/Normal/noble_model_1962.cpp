//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: noble_model_1962
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: Normal)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "noble_model_1962.hpp"
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



    Cellnoble_model_1962FromCellML::Cellnoble_model_1962FromCellML(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractCardiacCell(
                pSolver,
                4,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        //
        this->mpSystemInfo = OdeSystemInformation<Cellnoble_model_1962FromCellML>::Instance();
        Init();
        
        this->mParameters[0] = 12.0; // (var_membrane__Cm) [microF_per_cm2]
        this->mParameters[1] = 1.2; // (var_potassium_channel__G_K_max) [milliS_per_cm2]
        this->mParameters[2] = 400.0; // (var_sodium_channel__g_Na_max) [milliS_per_cm2]
        this->mParameters[3] = 0; // (var_sodium_channel__perc_reduced_inact_for_IpNa) [dimensionless]
        this->mParameters[4] = 0; // (var_sodium_channel__shift_INa_inact) [millivolt]
        this->mParameters[5] = 0.014999999999999999; // (var_potassium_channel__G_K1_max) [milliS_per_cm2]
        this->mParameters[6] = 0.074999999999999997; // (var_leakage_current__g_L) [milliS_per_cm2]
    }

    Cellnoble_model_1962FromCellML::~Cellnoble_model_1962FromCellML()
    {
    }

    
    double Cellnoble_model_1962FromCellML::GetIIonic(const std::vector<double>* pStateVariables)
    {
        // For state variable interpolation (SVI) we read in interpolated state variables,
        // otherwise for ionic current interpolation (ICI) we use the state variables of this model (node).
        if (!pStateVariables) pStateVariables = &rGetStateVariables();
        const std::vector<double>& rY = *pStateVariables;
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -81.4147357
        double var_chaste_interface__sodium_channel_m_gate__m = rY[1];
        // Units: dimensionless; Initial value: 0.0438066719
        double var_chaste_interface__sodium_channel_h_gate__h = rY[2];
        // Units: dimensionless; Initial value: 0.854216896
        double var_chaste_interface__potassium_channel_n_gate__n = rY[3];
        // Units: dimensionless; Initial value: 0.593071543
        
        const double var_leakage_current__E_L = -60.0; // millivolt
        const double var_leakage_current__i_Leak = (-var_leakage_current__E_L + var_chaste_interface__membrane__V) * mParameters[6]; // microA_per_cm2
        const double var_potassium_channel__g_K1 = mParameters[5] * exp(1.5 + 0.016666666666666666 * var_chaste_interface__membrane__V) + mParameters[1] * exp(-1.8 - 0.02 * var_chaste_interface__membrane__V); // milliS_per_cm2
        const double var_potassium_channel__g_K2 = pow(var_chaste_interface__potassium_channel_n_gate__n, 4) * mParameters[1]; // milliS_per_cm2
        const double var_potassium_channel__i_K = (100.0 + var_chaste_interface__membrane__V) * (var_potassium_channel__g_K1 + var_potassium_channel__g_K2); // microA_per_cm2
        const double var_sodium_channel__E_Na = 40.0; // millivolt
        const double var_sodium_channel__g_Na = pow(var_chaste_interface__sodium_channel_m_gate__m, 3) * mParameters[2] * var_chaste_interface__sodium_channel_h_gate__h; // milliS_per_cm2
        const double var_sodium_channel__i_Na = (0.14000000000000001 + var_sodium_channel__g_Na) * (-var_sodium_channel__E_Na + var_chaste_interface__membrane__V); // microA_per_cm2
        const double var_chaste_interface__i_ionic = var_leakage_current__i_Leak + var_potassium_channel__i_K + var_sodium_channel__i_Na; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellnoble_model_1962FromCellML::EvaluateYDerivatives(double var_chaste_interface__environment__time, const std::vector<double>& rY, std::vector<double>& rDY)
    {
        // Inputs:
        // Time units: millisecond
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -81.4147357
        double var_chaste_interface__sodium_channel_m_gate__m = rY[1];
        // Units: dimensionless; Initial value: 0.0438066719
        double var_chaste_interface__sodium_channel_h_gate__h = rY[2];
        // Units: dimensionless; Initial value: 0.854216896
        double var_chaste_interface__potassium_channel_n_gate__n = rY[3];
        // Units: dimensionless; Initial value: 0.593071543

        // Mathematics
        double d_dt_chaste_interface_var_membrane__V;
        const double var_potassium_channel_n_gate__alpha_n = 0.0001 * (-50.0 - var_chaste_interface__membrane__V) / (-1.0 + exp(-5.0 - 0.10000000000000001 * var_chaste_interface__membrane__V)); // per_millisecond
        const double var_potassium_channel_n_gate__beta_n = 0.002 * exp(-1.125 - 0.012500000000000001 * var_chaste_interface__membrane__V); // per_millisecond
        const double d_dt_chaste_interface_var_potassium_channel_n_gate__n = (1.0 - var_chaste_interface__potassium_channel_n_gate__n) * var_potassium_channel_n_gate__alpha_n - var_potassium_channel_n_gate__beta_n * var_chaste_interface__potassium_channel_n_gate__n; // 1 / millisecond
        const double var_sodium_channel_h_gate__alpha_h = 0.17000000000000001 * exp(-4.5 + 0.050000000000000003 * mParameters[4] - 0.050000000000000003 * var_chaste_interface__membrane__V); // per_millisecond
        const double var_sodium_channel_h_gate__beta_h = 1 / (1.0 + exp(-4.2000000000000002 + 0.10000000000000001 * mParameters[4] - 0.10000000000000001 * var_chaste_interface__membrane__V)); // per_millisecond
        const double var_sodium_channel_h_gate__h_inf = 0.01 * mParameters[3] + (1.0 - 0.01 * mParameters[3]) * var_sodium_channel_h_gate__alpha_h / (var_sodium_channel_h_gate__alpha_h + var_sodium_channel_h_gate__beta_h); // dimensionless
        const double var_sodium_channel_h_gate__tau_h = 1 / (var_sodium_channel_h_gate__alpha_h + var_sodium_channel_h_gate__beta_h); // millisecond
        const double d_dt_chaste_interface_var_sodium_channel_h_gate__h = (-var_chaste_interface__sodium_channel_h_gate__h + var_sodium_channel_h_gate__h_inf) / var_sodium_channel_h_gate__tau_h; // 1 / millisecond
        const double var_sodium_channel_m_gate__alpha_m = 0.10000000000000001 * (-48.0 - var_chaste_interface__membrane__V) / (-1.0 + exp(-3.2000000000000002 - 0.066666666666666666 * var_chaste_interface__membrane__V)); // per_millisecond
        const double var_sodium_channel_m_gate__beta_m = 0.12 * (8.0 + var_chaste_interface__membrane__V) / (-1.0 + exp(1.6000000000000001 + 0.20000000000000001 * var_chaste_interface__membrane__V)); // per_millisecond
        const double d_dt_chaste_interface_var_sodium_channel_m_gate__m = (1.0 - var_chaste_interface__sodium_channel_m_gate__m) * var_sodium_channel_m_gate__alpha_m - var_sodium_channel_m_gate__beta_m * var_chaste_interface__sodium_channel_m_gate__m; // 1 / millisecond

        if (mSetVoltageDerivativeToZero)
        {
            d_dt_chaste_interface_var_membrane__V = 0.0;
        }
        else
        {
            const double var_leakage_current__E_L = -60.0; // millivolt
            const double var_leakage_current__i_Leak = (-var_leakage_current__E_L + var_chaste_interface__membrane__V) * mParameters[6]; // microA_per_cm2
            const double var_potassium_channel__g_K1 = mParameters[5] * exp(1.5 + 0.016666666666666666 * var_chaste_interface__membrane__V) + mParameters[1] * exp(-1.8 - 0.02 * var_chaste_interface__membrane__V); // milliS_per_cm2
            const double var_potassium_channel__g_K2 = pow(var_chaste_interface__potassium_channel_n_gate__n, 4) * mParameters[1]; // milliS_per_cm2
            const double var_potassium_channel__i_K = (100.0 + var_chaste_interface__membrane__V) * (var_potassium_channel__g_K1 + var_potassium_channel__g_K2); // microA_per_cm2
            const double var_sodium_channel__E_Na = 40.0; // millivolt
            const double var_sodium_channel__g_Na = pow(var_chaste_interface__sodium_channel_m_gate__m, 3) * mParameters[2] * var_chaste_interface__sodium_channel_h_gate__h; // milliS_per_cm2
            const double var_sodium_channel__i_Na = (0.14000000000000001 + var_sodium_channel__g_Na) * (-var_sodium_channel__E_Na + var_chaste_interface__membrane__V); // microA_per_cm2
            d_dt_chaste_interface_var_membrane__V = (-var_leakage_current__i_Leak - var_potassium_channel__i_K - var_sodium_channel__i_Na) / mParameters[0]; // millivolt / millisecond
        }
        
        rDY[0] = d_dt_chaste_interface_var_membrane__V;
        rDY[1] = d_dt_chaste_interface_var_sodium_channel_m_gate__m;
        rDY[2] = d_dt_chaste_interface_var_sodium_channel_h_gate__h;
        rDY[3] = d_dt_chaste_interface_var_potassium_channel_n_gate__n;
    }

    std::vector<double> Cellnoble_model_1962FromCellML::ComputeDerivedQuantities(double var_chaste_interface__environment__time, const std::vector<double> & rY)
    {
        // Inputs:
        // Time units: millisecond
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -81.4147357
        double var_chaste_interface__sodium_channel_m_gate__m = rY[1];
        // Units: dimensionless; Initial value: 0.0438066719
        double var_chaste_interface__sodium_channel_h_gate__h = rY[2];
        // Units: dimensionless; Initial value: 0.854216896
        double var_chaste_interface__potassium_channel_n_gate__n = rY[3];
        // Units: dimensionless; Initial value: 0.593071543
        
        // Mathematics
        const double var_leakage_current__E_L = -60.0; // millivolt
        const double var_leakage_current__i_Leak = (-var_leakage_current__E_L + var_chaste_interface__membrane__V) * mParameters[6]; // microA_per_cm2
        const double var_potassium_channel__g_K1 = mParameters[5] * exp(1.5 + 0.016666666666666666 * var_chaste_interface__membrane__V) + mParameters[1] * exp(-1.8 - 0.02 * var_chaste_interface__membrane__V); // milliS_per_cm2
        const double var_potassium_channel__g_K2 = pow(var_chaste_interface__potassium_channel_n_gate__n, 4) * mParameters[1]; // milliS_per_cm2
        const double var_potassium_channel__i_K = (100.0 + var_chaste_interface__membrane__V) * (var_potassium_channel__g_K1 + var_potassium_channel__g_K2); // microA_per_cm2
        const double var_sodium_channel__E_Na = 40.0; // millivolt
        const double var_sodium_channel_h_gate__alpha_h = 0.17000000000000001 * exp(-4.5 + 0.050000000000000003 * mParameters[4] - 0.050000000000000003 * var_chaste_interface__membrane__V); // per_millisecond
        const double var_sodium_channel_h_gate__beta_h = 1 / (1.0 + exp(-4.2000000000000002 + 0.10000000000000001 * mParameters[4] - 0.10000000000000001 * var_chaste_interface__membrane__V)); // per_millisecond
        const double var_sodium_channel_h_gate__tau_h = 1 / (var_sodium_channel_h_gate__alpha_h + var_sodium_channel_h_gate__beta_h); // millisecond
        const double var_sodium_channel__g_Na = pow(var_chaste_interface__sodium_channel_m_gate__m, 3) * mParameters[2] * var_chaste_interface__sodium_channel_h_gate__h; // milliS_per_cm2
        const double var_sodium_channel__i_Na = (0.14000000000000001 + var_sodium_channel__g_Na) * (-var_sodium_channel__E_Na + var_chaste_interface__membrane__V); // microA_per_cm2

        std::vector<double> dqs(5);
        dqs[0] = var_potassium_channel__i_K;
        dqs[1] = var_sodium_channel__i_Na;
        dqs[2] = var_sodium_channel_h_gate__tau_h;
        dqs[3] = var_leakage_current__i_Leak;
        dqs[4] = var_chaste_interface__environment__time;
        return dqs;
    }

template<>
void OdeSystemInformation<Cellnoble_model_1962FromCellML>::Initialise(void)
{
    this->mSystemName = "noble_model_1962";
    this->mFreeVariableName = "time";
    this->mFreeVariableUnits = "millisecond";

    // rY[0]:
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("millivolt");
    this->mInitialConditions.push_back(-81.4147357);

    // rY[1]:
    this->mVariableNames.push_back("membrane_fast_sodium_current_m_gate");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0438066719);

    // rY[2]:
    this->mVariableNames.push_back("membrane_fast_sodium_current_h_gate");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.854216896);

    // rY[3]:
    this->mVariableNames.push_back("potassium_channel_n_gate__n");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.593071543);

    // mParameters[0]:
    this->mParameterNames.push_back("membrane_capacitance");
    this->mParameterUnits.push_back("microF_per_cm2");

    // mParameters[1]:
    this->mParameterNames.push_back("membrane_delayed_rectifier_potassium_current_conductance");
    this->mParameterUnits.push_back("milliS_per_cm2");

    // mParameters[2]:
    this->mParameterNames.push_back("membrane_fast_sodium_current_conductance");
    this->mParameterUnits.push_back("milliS_per_cm2");

    // mParameters[3]:
    this->mParameterNames.push_back("membrane_fast_sodium_current_reduced_inactivation");
    this->mParameterUnits.push_back("dimensionless");

    // mParameters[4]:
    this->mParameterNames.push_back("membrane_fast_sodium_current_shift_inactivation");
    this->mParameterUnits.push_back("millivolt");

    // mParameters[5]:
    this->mParameterNames.push_back("membrane_inward_rectifier_potassium_current_conductance");
    this->mParameterUnits.push_back("milliS_per_cm2");

    // mParameters[6]:
    this->mParameterNames.push_back("membrane_leakage_current_conductance");
    this->mParameterUnits.push_back("milliS_per_cm2");

    // Derived Quantity index [0]:
    this->mDerivedQuantityNames.push_back("membrane_delayed_rectifier_potassium_current");
    this->mDerivedQuantityUnits.push_back("microA_per_cm2");

    // Derived Quantity index [1]:
    this->mDerivedQuantityNames.push_back("membrane_fast_sodium_current");
    this->mDerivedQuantityUnits.push_back("microA_per_cm2");

    // Derived Quantity index [2]:
    this->mDerivedQuantityNames.push_back("membrane_fast_sodium_current_h_gate_tau");
    this->mDerivedQuantityUnits.push_back("millisecond");

    // Derived Quantity index [3]:
    this->mDerivedQuantityNames.push_back("membrane_leakage_current");
    this->mDerivedQuantityUnits.push_back("microA_per_cm2");

    // Derived Quantity index [4]:
    this->mDerivedQuantityNames.push_back("time");
    this->mDerivedQuantityUnits.push_back("millisecond");

    
    this->mAttributes["SuggestedCycleLength"] = 1000;
    this->mInitialised = true;
}

// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Cellnoble_model_1962FromCellML)

