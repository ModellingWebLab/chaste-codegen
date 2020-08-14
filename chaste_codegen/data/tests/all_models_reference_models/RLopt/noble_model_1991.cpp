//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: noble_model_1991
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: RushLarsenOpt)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "noble_model_1991.hpp"
#include <cmath>
#include <cassert>
#include <memory>
#include "Exception.hpp"
#include "OdeSystemInformation.hpp"
#include "RegularStimulus.hpp"
#include "HeartConfig.hpp"
#include "IsNan.hpp"
#include "MathsCustomFunctions.hpp"

    boost::shared_ptr<RegularStimulus> Cellnoble_model_1991FromCellMLRushLarsenOpt::UseCellMLDefaultStimulus()
    {
        // Use the default stimulus specified by CellML metadata
        const double var_chaste_interface__membrane__stim_amplitude_converted = -0.0060000000000000001 * HeartConfig::Instance()->GetCapacitance() / mParameters[0]; // uA_per_cm2
        const double var_chaste_interface__membrane__stim_duration_converted = 2.0; // millisecond
        const double var_chaste_interface__membrane__stim_period_converted = 1000.0; // millisecond
        const double var_chaste_interface__membrane__stim_start_converted = 100.0; // millisecond
        boost::shared_ptr<RegularStimulus> p_cellml_stim(new RegularStimulus(
                -fabs(var_chaste_interface__membrane__stim_amplitude_converted),
                var_chaste_interface__membrane__stim_duration_converted,
                var_chaste_interface__membrane__stim_period_converted,
                var_chaste_interface__membrane__stim_start_converted
                ));
        mpIntracellularStimulus = p_cellml_stim;
        return p_cellml_stim;
    }

    Cellnoble_model_1991FromCellMLRushLarsenOpt::Cellnoble_model_1991FromCellMLRushLarsenOpt(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractRushLarsenCardiacCell(
                17,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        //
        this->mpSystemInfo = OdeSystemInformation<Cellnoble_model_1991FromCellMLRushLarsenOpt>::Instance();
        Init();

        // We have a default stimulus specified in the CellML file metadata
        this->mHasDefaultStimulusFromCellML = true;
        
        this->mParameters[0] = 9.5000000000000005e-5; // (var_membrane__Cm) [microF]
    }

    Cellnoble_model_1991FromCellMLRushLarsenOpt::~Cellnoble_model_1991FromCellMLRushLarsenOpt()
    {
    }
    
    double Cellnoble_model_1991FromCellMLRushLarsenOpt::GetIIonic(const std::vector<double>* pStateVariables)
    {
        // For state variable interpolation (SVI) we read in interpolated state variables,
        // otherwise for ionic current interpolation (ICI) we use the state variables of this model (node).
        if (!pStateVariables) pStateVariables = &rGetStateVariables();
        const std::vector<double>& rY = *pStateVariables;
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -93.0
        double var_chaste_interface__time_dependent_potassium_current_x_gate__x = rY[1];
        // Units: dimensionless; Initial value: 0.001
        double var_chaste_interface__fast_sodium_current_m_gate__m = rY[2];
        // Units: dimensionless; Initial value: 0.000105
        double var_chaste_interface__fast_sodium_current_h_gate__h = rY[3];
        // Units: dimensionless; Initial value: 0.99816539
        double var_chaste_interface__L_type_Ca_channel_d_gate__d = rY[4];
        // Units: dimensionless; Initial value: 0.0
        double var_chaste_interface__L_type_Ca_channel_f_gate__f = rY[5];
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__transient_outward_current_s_gate__s = rY[6];
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__transient_outward_current_r_gate__r = rY[7];
        // Units: dimensionless; Initial value: 0.0
        double var_chaste_interface__intracellular_sodium_concentration__Na_i = rY[10];
        // Units: millimolar; Initial value: 5.0
        double var_chaste_interface__intracellular_potassium_concentration__K_i = rY[11];
        // Units: millimolar; Initial value: 140.0
        double var_chaste_interface__intracellular_calcium_concentration__Ca_i = rY[12];
        // Units: millimolar; Initial value: 7.63e-06
        
        const double var_L_type_Ca_channel__i_Ca_L_Ca = 0.037433890822745473 * (-50.0 + var_chaste_interface__membrane__V) * (-2.0 * exp(3.7433890822745473 - 0.074867781645490947 * var_chaste_interface__membrane__V) + var_chaste_interface__intracellular_calcium_concentration__Ca_i * exp(3.7433890822745473)) * var_chaste_interface__L_type_Ca_channel_d_gate__d * var_chaste_interface__L_type_Ca_channel_f_gate__f / (1.0 - exp(3.7433890822745473 - 0.074867781645490947 * var_chaste_interface__membrane__V)); // nanoA
        const double var_L_type_Ca_channel__i_Ca_L_K = 1.8716945411372735e-5 * (-50.0 + var_chaste_interface__membrane__V) * (-4.0 * exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V) + var_chaste_interface__intracellular_potassium_concentration__K_i * exp(1.8716945411372736)) * var_chaste_interface__L_type_Ca_channel_d_gate__d * var_chaste_interface__L_type_Ca_channel_f_gate__f / (1.0 - exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V)); // nanoA
        const double var_L_type_Ca_channel__i_Ca_L_Na = 9.3584727056863679e-5 * (-50.0 + var_chaste_interface__membrane__V) * (-140.0 * exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V) + var_chaste_interface__intracellular_sodium_concentration__Na_i * exp(1.8716945411372736)) * var_chaste_interface__L_type_Ca_channel_d_gate__d * var_chaste_interface__L_type_Ca_channel_f_gate__f / (1.0 - exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V)); // nanoA
        const double var_calcium_background_current__i_b_Ca = 0.00025000000000000001 * var_chaste_interface__membrane__V - 0.0033392200824619565 * log(2.0 / var_chaste_interface__intracellular_calcium_concentration__Ca_i); // nanoA
        const double var_reversal_potentials__E_K = 26.713760659695652 * log(4.0 / var_chaste_interface__intracellular_potassium_concentration__K_i); // millivolt
        const double var_potassium_background_current__i_b_K = 0.00059999999999999995 * var_chaste_interface__membrane__V - 0.00059999999999999995 * var_reversal_potentials__E_K; // nanoA
        const double var_fast_sodium_current__i_Na = 2.5 * pow(var_chaste_interface__fast_sodium_current_m_gate__m, 3) * (-26.713760659695652 * log(140.47999999999999 / (var_chaste_interface__intracellular_sodium_concentration__Na_i + 0.12 * var_chaste_interface__intracellular_potassium_concentration__K_i)) + var_chaste_interface__membrane__V) * var_chaste_interface__fast_sodium_current_h_gate__h; // nanoA
        const double var_sodium_background_current__i_b_Na = 0.00059999999999999995 * var_chaste_interface__membrane__V - 0.016028256395817387 * log(140.0 / var_chaste_interface__intracellular_sodium_concentration__Na_i); // nanoA
        const double var_sodium_calcium_exchanger__i_NaCa = 0.00050000000000000001 * (2.0 * pow(var_chaste_interface__intracellular_sodium_concentration__Na_i, 3.0) * exp(0.018716945411372737 * var_chaste_interface__membrane__V) - 2744000.0 * var_chaste_interface__intracellular_calcium_concentration__Ca_i * exp(-0.018716945411372737 * var_chaste_interface__membrane__V)) / (1.0 + 144.92753623188406 * var_chaste_interface__intracellular_calcium_concentration__Ca_i); // nanoA
        const double var_sodium_potassium_pump__i_NaK = 0.55999999999999994 * var_chaste_interface__intracellular_sodium_concentration__Na_i / (40.0 + var_chaste_interface__intracellular_sodium_concentration__Na_i); // nanoA
        const double var_time_dependent_potassium_current__i_K = (0.0071428571428571426 * var_chaste_interface__intracellular_potassium_concentration__K_i - 0.028571428571428571 * exp(-0.037433890822745473 * var_chaste_interface__membrane__V)) * var_chaste_interface__time_dependent_potassium_current_x_gate__x; // nanoA
        const double var_time_independent_potassium_current__i_K1 = 0.2857142857142857 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) / (1.0 + exp(-0.74867781645490938 + 0.074867781645490947 * var_chaste_interface__membrane__V - 0.074867781645490947 * var_reversal_potentials__E_K)); // nanoA
        const double var_transient_outward_current__i_to = 0.0050000000000000001 * (-var_reversal_potentials__E_K + var_chaste_interface__membrane__V) * var_chaste_interface__transient_outward_current_r_gate__r * var_chaste_interface__transient_outward_current_s_gate__s; // nanoA
        const double var_chaste_interface__i_ionic = 0.001 * (var_L_type_Ca_channel__i_Ca_L_Ca + var_L_type_Ca_channel__i_Ca_L_K + var_L_type_Ca_channel__i_Ca_L_Na + var_calcium_background_current__i_b_Ca + var_fast_sodium_current__i_Na + var_potassium_background_current__i_b_K + var_sodium_background_current__i_b_Na + var_sodium_calcium_exchanger__i_NaCa + var_sodium_potassium_pump__i_NaK + var_time_dependent_potassium_current__i_K + var_time_independent_potassium_current__i_K1 + var_transient_outward_current__i_to) * HeartConfig::Instance()->GetCapacitance() / mParameters[0]; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellnoble_model_1991FromCellMLRushLarsenOpt::EvaluateEquations(double var_chaste_interface__environment__time_converted, std::vector<double> &rDY, std::vector<double> &rAlphaOrTau, std::vector<double> &rBetaOrInf)
    {
        std::vector<double>& rY = rGetStateVariables();
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -93.0
        double var_chaste_interface__time_dependent_potassium_current_x_gate__x = rY[1];
        // Units: dimensionless; Initial value: 0.001
        double var_chaste_interface__fast_sodium_current_m_gate__m = rY[2];
        // Units: dimensionless; Initial value: 0.000105
        double var_chaste_interface__fast_sodium_current_h_gate__h = rY[3];
        // Units: dimensionless; Initial value: 0.99816539
        double var_chaste_interface__L_type_Ca_channel_d_gate__d = rY[4];
        // Units: dimensionless; Initial value: 0.0
        double var_chaste_interface__L_type_Ca_channel_f_gate__f = rY[5];
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__transient_outward_current_s_gate__s = rY[6];
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__transient_outward_current_r_gate__r = rY[7];
        // Units: dimensionless; Initial value: 0.0
        double var_chaste_interface__calcium_release__ActFrac = rY[8];
        // Units: dimensionless; Initial value: 0.0
        double var_chaste_interface__calcium_release__ProdFrac = rY[9];
        // Units: dimensionless; Initial value: 0.0
        double var_chaste_interface__intracellular_sodium_concentration__Na_i = rY[10];
        // Units: millimolar; Initial value: 5.0
        double var_chaste_interface__intracellular_potassium_concentration__K_i = rY[11];
        // Units: millimolar; Initial value: 140.0
        double var_chaste_interface__intracellular_calcium_concentration__Ca_i = rY[12];
        // Units: millimolar; Initial value: 7.63e-06
        double var_chaste_interface__intracellular_calcium_concentration__Ca_up = rY[13];
        // Units: millimolar; Initial value: 0.3013
        double var_chaste_interface__intracellular_calcium_concentration__Ca_rel = rY[14];
        // Units: millimolar; Initial value: 0.2989
        double var_chaste_interface__intracellular_calcium_concentration__Ca_Calmod = rY[15];
        // Units: millimolar; Initial value: 0.0003
        double var_chaste_interface__intracellular_calcium_concentration__Ca_Trop = rY[16];
        // Units: millimolar; Initial value: 0.0002

        // Mathematics
        double d_dt_chaste_interface_var_membrane__V;
        const double var_L_type_Ca_channel_d_gate__speed_d = 3.0; // dimensionless
        const double var_L_type_Ca_channel_f_gate__speed_f = 0.5; // dimensionless
        const double d_dt_chaste_interface_var_calcium_release__ActFrac = -0.001 * (60.0 + 500.0 * pow(var_chaste_interface__intracellular_calcium_concentration__Ca_i, 2) / pow((0.00050000000000000001 + var_chaste_interface__intracellular_calcium_concentration__Ca_i), 2)) * var_chaste_interface__calcium_release__ActFrac + 0.5 * pow(var_chaste_interface__intracellular_calcium_concentration__Ca_i, 2) * (1.0 - var_chaste_interface__calcium_release__ActFrac - var_chaste_interface__calcium_release__ProdFrac) / pow((0.00050000000000000001 + var_chaste_interface__intracellular_calcium_concentration__Ca_i), 2); // 1 / millisecond
        const double d_dt_chaste_interface_var_calcium_release__ProdFrac = -0.001 * var_chaste_interface__calcium_release__ProdFrac + 0.001 * (60.0 + 500.0 * pow(var_chaste_interface__intracellular_calcium_concentration__Ca_i, 2) / pow((0.00050000000000000001 + var_chaste_interface__intracellular_calcium_concentration__Ca_i), 2)) * var_chaste_interface__calcium_release__ActFrac; // 1 / millisecond
        const double d_dt_chaste_interface_var_intracellular_calcium_concentration__Ca_rel = 0.0050000000000000001 * var_chaste_interface__intracellular_calcium_concentration__Ca_up - 0.0050000000000000001 * var_chaste_interface__intracellular_calcium_concentration__Ca_rel - 0.25 * pow(var_chaste_interface__calcium_release__ActFrac, 2) * var_chaste_interface__intracellular_calcium_concentration__Ca_rel / pow((0.25 + var_chaste_interface__calcium_release__ActFrac), 2); // millimolar / millisecond
        const double d_dt_chaste_interface_var_intracellular_calcium_concentration__Ca_Calmod = -0.050000000000000003 * var_chaste_interface__intracellular_calcium_concentration__Ca_Calmod + 100.0 * (0.02 - var_chaste_interface__intracellular_calcium_concentration__Ca_Calmod) * var_chaste_interface__intracellular_calcium_concentration__Ca_i; // millimolar / millisecond
        const double d_dt_chaste_interface_var_intracellular_calcium_concentration__Ca_Trop = -0.20000000000000001 * var_chaste_interface__intracellular_calcium_concentration__Ca_Trop + 100.0 * (0.050000000000000003 - var_chaste_interface__intracellular_calcium_concentration__Ca_Trop) * var_chaste_interface__intracellular_calcium_concentration__Ca_i; // millimolar / millisecond
        const double var_L_type_Ca_channel_d_gate__alpha_d = ((fabs(19.0 + var_chaste_interface__membrane__V) < 0.0001) ? (120.0) : (30.0 * (19.0 + var_chaste_interface__membrane__V) / (1.0 - exp(-4.75 - 0.25 * var_chaste_interface__membrane__V)))); // per_second
        const double var_L_type_Ca_channel_d_gate__beta_d = ((fabs(19.0 + var_chaste_interface__membrane__V) < 0.0001) ? (120.0) : (12.0 * (19.0 + var_chaste_interface__membrane__V) / (-1.0 + exp(1.8999999999999999 + 0.10000000000000001 * var_chaste_interface__membrane__V)))); // per_second
        const double var_L_type_Ca_channel_f_gate__alpha_f = ((fabs(34.0 + var_chaste_interface__membrane__V) < 0.0001) ? (25.0) : (6.25 * (34.0 + var_chaste_interface__membrane__V) / (-1.0 + exp(8.5 + 0.25 * var_chaste_interface__membrane__V)))); // per_second
        const double var_L_type_Ca_channel_f_gate__beta_f = 50.0 / (1.0 + exp(-8.5 - 0.25 * var_chaste_interface__membrane__V)); // per_second
        const double var_fast_sodium_current_h_gate__alpha_h = 20.0 * exp(-9.375 - 0.125 * var_chaste_interface__membrane__V); // per_second
        const double var_fast_sodium_current_h_gate__beta_h = 2000.0 / (1.0 + 320.0 * exp(-7.5 - 0.10000000000000001 * var_chaste_interface__membrane__V)); // per_second
        const double var_fast_sodium_current_m_gate__alpha_m = ((fabs(41.0 + var_chaste_interface__membrane__V) < 1.0000000000000001e-5) ? (2000.0) : (200.0 * (41.0 + var_chaste_interface__membrane__V) / (1.0 - exp(-4.1000000000000005 - 0.10000000000000001 * var_chaste_interface__membrane__V)))); // per_second
        const double var_fast_sodium_current_m_gate__beta_m = 8000.0 * exp(-3.6960000000000002 - 0.056000000000000001 * var_chaste_interface__membrane__V); // per_second
        const double d_dt_chaste_interface_var_intracellular_calcium_concentration__Ca_up = 0.050000000000000003 * var_chaste_interface__intracellular_calcium_concentration__Ca_rel - 0.050000000000000003 * var_chaste_interface__intracellular_calcium_concentration__Ca_up + 0.019599999999999999 * var_chaste_interface__intracellular_calcium_concentration__Ca_i / (0.00041999999999999996 + 0.00023999999999999998 * var_chaste_interface__intracellular_calcium_concentration__Ca_up + var_chaste_interface__intracellular_calcium_concentration__Ca_i) - 3.5279999999999993e-7 * var_chaste_interface__intracellular_calcium_concentration__Ca_up / (0.00041999999999999996 + 0.00023999999999999998 * var_chaste_interface__intracellular_calcium_concentration__Ca_up + var_chaste_interface__intracellular_calcium_concentration__Ca_i); // millimolar / millisecond
        const double d_dt_chaste_interface_var_intracellular_calcium_concentration__Ca_i = 1.0549054718227806e-6 * log(2.0 / var_chaste_interface__intracellular_calcium_concentration__Ca_i) + 0.050000000000000003 * var_chaste_interface__intracellular_calcium_concentration__Ca_Calmod + 0.20000000000000001 * var_chaste_interface__intracellular_calcium_concentration__Ca_Trop - 7.8978432521061529e-8 * var_chaste_interface__membrane__V + 3.1591373008424611e-7 * (2.0 * pow(var_chaste_interface__intracellular_sodium_concentration__Na_i, 3.0) * exp(0.018716945411372737 * var_chaste_interface__membrane__V) - 2744000.0 * var_chaste_interface__intracellular_calcium_concentration__Ca_i * exp(-0.018716945411372737 * var_chaste_interface__membrane__V)) / (1.0 + 144.92753623188406 * var_chaste_interface__intracellular_calcium_concentration__Ca_i) + 7.1999999999999991e-9 * var_chaste_interface__intracellular_calcium_concentration__Ca_up / (0.00041999999999999996 + 0.00023999999999999998 * var_chaste_interface__intracellular_calcium_concentration__Ca_up + var_chaste_interface__intracellular_calcium_concentration__Ca_i) - 100.0 * (0.050000000000000003 - var_chaste_interface__intracellular_calcium_concentration__Ca_Trop) * var_chaste_interface__intracellular_calcium_concentration__Ca_i - 100.0 * (0.02 - var_chaste_interface__intracellular_calcium_concentration__Ca_Calmod) * var_chaste_interface__intracellular_calcium_concentration__Ca_i - 0.00040000000000000002 * var_chaste_interface__intracellular_calcium_concentration__Ca_i / (0.00041999999999999996 + 0.00023999999999999998 * var_chaste_interface__intracellular_calcium_concentration__Ca_up + var_chaste_interface__intracellular_calcium_concentration__Ca_i) + 0.051020408163265314 * pow(var_chaste_interface__calcium_release__ActFrac, 2) * var_chaste_interface__intracellular_calcium_concentration__Ca_rel / pow((0.25 + var_chaste_interface__calcium_release__ActFrac), 2) - 1.1825880081379951e-5 * (-50.0 + var_chaste_interface__membrane__V) * (-2.0 * exp(3.7433890822745473 - 0.074867781645490947 * var_chaste_interface__membrane__V) + var_chaste_interface__intracellular_calcium_concentration__Ca_i * exp(3.7433890822745473)) * var_chaste_interface__L_type_Ca_channel_d_gate__d * var_chaste_interface__L_type_Ca_channel_f_gate__f / (1.0 - exp(3.7433890822745473 - 0.074867781645490947 * var_chaste_interface__membrane__V)); // millimolar / millisecond
        const double d_dt_chaste_interface_var_intracellular_sodium_concentration__Na_i = 1.0127092529498693e-5 * log(140.0 / var_chaste_interface__intracellular_sodium_concentration__Na_i) - 3.7909647610109532e-7 * var_chaste_interface__membrane__V - 0.0010614701330830668 * var_chaste_interface__intracellular_sodium_concentration__Na_i / (40.0 + var_chaste_interface__intracellular_sodium_concentration__Na_i) - 9.477411902527384e-7 * (2.0 * pow(var_chaste_interface__intracellular_sodium_concentration__Na_i, 3.0) * exp(0.018716945411372737 * var_chaste_interface__membrane__V) - 2744000.0 * var_chaste_interface__intracellular_calcium_concentration__Ca_i * exp(-0.018716945411372737 * var_chaste_interface__membrane__V)) / (1.0 + 144.92753623188406 * var_chaste_interface__intracellular_calcium_concentration__Ca_i) - 0.0015795686504212305 * pow(var_chaste_interface__fast_sodium_current_m_gate__m, 3) * (-26.713760659695652 * log(140.47999999999999 / (var_chaste_interface__intracellular_sodium_concentration__Na_i + 0.12 * var_chaste_interface__intracellular_potassium_concentration__K_i)) + var_chaste_interface__membrane__V) * var_chaste_interface__fast_sodium_current_h_gate__h - 5.9129400406899753e-8 * (-50.0 + var_chaste_interface__membrane__V) * (-140.0 * exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V) + var_chaste_interface__intracellular_sodium_concentration__Na_i * exp(1.8716945411372736)) * var_chaste_interface__L_type_Ca_channel_d_gate__d * var_chaste_interface__L_type_Ca_channel_f_gate__f / (1.0 - exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V)); // millimolar / millisecond
        const double var_time_dependent_potassium_current_x_gate__alpha_x = 0.5 * exp(4.1300000000000008 + 0.082600000000000007 * var_chaste_interface__membrane__V) / (1.0 + exp(2.8500000000000001 + 0.057000000000000002 * var_chaste_interface__membrane__V)); // per_second
        const double var_time_dependent_potassium_current_x_gate__beta_x = 1.3 * exp(-1.2 - 0.059999999999999998 * var_chaste_interface__membrane__V) / (1.0 + exp(-0.80000000000000004 - 0.040000000000000001 * var_chaste_interface__membrane__V)); // per_second
        const double var_transient_outward_current_s_gate__alpha_s = 0.033000000000000002 * exp(-0.058823529411764705 * var_chaste_interface__membrane__V); // per_second
        const double var_transient_outward_current_s_gate__beta_s = 33.0 / (1.0 + exp(-1.25 - 0.125 * var_chaste_interface__membrane__V)); // per_second
        const double d_dt_chaste_interface_var_intracellular_potassium_concentration__K_i = 1.0127092529498693e-5 * log(4.0 / var_chaste_interface__intracellular_potassium_concentration__K_i) - 3.7909647610109532e-7 * var_chaste_interface__membrane__V + 0.00070764675538871125 * var_chaste_interface__intracellular_sodium_concentration__Na_i / (40.0 + var_chaste_interface__intracellular_sodium_concentration__Na_i) - 0.00018052213147671208 * (-26.713760659695652 * log(4.0 / var_chaste_interface__intracellular_potassium_concentration__K_i) + var_chaste_interface__membrane__V) / (1.0 + exp(-0.74867781645490938 + 0.074867781645490947 * var_chaste_interface__membrane__V - 2.0 * log(4.0 / var_chaste_interface__intracellular_potassium_concentration__K_i))) - 0.00063182746016849224 * (0.0071428571428571426 * var_chaste_interface__intracellular_potassium_concentration__K_i - 0.028571428571428571 * exp(-0.037433890822745473 * var_chaste_interface__membrane__V)) * var_chaste_interface__time_dependent_potassium_current_x_gate__x - 3.1591373008424612e-6 * (-26.713760659695652 * log(4.0 / var_chaste_interface__intracellular_potassium_concentration__K_i) + var_chaste_interface__membrane__V) * var_chaste_interface__transient_outward_current_r_gate__r * var_chaste_interface__transient_outward_current_s_gate__s - 1.182588008137995e-8 * (-50.0 + var_chaste_interface__membrane__V) * (-4.0 * exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V) + var_chaste_interface__intracellular_potassium_concentration__K_i * exp(1.8716945411372736)) * var_chaste_interface__L_type_Ca_channel_d_gate__d * var_chaste_interface__L_type_Ca_channel_f_gate__f / (1.0 - exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V)); // millimolar / millisecond

        if (mSetVoltageDerivativeToZero)
        {
            d_dt_chaste_interface_var_membrane__V = 0.0;
        }
        else
        {
            d_dt_chaste_interface_var_membrane__V = -0.001 * (0.0014499999999999999 * var_chaste_interface__membrane__V - 0.0033392200824619565 * log(2.0 / var_chaste_interface__intracellular_calcium_concentration__Ca_i) - 0.016028256395817387 * log(4.0 / var_chaste_interface__intracellular_potassium_concentration__K_i) - 0.016028256395817387 * log(140.0 / var_chaste_interface__intracellular_sodium_concentration__Na_i) + (0.0071428571428571426 * var_chaste_interface__intracellular_potassium_concentration__K_i - 0.028571428571428571 * exp(-0.037433890822745473 * var_chaste_interface__membrane__V)) * var_chaste_interface__time_dependent_potassium_current_x_gate__x + 0.00050000000000000001 * (2.0 * pow(var_chaste_interface__intracellular_sodium_concentration__Na_i, 3.0) * exp(0.018716945411372737 * var_chaste_interface__membrane__V) - 2744000.0 * var_chaste_interface__intracellular_calcium_concentration__Ca_i * exp(-0.018716945411372737 * var_chaste_interface__membrane__V)) / (1.0 + 144.92753623188406 * var_chaste_interface__intracellular_calcium_concentration__Ca_i) + 0.55999999999999994 * var_chaste_interface__intracellular_sodium_concentration__Na_i / (40.0 + var_chaste_interface__intracellular_sodium_concentration__Na_i) + 0.2857142857142857 * (-26.713760659695652 * log(4.0 / var_chaste_interface__intracellular_potassium_concentration__K_i) + var_chaste_interface__membrane__V) / (1.0 + exp(-0.74867781645490938 + 0.074867781645490947 * var_chaste_interface__membrane__V - 2.0 * log(4.0 / var_chaste_interface__intracellular_potassium_concentration__K_i))) + 2.5 * pow(var_chaste_interface__fast_sodium_current_m_gate__m, 3) * (-26.713760659695652 * log(140.47999999999999 / (var_chaste_interface__intracellular_sodium_concentration__Na_i + 0.12 * var_chaste_interface__intracellular_potassium_concentration__K_i)) + var_chaste_interface__membrane__V) * var_chaste_interface__fast_sodium_current_h_gate__h + 1000.0 * GetIntracellularAreaStimulus(var_chaste_interface__environment__time_converted) * mParameters[0] / HeartConfig::Instance()->GetCapacitance() + 0.0050000000000000001 * (-26.713760659695652 * log(4.0 / var_chaste_interface__intracellular_potassium_concentration__K_i) + var_chaste_interface__membrane__V) * var_chaste_interface__transient_outward_current_r_gate__r * var_chaste_interface__transient_outward_current_s_gate__s + 0.037433890822745473 * (-50.0 + var_chaste_interface__membrane__V) * (-2.0 * exp(3.7433890822745473 - 0.074867781645490947 * var_chaste_interface__membrane__V) + var_chaste_interface__intracellular_calcium_concentration__Ca_i * exp(3.7433890822745473)) * var_chaste_interface__L_type_Ca_channel_d_gate__d * var_chaste_interface__L_type_Ca_channel_f_gate__f / (1.0 - exp(3.7433890822745473 - 0.074867781645490947 * var_chaste_interface__membrane__V)) + 1.8716945411372735e-5 * (-50.0 + var_chaste_interface__membrane__V) * (-4.0 * exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V) + var_chaste_interface__intracellular_potassium_concentration__K_i * exp(1.8716945411372736)) * var_chaste_interface__L_type_Ca_channel_d_gate__d * var_chaste_interface__L_type_Ca_channel_f_gate__f / (1.0 - exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V)) + 9.3584727056863679e-5 * (-50.0 + var_chaste_interface__membrane__V) * (-140.0 * exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V) + var_chaste_interface__intracellular_sodium_concentration__Na_i * exp(1.8716945411372736)) * var_chaste_interface__L_type_Ca_channel_d_gate__d * var_chaste_interface__L_type_Ca_channel_f_gate__f / (1.0 - exp(1.8716945411372736 - 0.037433890822745473 * var_chaste_interface__membrane__V))) / mParameters[0]; // millivolt / millisecond
        }
        
        rDY[0] = d_dt_chaste_interface_var_membrane__V;
        rAlphaOrTau[1] = 0.001 * var_time_dependent_potassium_current_x_gate__alpha_x;
        rBetaOrInf[1] = 0.001 * var_time_dependent_potassium_current_x_gate__beta_x;
        rAlphaOrTau[2] = 0.001 * var_fast_sodium_current_m_gate__alpha_m;
        rBetaOrInf[2] = 0.001 * var_fast_sodium_current_m_gate__beta_m;
        rAlphaOrTau[3] = 0.001 * var_fast_sodium_current_h_gate__alpha_h;
        rBetaOrInf[3] = 0.001 * var_fast_sodium_current_h_gate__beta_h;
        rAlphaOrTau[4] = 0.001 * var_L_type_Ca_channel_d_gate__alpha_d * var_L_type_Ca_channel_d_gate__speed_d;
        rBetaOrInf[4] = 0.001 * var_L_type_Ca_channel_d_gate__beta_d * var_L_type_Ca_channel_d_gate__speed_d;
        rAlphaOrTau[5] = 0.001 * var_L_type_Ca_channel_f_gate__alpha_f * var_L_type_Ca_channel_f_gate__speed_f;
        rBetaOrInf[5] = 0.001 * var_L_type_Ca_channel_f_gate__beta_f * var_L_type_Ca_channel_f_gate__speed_f;
        rAlphaOrTau[6] = 0.001 * var_transient_outward_current_s_gate__alpha_s;
        rBetaOrInf[6] = 0.001 * var_transient_outward_current_s_gate__beta_s;
        rAlphaOrTau[7] = 3.0030030030030028;
        rBetaOrInf[7] = 1 / (1.0 + exp(-0.80000000000000004 - 0.20000000000000001 * var_chaste_interface__membrane__V));
        rDY[8] = d_dt_chaste_interface_var_calcium_release__ActFrac;
        rDY[9] = d_dt_chaste_interface_var_calcium_release__ProdFrac;
        rDY[10] = d_dt_chaste_interface_var_intracellular_sodium_concentration__Na_i;
        rDY[11] = d_dt_chaste_interface_var_intracellular_potassium_concentration__K_i;
        rDY[12] = d_dt_chaste_interface_var_intracellular_calcium_concentration__Ca_i;
        rDY[13] = d_dt_chaste_interface_var_intracellular_calcium_concentration__Ca_up;
        rDY[14] = d_dt_chaste_interface_var_intracellular_calcium_concentration__Ca_rel;
        rDY[15] = d_dt_chaste_interface_var_intracellular_calcium_concentration__Ca_Calmod;
        rDY[16] = d_dt_chaste_interface_var_intracellular_calcium_concentration__Ca_Trop;
    }
    void Cellnoble_model_1991FromCellMLRushLarsenOpt::ComputeOneStepExceptVoltage(const std::vector<double> &rDY, const std::vector<double> &rAlphaOrTau, const std::vector<double> &rBetaOrInf)
    {
        std::vector<double>& rY = rGetStateVariables();
        
        {
            const double tau_inv = rAlphaOrTau[1] + rBetaOrInf[1];
            const double y_inf = rAlphaOrTau[1] / tau_inv;
            rY[1] = y_inf + (rY[1] - y_inf)*exp(-mDt*tau_inv);
        }
        {
            const double tau_inv = rAlphaOrTau[2] + rBetaOrInf[2];
            const double y_inf = rAlphaOrTau[2] / tau_inv;
            rY[2] = y_inf + (rY[2] - y_inf)*exp(-mDt*tau_inv);
        }
        {
            const double tau_inv = rAlphaOrTau[3] + rBetaOrInf[3];
            const double y_inf = rAlphaOrTau[3] / tau_inv;
            rY[3] = y_inf + (rY[3] - y_inf)*exp(-mDt*tau_inv);
        }
        {
            const double tau_inv = rAlphaOrTau[4] + rBetaOrInf[4];
            const double y_inf = rAlphaOrTau[4] / tau_inv;
            rY[4] = y_inf + (rY[4] - y_inf)*exp(-mDt*tau_inv);
        }
        {
            const double tau_inv = rAlphaOrTau[5] + rBetaOrInf[5];
            const double y_inf = rAlphaOrTau[5] / tau_inv;
            rY[5] = y_inf + (rY[5] - y_inf)*exp(-mDt*tau_inv);
        }
        {
            const double tau_inv = rAlphaOrTau[6] + rBetaOrInf[6];
            const double y_inf = rAlphaOrTau[6] / tau_inv;
            rY[6] = y_inf + (rY[6] - y_inf)*exp(-mDt*tau_inv);
        }
        rY[7] = rBetaOrInf[7] + (rY[7] - rBetaOrInf[7])*exp(-mDt/rAlphaOrTau[7]);
        rY[8] += mDt * rDY[8];
        rY[9] += mDt * rDY[9];
        rY[10] += mDt * rDY[10];
        rY[11] += mDt * rDY[11];
        rY[12] += mDt * rDY[12];
        rY[13] += mDt * rDY[13];
        rY[14] += mDt * rDY[14];
        rY[15] += mDt * rDY[15];
        rY[16] += mDt * rDY[16];
    }

    std::vector<double> Cellnoble_model_1991FromCellMLRushLarsenOpt::ComputeDerivedQuantities(double var_chaste_interface__environment__time_converted, const std::vector<double> & rY)
    {
        // Inputs:
        // Time units: millisecond
        

        // Mathematics
        const double var_membrane__i_Stim_converted = GetIntracellularAreaStimulus(var_chaste_interface__environment__time_converted); // uA_per_cm2

        std::vector<double> dqs(2);
        dqs[0] = var_chaste_interface__environment__time_converted;
        dqs[1] = var_membrane__i_Stim_converted;
        return dqs;
    }

template<>
void OdeSystemInformation<Cellnoble_model_1991FromCellMLRushLarsenOpt>::Initialise(void)
{
    this->mSystemName = "noble_model_1991";
    this->mFreeVariableName = "environment__time";
    this->mFreeVariableUnits = "millisecond";

    // rY[0]:
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("millivolt");
    this->mInitialConditions.push_back(-93.0);

    // rY[1]:
    this->mVariableNames.push_back("time_dependent_potassium_current_x_gate__x");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.001);

    // rY[2]:
    this->mVariableNames.push_back("fast_sodium_current_m_gate__m");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.000105);

    // rY[3]:
    this->mVariableNames.push_back("fast_sodium_current_h_gate__h");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.99816539);

    // rY[4]:
    this->mVariableNames.push_back("L_type_Ca_channel_d_gate__d");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0);

    // rY[5]:
    this->mVariableNames.push_back("L_type_Ca_channel_f_gate__f");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(1.0);

    // rY[6]:
    this->mVariableNames.push_back("transient_outward_current_s_gate__s");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(1.0);

    // rY[7]:
    this->mVariableNames.push_back("transient_outward_current_r_gate__r");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0);

    // rY[8]:
    this->mVariableNames.push_back("calcium_release__ActFrac");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0);

    // rY[9]:
    this->mVariableNames.push_back("calcium_release__ProdFrac");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0);

    // rY[10]:
    this->mVariableNames.push_back("intracellular_sodium_concentration__Na_i");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(5.0);

    // rY[11]:
    this->mVariableNames.push_back("intracellular_potassium_concentration__K_i");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(140.0);

    // rY[12]:
    this->mVariableNames.push_back("intracellular_calcium_concentration__Ca_i");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(7.63e-06);

    // rY[13]:
    this->mVariableNames.push_back("intracellular_calcium_concentration__Ca_up");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(0.3013);

    // rY[14]:
    this->mVariableNames.push_back("intracellular_calcium_concentration__Ca_rel");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(0.2989);

    // rY[15]:
    this->mVariableNames.push_back("intracellular_calcium_concentration__Ca_Calmod");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(0.0003);

    // rY[16]:
    this->mVariableNames.push_back("intracellular_calcium_concentration__Ca_Trop");
    this->mVariableUnits.push_back("millimolar");
    this->mInitialConditions.push_back(0.0002);

    // mParameters[0]:
    this->mParameterNames.push_back("membrane_capacitance");
    this->mParameterUnits.push_back("microF");

    // Derived Quantity index [0]:
    this->mDerivedQuantityNames.push_back("environment__time");
    this->mDerivedQuantityUnits.push_back("millisecond");

    // Derived Quantity index [1]:
    this->mDerivedQuantityNames.push_back("membrane_stimulus_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    this->mInitialised = true;
}

// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Cellnoble_model_1991FromCellMLRushLarsenOpt)

