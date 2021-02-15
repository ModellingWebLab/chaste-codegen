//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: bueno_2007
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: Normal)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "bueno_2007_endo.hpp"
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


    boost::shared_ptr<RegularStimulus> Cellbueno_2007_endoFromCellML::UseCellMLDefaultStimulus()
    {
        // Use the default stimulus specified by CellML metadata
        const double var_chaste_interface__membrane__IstimAmplitude = -0.5; // uA_per_cm2
        const double var_chaste_interface__membrane__IstimPeriod = 1000.0; // ms
        const double var_chaste_interface__membrane__IstimPulseDuration = 1.0; // ms
        const double var_chaste_interface__membrane__IstimStart = 10.0; // ms
        boost::shared_ptr<RegularStimulus> p_cellml_stim(new RegularStimulus(
                -fabs(var_chaste_interface__membrane__IstimAmplitude),
                var_chaste_interface__membrane__IstimPulseDuration,
                var_chaste_interface__membrane__IstimPeriod,
                var_chaste_interface__membrane__IstimStart
                ));
        mpIntracellularStimulus = p_cellml_stim;
        return p_cellml_stim;
    }

    Cellbueno_2007_endoFromCellML::Cellbueno_2007_endoFromCellML(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractCardiacCell(
                pSolver,
                4,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        //
        this->mpSystemInfo = OdeSystemInformation<Cellbueno_2007_endoFromCellML>::Instance();
        Init();

        // We have a default stimulus specified in the CellML file metadata
        this->mHasDefaultStimulusFromCellML = true;
        
        this->mParameters[0] = 1.0; // (var_membrane__C) [uF_per_cm2]
    }

    Cellbueno_2007_endoFromCellML::~Cellbueno_2007_endoFromCellML()
    {
    }

    
    double Cellbueno_2007_endoFromCellML::GetIIonic(const std::vector<double>* pStateVariables)
    {
        // For state variable interpolation (SVI) we read in interpolated state variables,
        // otherwise for ionic current interpolation (ICI) we use the state variables of this model (node).
        if (!pStateVariables) pStateVariables = &rGetStateVariables();
        const std::vector<double>& rY = *pStateVariables;
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: mV; Initial value: 0.0
        double var_chaste_interface__fast_inward_current_v_gate__v = rY[1];
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__slow_inward_current_w_gate__w = rY[2];
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__slow_inward_current_s_gate__s = rY[3];
        // Units: dimensionless; Initial value: 0.0
        
        const double var_fast_inward_current__tau_fi = 0.104; // cm2_per_uA
        const double var_fast_inward_current__u_u = 1.5600000000000001; // dimensionless
        const double var_m__u_m = 0.29999999999999999; // dimensionless
        const double var_membrane__alpha = 1.0; // per_mV
        const double var_membrane__u = var_chaste_interface__membrane__V * var_membrane__alpha; // dimensionless
        const double var_m__m = ((var_m__u_m > var_membrane__u) ? (0) : (1.0)); // dimensionless
        const double var_fast_inward_current__i_fi = -(-var_m__u_m + var_membrane__u) * (-var_membrane__u + var_fast_inward_current__u_u) * var_chaste_interface__fast_inward_current_v_gate__v * var_m__m / var_fast_inward_current__tau_fi; // uA_per_cm2
        const double var_p__u_p = 0.13; // dimensionless
        const double var_p__p = ((var_membrane__u < var_p__u_p) ? (0) : (1.0)); // dimensionless
        const double var_r__u_r = 0.0060000000000000001; // dimensionless
        const double var_r__r = ((var_membrane__u < var_r__u_r) ? (0) : (1.0)); // dimensionless
        const double var_slow_inward_current__tau_si = 2.9013; // cm2_per_uA
        const double var_slow_inward_current__i_si = -var_p__p * var_chaste_interface__slow_inward_current_s_gate__s * var_chaste_interface__slow_inward_current_w_gate__w / var_slow_inward_current__tau_si; // uA_per_cm2
        const double var_slow_outward_current__k_so = 2.0; // dimensionless
        const double var_slow_outward_current__tau_o1 = 470.0; // cm2_per_uA
        const double var_slow_outward_current__tau_o2 = 6.0; // cm2_per_uA
        const double var_slow_outward_current__tau_o = (1.0 - var_r__r) * var_slow_outward_current__tau_o1 + var_r__r * var_slow_outward_current__tau_o2; // cm2_per_uA
        const double var_slow_outward_current__tau_so1 = 40.0; // cm2_per_uA
        const double var_slow_outward_current__tau_so2 = 1.2; // cm2_per_uA
        const double var_slow_outward_current__u_so = 0.65000000000000002; // dimensionless
        const double var_slow_outward_current__tau_so = 0.5 * (1.0 + tanh((-var_slow_outward_current__u_so + var_membrane__u) * var_slow_outward_current__k_so)) * (-var_slow_outward_current__tau_so1 + var_slow_outward_current__tau_so2) + var_slow_outward_current__tau_so1; // cm2_per_uA
        const double var_slow_outward_current__i_so = var_p__p / var_slow_outward_current__tau_so + (1.0 - var_p__p) * var_membrane__u / var_slow_outward_current__tau_o; // uA_per_cm2
        const double var_chaste_interface__i_ionic = var_fast_inward_current__i_fi + var_slow_inward_current__i_si + var_slow_outward_current__i_so; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellbueno_2007_endoFromCellML::EvaluateYDerivatives(double var_chaste_interface__environment__time, const std::vector<double>& rY, std::vector<double>& rDY)
    {
        // Inputs:
        // Time units: millisecond
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: mV; Initial value: 0.0
        double var_chaste_interface__fast_inward_current_v_gate__v = rY[1];
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__slow_inward_current_w_gate__w = rY[2];
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__slow_inward_current_s_gate__s = rY[3];
        // Units: dimensionless; Initial value: 0.0

        // Mathematics
        double d_dt_chaste_interface_var_membrane__V;
        const double var_fast_inward_current_v_gate__tau_v1_minus = 75.0; // ms
        const double var_fast_inward_current_v_gate__tau_v2_minus = 10.0; // ms
        const double var_fast_inward_current_v_gate__tau_v_plus = 1.4505999999999999; // ms
        const double var_m__u_m = 0.29999999999999999; // dimensionless
        const double var_membrane__alpha = 1.0; // per_mV
        const double var_membrane__u = var_chaste_interface__membrane__V * var_membrane__alpha; // dimensionless
        const double var_m__m = ((var_m__u_m > var_membrane__u) ? (0) : (1.0)); // dimensionless
        const double var_p__u_p = 0.13; // dimensionless
        const double var_p__p = ((var_membrane__u < var_p__u_p) ? (0) : (1.0)); // dimensionless
        const double var_q__u_q = 0.024; // dimensionless
        const double var_fast_inward_current_v_gate__v_inf = ((var_membrane__u < var_q__u_q) ? (1.0) : (0)); // dimensionless
        const double var_q__q = ((var_membrane__u < var_q__u_q) ? (0) : (1.0)); // dimensionless
        const double var_fast_inward_current_v_gate__tau_v_minus = (1.0 - var_q__q) * var_fast_inward_current_v_gate__tau_v1_minus + var_fast_inward_current_v_gate__tau_v2_minus * var_q__q; // ms
        const double d_dt_chaste_interface_var_fast_inward_current_v_gate__v = (1.0 - var_m__m) * (-var_chaste_interface__fast_inward_current_v_gate__v + var_fast_inward_current_v_gate__v_inf) / var_fast_inward_current_v_gate__tau_v_minus - var_chaste_interface__fast_inward_current_v_gate__v * var_m__m / var_fast_inward_current_v_gate__tau_v_plus; // 1 / ms
        const double var_r__u_r = 0.0060000000000000001; // dimensionless
        const double var_r__r = ((var_membrane__u < var_r__u_r) ? (0) : (1.0)); // dimensionless
        const double var_slow_inward_current_s_gate__k_s = 2.0994000000000002; // dimensionless
        const double var_slow_inward_current_s_gate__tau_s1 = 2.7342; // ms
        const double var_slow_inward_current_s_gate__tau_s2 = 2.0; // ms
        const double var_slow_inward_current_s_gate__tau_s = (1.0 - var_p__p) * var_slow_inward_current_s_gate__tau_s1 + var_p__p * var_slow_inward_current_s_gate__tau_s2; // ms
        const double var_slow_inward_current_s_gate__u_s = 0.90869999999999995; // dimensionless
        const double d_dt_chaste_interface_var_slow_inward_current_s_gate__s = (0.5 - var_chaste_interface__slow_inward_current_s_gate__s + 0.5 * tanh((-var_slow_inward_current_s_gate__u_s + var_membrane__u) * var_slow_inward_current_s_gate__k_s)) / var_slow_inward_current_s_gate__tau_s; // 1 / ms
        const double var_slow_inward_current_w_gate__k_w_minus = 200.0; // dimensionless
        const double var_slow_inward_current_w_gate__tau_w1_minus = 6.0; // ms
        const double var_slow_inward_current_w_gate__tau_w2_minus = 140.0; // ms
        const double var_slow_inward_current_w_gate__tau_w_plus = 280.0; // ms
        const double var_slow_inward_current_w_gate__tau_winf = 0.027300000000000001; // ms
        const double var_slow_inward_current_w_gate__u_w_minus = 0.016; // dimensionless
        const double var_slow_inward_current_w_gate__tau_w_minus = 0.5 * (1.0 + tanh((-var_slow_inward_current_w_gate__u_w_minus + var_membrane__u) * var_slow_inward_current_w_gate__k_w_minus)) * (-var_slow_inward_current_w_gate__tau_w1_minus + var_slow_inward_current_w_gate__tau_w2_minus) + var_slow_inward_current_w_gate__tau_w1_minus; // ms
        const double var_slow_inward_current_w_gate__wstar_inf = 0.78000000000000003; // dimensionless
        const double var_slow_inward_current_w_gate__w_inf = (1.0 - var_r__r) * (1.0 - var_membrane__u / var_slow_inward_current_w_gate__tau_winf) + var_r__r * var_slow_inward_current_w_gate__wstar_inf; // dimensionless
        const double d_dt_chaste_interface_var_slow_inward_current_w_gate__w = (1.0 - var_r__r) * (-var_chaste_interface__slow_inward_current_w_gate__w + var_slow_inward_current_w_gate__w_inf) / var_slow_inward_current_w_gate__tau_w_minus - var_r__r * var_chaste_interface__slow_inward_current_w_gate__w / var_slow_inward_current_w_gate__tau_w_plus; // 1 / ms

        if (mSetVoltageDerivativeToZero)
        {
            d_dt_chaste_interface_var_membrane__V = 0.0;
        }
        else
        {
            const double var_fast_inward_current__tau_fi = 0.104; // cm2_per_uA
            const double var_fast_inward_current__u_u = 1.5600000000000001; // dimensionless
            const double var_membrane__i_stim = GetIntracellularAreaStimulus(var_chaste_interface__environment__time); // uA_per_cm2
            const double var_fast_inward_current__i_fi = -(-var_m__u_m + var_membrane__u) * (-var_membrane__u + var_fast_inward_current__u_u) * var_chaste_interface__fast_inward_current_v_gate__v * var_m__m / var_fast_inward_current__tau_fi; // uA_per_cm2
            const double var_slow_inward_current__tau_si = 2.9013; // cm2_per_uA
            const double var_slow_inward_current__i_si = -var_p__p * var_chaste_interface__slow_inward_current_s_gate__s * var_chaste_interface__slow_inward_current_w_gate__w / var_slow_inward_current__tau_si; // uA_per_cm2
            const double var_slow_outward_current__k_so = 2.0; // dimensionless
            const double var_slow_outward_current__tau_o1 = 470.0; // cm2_per_uA
            const double var_slow_outward_current__tau_o2 = 6.0; // cm2_per_uA
            const double var_slow_outward_current__tau_o = (1.0 - var_r__r) * var_slow_outward_current__tau_o1 + var_r__r * var_slow_outward_current__tau_o2; // cm2_per_uA
            const double var_slow_outward_current__tau_so1 = 40.0; // cm2_per_uA
            const double var_slow_outward_current__tau_so2 = 1.2; // cm2_per_uA
            const double var_slow_outward_current__u_so = 0.65000000000000002; // dimensionless
            const double var_slow_outward_current__tau_so = 0.5 * (1.0 + tanh((-var_slow_outward_current__u_so + var_membrane__u) * var_slow_outward_current__k_so)) * (-var_slow_outward_current__tau_so1 + var_slow_outward_current__tau_so2) + var_slow_outward_current__tau_so1; // cm2_per_uA
            const double var_slow_outward_current__i_so = var_p__p / var_slow_outward_current__tau_so + (1.0 - var_p__p) * var_membrane__u / var_slow_outward_current__tau_o; // uA_per_cm2
            d_dt_chaste_interface_var_membrane__V = -(var_fast_inward_current__i_fi + var_membrane__i_stim + var_slow_inward_current__i_si + var_slow_outward_current__i_so) / mParameters[0]; // mV / ms
        }
        
        rDY[0] = d_dt_chaste_interface_var_membrane__V;
        rDY[1] = d_dt_chaste_interface_var_fast_inward_current_v_gate__v;
        rDY[2] = d_dt_chaste_interface_var_slow_inward_current_w_gate__w;
        rDY[3] = d_dt_chaste_interface_var_slow_inward_current_s_gate__s;
    }

    std::vector<double> Cellbueno_2007_endoFromCellML::ComputeDerivedQuantities(double var_chaste_interface__environment__time, const std::vector<double> & rY)
    {
        // Inputs:
        // Time units: millisecond
        
        // Mathematics
        const double var_membrane__i_stim = GetIntracellularAreaStimulus(var_chaste_interface__environment__time); // uA_per_cm2

        std::vector<double> dqs(2);
        dqs[0] = var_membrane__i_stim;
        dqs[1] = var_chaste_interface__environment__time;
        return dqs;
    }

template<>
void OdeSystemInformation<Cellbueno_2007_endoFromCellML>::Initialise(void)
{
    this->mSystemName = "bueno_2007";
    this->mFreeVariableName = "time";
    this->mFreeVariableUnits = "ms";

    // rY[0]:
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("mV");
    this->mInitialConditions.push_back(0.0);

    // rY[1]:
    this->mVariableNames.push_back("fast_inward_current_v_gate__v");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(1.0);

    // rY[2]:
    this->mVariableNames.push_back("slow_inward_current_w_gate__w");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(1.0);

    // rY[3]:
    this->mVariableNames.push_back("slow_inward_current_s_gate__s");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0);

    // mParameters[0]:
    this->mParameterNames.push_back("membrane_capacitance");
    this->mParameterUnits.push_back("uF_per_cm2");

    // Derived Quantity index [0]:
    this->mDerivedQuantityNames.push_back("membrane_stimulus_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [1]:
    this->mDerivedQuantityNames.push_back("time");
    this->mDerivedQuantityUnits.push_back("ms");

    this->mInitialised = true;
}

// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Cellbueno_2007_endoFromCellML)

