//! @file
//!
//! This source file was generated from CellML by chaste_codegen version 0.0.1
//!
//! Model: stewart_zhang_model_2008
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: normal)
//! on 2020-02-25 21:29:05
//!
//! <autogenerated>

#include "stewart_zhang_model_2008_ss.hpp"
#include <cmath>
#include <cassert>
#include <memory>
#include "Exception.hpp"
#include "OdeSystemInformation.hpp"
#include "RegularStimulus.hpp"
#include "HeartConfig.hpp"
#include "IsNan.hpp"
#include "MathsCustomFunctions.hpp"

    double Cellstewart_zhang_model_2008_ssFromCellML::GetIntracellularCalciumConcentration()
    {
        return mStateVariables[1];
    }

    Cellstewart_zhang_model_2008_ssFromCellML::Cellstewart_zhang_model_2008_ssFromCellML(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractCardiacCell(
                pSolver,
                20,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        //
        this->mpSystemInfo = OdeSystemInformation<Cellstewart_zhang_model_2008_ssFromCellML>::Instance();
        Init();
        
    }

    Cellstewart_zhang_model_2008_ssFromCellML::~Cellstewart_zhang_model_2008_ssFromCellML()
    {
    }

    double Cellstewart_zhang_model_2008_ssFromCellML::GetIIonic(const std::vector<double>* pStateVariables)
    {
        // For state variable interpolation (SVI) we read in interpolated state variables,
        // otherwise for ionic current interpolation (ICI) we use the state variables of this model (node).
        if (!pStateVariables) pStateVariables = &rGetStateVariables();
        const std::vector<double>& rY = *pStateVariables;
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -69.1370441635924
        double var_chaste_interface__calcium_dynamics__Ca_i = rY[1];
        // Units: millimolar; Initial value: 0.000101878186157052
        double var_chaste_interface__hyperpolarization_activated_current_y_gate__y = rY[2];
        // Units: dimensionless; Initial value: 0.0457562667986602
        double var_chaste_interface__rapid_time_dependent_potassium_current_Xr1_gate__Xr1 = rY[3];
        // Units: dimensionless; Initial value: 0.00550281999719088
        double var_chaste_interface__rapid_time_dependent_potassium_current_Xr2_gate__Xr2 = rY[4];
        // Units: dimensionless; Initial value: 0.313213286437995
        double var_chaste_interface__slow_time_dependent_potassium_current_Xs_gate__Xs = rY[5];
        // Units: dimensionless; Initial value: 0.00953708522974789
        double var_chaste_interface__fast_sodium_current_m_gate__m = rY[6];
        // Units: dimensionless; Initial value: 0.0417391656294997
        double var_chaste_interface__fast_sodium_current_h_gate__h = rY[7];
        // Units: dimensionless; Initial value: 0.190678733735145
        double var_chaste_interface__fast_sodium_current_j_gate__j = rY[8];
        // Units: dimensionless; Initial value: 0.238219836154029
        double var_chaste_interface__L_type_Ca_current_d_gate__d = rY[9];
        // Units: dimensionless; Initial value: 0.000287906256206415
        double var_chaste_interface__L_type_Ca_current_f_gate__f = rY[10];
        // Units: dimensionless; Initial value: 0.989328560287987
        double var_chaste_interface__L_type_Ca_current_f2_gate__f2 = rY[11];
        // Units: dimensionless; Initial value: 0.995474890442185
        double var_chaste_interface__L_type_Ca_current_fCass_gate__fCass = rY[12];
        // Units: dimensionless; Initial value: 0.999955429598213
        double var_chaste_interface__transient_outward_current_s_gate__s = rY[13];
        // Units: dimensionless; Initial value: 0.96386101799501
        double var_chaste_interface__transient_outward_current_r_gate__r = rY[14];
        // Units: dimensionless; Initial value: 0.00103618091196912
        double var_chaste_interface__calcium_dynamics__Ca_ss = rY[16];
        // Units: millimolar; Initial value: 0.000446818714055411
        double var_chaste_interface__sodium_dynamics__Na_i = rY[18];
        // Units: millimolar; Initial value: 8.80420286531673
        double var_chaste_interface__potassium_dynamics__K_i = rY[19];
        // Units: millimolar; Initial value: 136.781894160227
        
        const double var_calcium_pump_current__i_p_Ca = 0.12379999999999999 * var_chaste_interface__calcium_dynamics__Ca_i / (0.00050000000000000001 + var_chaste_interface__calcium_dynamics__Ca_i); // picoA_per_picoF
        const double var_L_type_Ca_current__i_CaL = 0.57500202096124498 * (-2.0 + 0.25 * var_chaste_interface__calcium_dynamics__Ca_ss * exp(-1.1230167246823641 + 0.074867781645490947 * var_chaste_interface__membrane__V)) * (-15.0 + var_chaste_interface__membrane__V) * var_chaste_interface__L_type_Ca_current_d_gate__d * var_chaste_interface__L_type_Ca_current_f2_gate__f2 * var_chaste_interface__L_type_Ca_current_fCass_gate__fCass * var_chaste_interface__L_type_Ca_current_f_gate__f / (-1.0 + exp(-1.1230167246823641 + 0.074867781645490947 * var_chaste_interface__membrane__V)); // picoA_per_picoF
        const double var_calcium_background_current__i_b_Ca = 0.00059199999999999997 * var_chaste_interface__membrane__V - 0.0079072731552699126 * log(2.0 / var_chaste_interface__calcium_dynamics__Ca_i); // picoA_per_picoF
        const double var_reversal_potentials__E_K = 26.713760659695652 * log(5.4000000000000004 / var_chaste_interface__potassium_dynamics__K_i); // millivolt
        const double var_inward_rectifier_potassium_current__i_K1 = 0.065000000000000002 * (-8.0 - var_reversal_potentials__E_K + var_chaste_interface__membrane__V) / (1.0 + exp(7.5440000000000005 + 0.10000000000000001 * var_chaste_interface__membrane__V)); // picoA_per_picoF
        const double var_potassium_pump_current__i_p_K = 0.0146 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) / (1.0 + exp(4.1806020066889626 - 0.16722408026755853 * var_chaste_interface__membrane__V)); // picoA_per_picoF
        const double var_rapid_time_dependent_potassium_current__i_Kr = 0.091800000000000007 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) * var_chaste_interface__rapid_time_dependent_potassium_current_Xr1_gate__Xr1 * var_chaste_interface__rapid_time_dependent_potassium_current_Xr2_gate__Xr2; // picoA_per_picoF
        const double var_reversal_potentials__E_Na = 26.713760659695652 * log(140.0 / var_chaste_interface__sodium_dynamics__Na_i); // millivolt
        const double var_fast_sodium_current__i_Na = 130.5744 * pow(var_chaste_interface__fast_sodium_current_m_gate__m, 3.0) * (-var_reversal_potentials__E_Na + var_chaste_interface__membrane__V) * var_chaste_interface__fast_sodium_current_h_gate__h * var_chaste_interface__fast_sodium_current_j_gate__j; // picoA_per_picoF
        const double var_hyperpolarization_activated_current__i_f = 0.0234346 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) * var_chaste_interface__hyperpolarization_activated_current_y_gate__y + 0.014565399999999999 * (-var_reversal_potentials__E_Na + var_chaste_interface__membrane__V) * var_chaste_interface__hyperpolarization_activated_current_y_gate__y; // picoA_per_picoF
        const double var_slow_time_dependent_potassium_current__i_Ks = 0.23519999999999999 * pow(var_chaste_interface__slow_time_dependent_potassium_current_Xs_gate__Xs, 2.0) * (-26.713760659695652 * log(9.6000000000000014 / (0.029999999999999999 * var_chaste_interface__sodium_dynamics__Na_i + var_chaste_interface__potassium_dynamics__K_i)) + var_chaste_interface__membrane__V); // picoA_per_picoF
        const double var_sodium_background_current__i_b_Na = 0.00029 * var_chaste_interface__membrane__V - 0.00029 * var_reversal_potentials__E_Na; // picoA_per_picoF
        const double var_sodium_calcium_exchanger_current__i_NaCa = 8.6662202299424464e-5 * (2.0 * pow(var_chaste_interface__sodium_dynamics__Na_i, 3.0) * exp(0.013101861787960915 * var_chaste_interface__membrane__V) - 6860000.0 * var_chaste_interface__calcium_dynamics__Ca_i * exp(-0.024332029034784559 * var_chaste_interface__membrane__V)) / (1.0 + 0.10000000000000001 * exp(-0.024332029034784559 * var_chaste_interface__membrane__V)); // picoA_per_picoF
        const double var_sodium_potassium_pump_current__i_NaK = 2.2983750000000001 * var_chaste_interface__sodium_dynamics__Na_i / ((40.0 + var_chaste_interface__sodium_dynamics__Na_i) * (1.0 + 0.035299999999999998 * exp(-0.037433890822745473 * var_chaste_interface__membrane__V) + 0.1245 * exp(-0.0037433890822745476 * var_chaste_interface__membrane__V))); // picoA_per_picoF
        const double var_sustained_outward_current__i_sus = 0.022700000000000001 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) / (1.0 + exp(0.29411764705882354 - 0.058823529411764705 * var_chaste_interface__membrane__V)); // picoA_per_picoF
        const double var_transient_outward_current__i_to = 0.081839999999999996 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) * var_chaste_interface__transient_outward_current_r_gate__r * var_chaste_interface__transient_outward_current_s_gate__s; // picoA_per_picoF
        const double var_chaste_interface__i_ionic = (var_L_type_Ca_current__i_CaL + var_calcium_background_current__i_b_Ca + var_calcium_pump_current__i_p_Ca + var_fast_sodium_current__i_Na + var_hyperpolarization_activated_current__i_f + var_inward_rectifier_potassium_current__i_K1 + var_potassium_pump_current__i_p_K + var_rapid_time_dependent_potassium_current__i_Kr + var_slow_time_dependent_potassium_current__i_Ks + var_sodium_background_current__i_b_Na + var_sodium_calcium_exchanger_current__i_NaCa + var_sodium_potassium_pump_current__i_NaK + var_sustained_outward_current__i_sus + var_transient_outward_current__i_to) * HeartConfig::Instance()->GetCapacitance(); // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellstewart_zhang_model_2008_ssFromCellML::EvaluateYDerivatives(double var_chaste_interface__environment__time, const std::vector<double>& rY, std::vector<double>& rDY)
    {
        // Inputs:
        // Time units: millisecond
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -69.1370441635924
        double var_chaste_interface__calcium_dynamics__Ca_i = rY[1];
        // Units: millimolar; Initial value: 0.000101878186157052
        double var_chaste_interface__hyperpolarization_activated_current_y_gate__y = rY[2];
        // Units: dimensionless; Initial value: 0.0457562667986602
        double var_chaste_interface__rapid_time_dependent_potassium_current_Xr1_gate__Xr1 = rY[3];
        // Units: dimensionless; Initial value: 0.00550281999719088
        double var_chaste_interface__rapid_time_dependent_potassium_current_Xr2_gate__Xr2 = rY[4];
        // Units: dimensionless; Initial value: 0.313213286437995
        double var_chaste_interface__slow_time_dependent_potassium_current_Xs_gate__Xs = rY[5];
        // Units: dimensionless; Initial value: 0.00953708522974789
        double var_chaste_interface__fast_sodium_current_m_gate__m = rY[6];
        // Units: dimensionless; Initial value: 0.0417391656294997
        double var_chaste_interface__fast_sodium_current_h_gate__h = rY[7];
        // Units: dimensionless; Initial value: 0.190678733735145
        double var_chaste_interface__fast_sodium_current_j_gate__j = rY[8];
        // Units: dimensionless; Initial value: 0.238219836154029
        double var_chaste_interface__L_type_Ca_current_d_gate__d = rY[9];
        // Units: dimensionless; Initial value: 0.000287906256206415
        double var_chaste_interface__L_type_Ca_current_f_gate__f = rY[10];
        // Units: dimensionless; Initial value: 0.989328560287987
        double var_chaste_interface__L_type_Ca_current_f2_gate__f2 = rY[11];
        // Units: dimensionless; Initial value: 0.995474890442185
        double var_chaste_interface__L_type_Ca_current_fCass_gate__fCass = rY[12];
        // Units: dimensionless; Initial value: 0.999955429598213
        double var_chaste_interface__transient_outward_current_s_gate__s = rY[13];
        // Units: dimensionless; Initial value: 0.96386101799501
        double var_chaste_interface__transient_outward_current_r_gate__r = rY[14];
        // Units: dimensionless; Initial value: 0.00103618091196912
        double var_chaste_interface__calcium_dynamics__Ca_SR = rY[15];
        // Units: millimolar; Initial value: 3.10836886659417
        double var_chaste_interface__calcium_dynamics__Ca_ss = rY[16];
        // Units: millimolar; Initial value: 0.000446818714055411
        double var_chaste_interface__calcium_dynamics__R_prime = rY[17];
        // Units: dimensionless; Initial value: 0.991580051907845
        double var_chaste_interface__sodium_dynamics__Na_i = rY[18];
        // Units: millimolar; Initial value: 8.80420286531673
        double var_chaste_interface__potassium_dynamics__K_i = rY[19];
        // Units: millimolar; Initial value: 136.781894160227

        // Mathematics
        double d_dt_chaste_interface_var_membrane__V;
        const double d_dt_chaste_interface_var_L_type_Ca_current_fCass_gate__fCass = (0.40000000000000002 - var_chaste_interface__L_type_Ca_current_fCass_gate__fCass + 0.59999999999999998 / (1.0 + 399.99999999999994 * pow(var_chaste_interface__calcium_dynamics__Ca_ss, 2.0))) / (2.0 + 80.0 / (1.0 + 399.99999999999994 * pow(var_chaste_interface__calcium_dynamics__Ca_ss, 2.0))); // 1 / millisecond
        const double var_calcium_dynamics__i_leak = 0.00036000000000000002 * var_chaste_interface__calcium_dynamics__Ca_SR - 0.00036000000000000002 * var_chaste_interface__calcium_dynamics__Ca_i; // millimolar_per_millisecond
        const double var_calcium_dynamics__i_up = 0.0063749999999999996 / (1.0 + 6.2499999999999997e-8 * pow(var_chaste_interface__calcium_dynamics__Ca_i, (-2.0))); // millimolar_per_millisecond
        const double var_calcium_dynamics__i_xfer = 0.0038 * var_chaste_interface__calcium_dynamics__Ca_ss - 0.0038 * var_chaste_interface__calcium_dynamics__Ca_i; // millimolar_per_millisecond
        const double var_calcium_dynamics__kcasr = 2.5 - 1.5 / (1.0 + 2.25 * pow(1 / var_chaste_interface__calcium_dynamics__Ca_SR, 2.0)); // dimensionless
        const double var_calcium_dynamics__i_rel = 0.015299999999999998 * pow(var_chaste_interface__calcium_dynamics__Ca_ss, 2.0) * (-var_chaste_interface__calcium_dynamics__Ca_ss + var_chaste_interface__calcium_dynamics__Ca_SR) * var_chaste_interface__calcium_dynamics__R_prime / ((0.059999999999999998 + 0.14999999999999999 * pow(var_chaste_interface__calcium_dynamics__Ca_ss, 2.0) / var_calcium_dynamics__kcasr) * var_calcium_dynamics__kcasr); // millimolar_per_millisecond
        const double d_dt_chaste_interface_var_calcium_dynamics__Ca_SR = 1.0 * (-var_calcium_dynamics__i_leak - var_calcium_dynamics__i_rel + var_calcium_dynamics__i_up) / (1.0 + 3.0 * pow((0.29999999999999999 + var_chaste_interface__calcium_dynamics__Ca_SR), (-2.0))); // millimolar / millisecond
        const double d_dt_chaste_interface_var_calcium_dynamics__R_prime = 0.0050000000000000001 - 0.0050000000000000001 * var_chaste_interface__calcium_dynamics__R_prime - 0.044999999999999998 * var_chaste_interface__calcium_dynamics__Ca_ss * var_chaste_interface__calcium_dynamics__R_prime * var_calcium_dynamics__kcasr; // 1 / millisecond
        const double var_calcium_pump_current__i_p_Ca = 0.12379999999999999 * var_chaste_interface__calcium_dynamics__Ca_i / (0.00050000000000000001 + var_chaste_interface__calcium_dynamics__Ca_i); // picoA_per_picoF
        const double var_L_type_Ca_current__i_CaL = 0.57500202096124498 * (-2.0 + 0.25 * var_chaste_interface__calcium_dynamics__Ca_ss * exp(-1.1230167246823641 + 0.074867781645490947 * var_chaste_interface__membrane__V)) * (-15.0 + var_chaste_interface__membrane__V) * var_chaste_interface__L_type_Ca_current_d_gate__d * var_chaste_interface__L_type_Ca_current_f2_gate__f2 * var_chaste_interface__L_type_Ca_current_fCass_gate__fCass * var_chaste_interface__L_type_Ca_current_f_gate__f / (-1.0 + exp(-1.1230167246823641 + 0.074867781645490947 * var_chaste_interface__membrane__V)); // picoA_per_picoF
        const double d_dt_chaste_interface_var_L_type_Ca_current_d_gate__d = (-var_chaste_interface__L_type_Ca_current_d_gate__d + 1.0 / (1.0 + exp(-1.0666666666666667 - 0.13333333333333333 * var_chaste_interface__membrane__V))) / (1.0 / (1.0 + exp(2.5 - 0.050000000000000003 * var_chaste_interface__membrane__V)) + 1.3999999999999999 * (0.25 + 1.3999999999999999 / (1.0 + exp(-2.6923076923076925 - 0.076923076923076927 * var_chaste_interface__membrane__V))) / (1.0 + exp(1.0 + 0.20000000000000001 * var_chaste_interface__membrane__V))); // 1 / millisecond
        const double d_dt_chaste_interface_var_L_type_Ca_current_f2_gate__f2 = (0.33000000000000002 - var_chaste_interface__L_type_Ca_current_f2_gate__f2 + 0.67000000000000004 / (1.0 + exp(5.0 + 0.14285714285714285 * var_chaste_interface__membrane__V))) / (80.0 / (1.0 + exp(3.0 + 0.10000000000000001 * var_chaste_interface__membrane__V)) + 31.0 / (1.0 + exp(2.5 - 0.10000000000000001 * var_chaste_interface__membrane__V)) + 562.0 * exp(-3.0375000000000001 * pow((1 + 0.037037037037037035 * var_chaste_interface__membrane__V), 2.0))); // 1 / millisecond
        const double d_dt_chaste_interface_var_L_type_Ca_current_f_gate__f = (-var_chaste_interface__L_type_Ca_current_f_gate__f + 1.0 / (1.0 + exp(2.8571428571428572 + 0.14285714285714285 * var_chaste_interface__membrane__V))) / (20.0 + 200.0 / (1.0 + exp(1.3 - 0.10000000000000001 * var_chaste_interface__membrane__V)) + 180.0 / (1.0 + exp(3.0 + 0.10000000000000001 * var_chaste_interface__membrane__V)) + 1102.5 * exp(-3.2400000000000002 * pow((1 + 0.037037037037037035 * var_chaste_interface__membrane__V), 2.0))); // 1 / millisecond
        const double d_dt_chaste_interface_var_fast_sodium_current_h_gate__h = ((var_chaste_interface__membrane__V < -40.0) ? ((-var_chaste_interface__fast_sodium_current_h_gate__h + 1.0 * pow((1.0 + exp(9.6298788694481825 + 0.13458950201884254 * var_chaste_interface__membrane__V)), (-2.0))) * (310000.0 * exp(0.34849999999999998 * var_chaste_interface__membrane__V) + 2.7000000000000002 * exp(0.079000000000000001 * var_chaste_interface__membrane__V) + 0.057000000000000002 * exp(-11.764705882352942 - 0.14705882352941177 * var_chaste_interface__membrane__V))) : ((-var_chaste_interface__fast_sodium_current_h_gate__h + 1.0 * pow((1.0 + exp(9.6298788694481825 + 0.13458950201884254 * var_chaste_interface__membrane__V)), (-2.0))) / (0.16883116883116883 + 0.16883116883116883 * exp(-0.96036036036036043 - 0.0900900900900901 * var_chaste_interface__membrane__V)))); // 1 / millisecond
        const double d_dt_chaste_interface_var_fast_sodium_current_j_gate__j = ((var_chaste_interface__membrane__V < -40.0) ? ((-var_chaste_interface__fast_sodium_current_j_gate__j + 1.0 * pow((1.0 + exp(9.6298788694481825 + 0.13458950201884254 * var_chaste_interface__membrane__V)), (-2.0))) * (0.024240000000000001 * exp(-0.01052 * var_chaste_interface__membrane__V) / (1.0 + exp(-5.5312920000000005 - 0.13780000000000001 * var_chaste_interface__membrane__V)) + 1.0 * (37.780000000000001 + var_chaste_interface__membrane__V) * (-25428.0 * exp(0.24440000000000001 * var_chaste_interface__membrane__V) - 6.9480000000000002e-6 * exp(-0.043909999999999998 * var_chaste_interface__membrane__V)) / (1.0 + exp(24.640530000000002 + 0.311 * var_chaste_interface__membrane__V)))) : (0.59999999999999998 * (-var_chaste_interface__fast_sodium_current_j_gate__j + 1.0 * pow((1.0 + exp(9.6298788694481825 + 0.13458950201884254 * var_chaste_interface__membrane__V)), (-2.0))) * exp(0.057000000000000002 * var_chaste_interface__membrane__V) / (1.0 + exp(-3.2000000000000002 - 0.10000000000000001 * var_chaste_interface__membrane__V)))); // 1 / millisecond
        const double d_dt_chaste_interface_var_fast_sodium_current_m_gate__m = 1.0 * (1.0 + exp(-12.0 - 0.20000000000000001 * var_chaste_interface__membrane__V)) * (-var_chaste_interface__fast_sodium_current_m_gate__m + 1.0 * pow((1.0 + exp(-6.2967884828349945 - 0.11074197120708749 * var_chaste_interface__membrane__V)), (-2.0))) / (0.10000000000000001 / (1.0 + exp(7.0 + 0.20000000000000001 * var_chaste_interface__membrane__V)) + 0.10000000000000001 / (1.0 + exp(-0.25 + 0.0050000000000000001 * var_chaste_interface__membrane__V))); // 1 / millisecond
        const double d_dt_chaste_interface_var_hyperpolarization_activated_current_y_gate__y = (-var_chaste_interface__hyperpolarization_activated_current_y_gate__y + 1.0 / (1.0 + exp(11.852941176470587 + 0.14705882352941177 * var_chaste_interface__membrane__V))) * (0.00025000000000000001 * exp(3.6000000000000001 + 0.11 * var_chaste_interface__membrane__V) + 0.00025000000000000001 * exp(-2.8999999999999999 - 0.040000000000000001 * var_chaste_interface__membrane__V)); // 1 / millisecond
        const double d_dt_chaste_interface_var_calcium_dynamics__Ca_ss = 1.0 * (20.007315288953912 * var_calcium_dynamics__i_rel - 300.0 * var_calcium_dynamics__i_xfer - 0.017532824616602913 * var_L_type_Ca_current__i_CaL) / (1.0 + 0.0001 * pow((0.00025000000000000001 + var_chaste_interface__calcium_dynamics__Ca_ss), (-2.0))); // millimolar / millisecond
        const double d_dt_chaste_interface_var_rapid_time_dependent_potassium_current_Xr1_gate__Xr1 = 0.00037037037037037035 * (1.0 + exp(2.6086956521739131 + 0.086956521739130432 * var_chaste_interface__membrane__V)) * (1.0 + exp(-4.5 - 0.10000000000000001 * var_chaste_interface__membrane__V)) * (-var_chaste_interface__rapid_time_dependent_potassium_current_Xr1_gate__Xr1 + 1.0 / (1.0 + exp(-3.7142857142857144 - 0.14285714285714285 * var_chaste_interface__membrane__V))); // 1 / millisecond
        const double d_dt_chaste_interface_var_rapid_time_dependent_potassium_current_Xr2_gate__Xr2 = 0.29761904761904762 * (1.0 + exp(-3.0 + 0.050000000000000003 * var_chaste_interface__membrane__V)) * (1.0 + exp(-3.0 - 0.050000000000000003 * var_chaste_interface__membrane__V)) * (-var_chaste_interface__rapid_time_dependent_potassium_current_Xr2_gate__Xr2 + 1.0 / (1.0 + exp(3.6666666666666665 + 0.041666666666666664 * var_chaste_interface__membrane__V))); // 1 / millisecond
        const double var_calcium_background_current__i_b_Ca = 0.00059199999999999997 * var_chaste_interface__membrane__V - 0.0079072731552699126 * log(2.0 / var_chaste_interface__calcium_dynamics__Ca_i); // picoA_per_picoF
        const double var_reversal_potentials__E_K = 26.713760659695652 * log(5.4000000000000004 / var_chaste_interface__potassium_dynamics__K_i); // millivolt
        const double var_hyperpolarization_activated_current__i_f_K = 0.0234346 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) * var_chaste_interface__hyperpolarization_activated_current_y_gate__y; // picoA_per_picoF
        const double var_inward_rectifier_potassium_current__i_K1 = 0.065000000000000002 * (-8.0 - var_reversal_potentials__E_K + var_chaste_interface__membrane__V) / (1.0 + exp(7.5440000000000005 + 0.10000000000000001 * var_chaste_interface__membrane__V)); // picoA_per_picoF
        const double var_potassium_pump_current__i_p_K = 0.0146 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) / (1.0 + exp(4.1806020066889626 - 0.16722408026755853 * var_chaste_interface__membrane__V)); // picoA_per_picoF
        const double var_rapid_time_dependent_potassium_current__i_Kr = 0.091800000000000007 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) * var_chaste_interface__rapid_time_dependent_potassium_current_Xr1_gate__Xr1 * var_chaste_interface__rapid_time_dependent_potassium_current_Xr2_gate__Xr2; // picoA_per_picoF
        const double d_dt_chaste_interface_var_slow_time_dependent_potassium_current_Xs_gate__Xs = (-var_chaste_interface__slow_time_dependent_potassium_current_Xs_gate__Xs + 1.0 / (1.0 + exp(-0.35714285714285715 - 0.071428571428571425 * var_chaste_interface__membrane__V))) / (80.0 + 1400.0 / (sqrt(1.0 + exp(0.83333333333333337 - 0.16666666666666666 * var_chaste_interface__membrane__V)) * (1.0 + exp(-2.3333333333333335 + 0.066666666666666666 * var_chaste_interface__membrane__V)))); // 1 / millisecond
        const double var_reversal_potentials__E_Na = 26.713760659695652 * log(140.0 / var_chaste_interface__sodium_dynamics__Na_i); // millivolt
        const double var_fast_sodium_current__i_Na = 130.5744 * pow(var_chaste_interface__fast_sodium_current_m_gate__m, 3.0) * (-var_reversal_potentials__E_Na + var_chaste_interface__membrane__V) * var_chaste_interface__fast_sodium_current_h_gate__h * var_chaste_interface__fast_sodium_current_j_gate__j; // picoA_per_picoF
        const double var_hyperpolarization_activated_current__i_f_Na = 0.014565399999999999 * (-var_reversal_potentials__E_Na + var_chaste_interface__membrane__V) * var_chaste_interface__hyperpolarization_activated_current_y_gate__y; // picoA_per_picoF
        const double var_slow_time_dependent_potassium_current__i_Ks = 0.23519999999999999 * pow(var_chaste_interface__slow_time_dependent_potassium_current_Xs_gate__Xs, 2.0) * (-26.713760659695652 * log(9.6000000000000014 / (0.029999999999999999 * var_chaste_interface__sodium_dynamics__Na_i + var_chaste_interface__potassium_dynamics__K_i)) + var_chaste_interface__membrane__V); // picoA_per_picoF
        const double var_sodium_background_current__i_b_Na = 0.00029 * var_chaste_interface__membrane__V - 0.00029 * var_reversal_potentials__E_Na; // picoA_per_picoF
        const double var_sodium_calcium_exchanger_current__i_NaCa = 8.6662202299424464e-5 * (2.0 * pow(var_chaste_interface__sodium_dynamics__Na_i, 3.0) * exp(0.013101861787960915 * var_chaste_interface__membrane__V) - 6860000.0 * var_chaste_interface__calcium_dynamics__Ca_i * exp(-0.024332029034784559 * var_chaste_interface__membrane__V)) / (1.0 + 0.10000000000000001 * exp(-0.024332029034784559 * var_chaste_interface__membrane__V)); // picoA_per_picoF
        const double d_dt_chaste_interface_var_calcium_dynamics__Ca_i = 1.0 * (0.066691050963179718 * var_calcium_dynamics__i_leak + 0.00011688549744401942 * var_sodium_calcium_exchanger_current__i_NaCa - 0.066691050963179718 * var_calcium_dynamics__i_up - 5.8442748722009712e-5 * var_calcium_background_current__i_b_Ca - 5.8442748722009712e-5 * var_calcium_pump_current__i_p_Ca + var_calcium_dynamics__i_xfer) / (1.0 + 0.00020000000000000001 * pow((0.001 + var_chaste_interface__calcium_dynamics__Ca_i), (-2.0))); // millimolar / millisecond
        const double var_sodium_potassium_pump_current__i_NaK = 2.2983750000000001 * var_chaste_interface__sodium_dynamics__Na_i / ((40.0 + var_chaste_interface__sodium_dynamics__Na_i) * (1.0 + 0.035299999999999998 * exp(-0.037433890822745473 * var_chaste_interface__membrane__V) + 0.1245 * exp(-0.0037433890822745476 * var_chaste_interface__membrane__V))); // picoA_per_picoF
        const double d_dt_chaste_interface_var_sodium_dynamics__Na_i = -0.00035065649233205829 * var_sodium_calcium_exchanger_current__i_NaCa - 0.00035065649233205829 * var_sodium_potassium_pump_current__i_NaK - 0.00011688549744401942 * var_fast_sodium_current__i_Na - 0.00011688549744401942 * var_hyperpolarization_activated_current__i_f_Na - 0.00011688549744401942 * var_sodium_background_current__i_b_Na; // millimolar / millisecond
        const double var_sustained_outward_current__i_sus = 0.022700000000000001 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) / (1.0 + exp(0.29411764705882354 - 0.058823529411764705 * var_chaste_interface__membrane__V)); // picoA_per_picoF
        const double d_dt_chaste_interface_var_transient_outward_current_r_gate__r = (-var_chaste_interface__transient_outward_current_r_gate__r + 1.0 / (1.0 + exp(1.5384615384615385 - 0.076923076923076927 * var_chaste_interface__membrane__V))) / (7.2999999999999998 + 10.449999999999999 * exp(-0.88888888888888884 * pow((1 + 0.025000000000000001 * var_chaste_interface__membrane__V), 2.0))); // 1 / millisecond
        const double var_transient_outward_current__i_to = 0.081839999999999996 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) * var_chaste_interface__transient_outward_current_r_gate__r * var_chaste_interface__transient_outward_current_s_gate__s; // picoA_per_picoF
        const double d_dt_chaste_interface_var_potassium_dynamics__K_i = 0.00023377099488803885 * var_sodium_potassium_pump_current__i_NaK - 0.00011688549744401942 * var_hyperpolarization_activated_current__i_f_K - 0.00011688549744401942 * var_inward_rectifier_potassium_current__i_K1 - 0.00011688549744401942 * var_potassium_pump_current__i_p_K - 0.00011688549744401942 * var_rapid_time_dependent_potassium_current__i_Kr - 0.00011688549744401942 * var_slow_time_dependent_potassium_current__i_Ks - 0.00011688549744401942 * var_sustained_outward_current__i_sus - 0.00011688549744401942 * var_transient_outward_current__i_to; // millimolar / millisecond
        const double d_dt_chaste_interface_var_transient_outward_current_s_gate__s = (-var_chaste_interface__transient_outward_current_s_gate__s + 1.0 / (1.0 + exp(2.0769230769230771 + 0.076923076923076927 * var_chaste_interface__membrane__V))) / (42.0 + 5.0 / (1.0 + exp(-8.0 + 0.20000000000000001 * var_chaste_interface__membrane__V)) + 85.0 * exp(-1.953125 * pow((1 + 0.040000000000000001 * var_chaste_interface__membrane__V), 2.0))); // 1 / millisecond

        if (mSetVoltageDerivativeToZero)
        {
            d_dt_chaste_interface_var_membrane__V = 0.0;
        }
        else
        {
            d_dt_chaste_interface_var_membrane__V = -1.0 * var_L_type_Ca_current__i_CaL - 1.0 * var_calcium_background_current__i_b_Ca - 1.0 * var_calcium_pump_current__i_p_Ca - 1.0 * var_fast_sodium_current__i_Na - 1.0 * var_hyperpolarization_activated_current__i_f_K - 1.0 * var_hyperpolarization_activated_current__i_f_Na - 1.0 * var_inward_rectifier_potassium_current__i_K1 - 1.0 * var_potassium_pump_current__i_p_K - 1.0 * var_rapid_time_dependent_potassium_current__i_Kr - 1.0 * var_slow_time_dependent_potassium_current__i_Ks - 1.0 * var_sodium_background_current__i_b_Na - 1.0 * var_sodium_calcium_exchanger_current__i_NaCa - 1.0 * var_sodium_potassium_pump_current__i_NaK - 1.0 * var_sustained_outward_current__i_sus - 1.0 * var_transient_outward_current__i_to; // millivolt / millisecond
        }
        
        rDY[0] = d_dt_chaste_interface_var_membrane__V;
        rDY[1] = d_dt_chaste_interface_var_calcium_dynamics__Ca_i;
        rDY[2] = d_dt_chaste_interface_var_hyperpolarization_activated_current_y_gate__y;
        rDY[3] = d_dt_chaste_interface_var_rapid_time_dependent_potassium_current_Xr1_gate__Xr1;
        rDY[4] = d_dt_chaste_interface_var_rapid_time_dependent_potassium_current_Xr2_gate__Xr2;
        rDY[5] = d_dt_chaste_interface_var_slow_time_dependent_potassium_current_Xs_gate__Xs;
        rDY[6] = d_dt_chaste_interface_var_fast_sodium_current_m_gate__m;
        rDY[7] = d_dt_chaste_interface_var_fast_sodium_current_h_gate__h;
        rDY[8] = d_dt_chaste_interface_var_fast_sodium_current_j_gate__j;
        rDY[9] = d_dt_chaste_interface_var_L_type_Ca_current_d_gate__d;
        rDY[10] = d_dt_chaste_interface_var_L_type_Ca_current_f_gate__f;
        rDY[11] = d_dt_chaste_interface_var_L_type_Ca_current_f2_gate__f2;
        rDY[12] = d_dt_chaste_interface_var_L_type_Ca_current_fCass_gate__fCass;
        rDY[13] = d_dt_chaste_interface_var_transient_outward_current_s_gate__s;
        rDY[14] = d_dt_chaste_interface_var_transient_outward_current_r_gate__r;
        rDY[15] = d_dt_chaste_interface_var_calcium_dynamics__Ca_SR;
        rDY[16] = d_dt_chaste_interface_var_calcium_dynamics__Ca_ss;
        rDY[17] = d_dt_chaste_interface_var_calcium_dynamics__R_prime;
        rDY[18] = d_dt_chaste_interface_var_sodium_dynamics__Na_i;
        rDY[19] = d_dt_chaste_interface_var_potassium_dynamics__K_i;
    }

template<>
void OdeSystemInformation<Cellstewart_zhang_model_2008_ssFromCellML>::Initialise(void)
{
    this->mSystemName = "stewart_zhang_model_2008";
    this->mFreeVariableName = "environment__time";
    this->mFreeVariableUnits = "millisecond";

    // rY[0]:
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("millivolt");
    this->mInitialConditions.push_back(-69.1370441635924);

    // rY[1]:
    this->mVariableNames.push_back("cytosolic_calcium_concentration");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(0.000101878186157052);

    // rY[2]:
    this->mVariableNames.push_back("hyperpolarization_activated_current_y_gate__y");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0457562667986602);

    // rY[3]:
    this->mVariableNames.push_back("rapid_time_dependent_potassium_current_Xr1_gate__Xr1");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.00550281999719088);

    // rY[4]:
    this->mVariableNames.push_back("rapid_time_dependent_potassium_current_Xr2_gate__Xr2");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.313213286437995);

    // rY[5]:
    this->mVariableNames.push_back("slow_time_dependent_potassium_current_Xs_gate__Xs");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.00953708522974789);

    // rY[6]:
    this->mVariableNames.push_back("membrane_fast_sodium_current_m_gate");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0417391656294997);

    // rY[7]:
    this->mVariableNames.push_back("membrane_fast_sodium_current_h_gate");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.190678733735145);

    // rY[8]:
    this->mVariableNames.push_back("membrane_fast_sodium_current_j_gate");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.238219836154029);

    // rY[9]:
    this->mVariableNames.push_back("membrane_L_type_calcium_current_d_gate");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.000287906256206415);

    // rY[10]:
    this->mVariableNames.push_back("membrane_L_type_calcium_current_f_gate");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.989328560287987);

    // rY[11]:
    this->mVariableNames.push_back("membrane_L_type_calcium_current_f2_gate");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.995474890442185);

    // rY[12]:
    this->mVariableNames.push_back("membrane_L_type_calcium_current_fCa2_gate");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.999955429598213);

    // rY[13]:
    this->mVariableNames.push_back("transient_outward_current_s_gate__s");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.96386101799501);

    // rY[14]:
    this->mVariableNames.push_back("transient_outward_current_r_gate__r");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.00103618091196912);

    // rY[15]:
    this->mVariableNames.push_back("calcium_dynamics__Ca_SR");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(3.10836886659417);

    // rY[16]:
    this->mVariableNames.push_back("dyadic_space_calcium_concentration");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(0.000446818714055411);

    // rY[17]:
    this->mVariableNames.push_back("calcium_dynamics__R_prime");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.991580051907845);

    // rY[18]:
    this->mVariableNames.push_back("cytosolic_sodium_concentration");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(8.80420286531673);

    // rY[19]:
    this->mVariableNames.push_back("cytosolic_potassium_concentration");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(136.781894160227);

    this->mInitialised = true;
}


// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Cellstewart_zhang_model_2008_ssFromCellML)

