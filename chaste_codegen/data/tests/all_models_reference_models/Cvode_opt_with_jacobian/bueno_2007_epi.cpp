#ifdef CHASTE_CVODE
//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: bueno_2007
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: AnalyticCvodeOpt)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "bueno_2007_epi.hpp"
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

class Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables : public AbstractLookupTableCollection
{
public:
    static Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables* Instance()
    {
        if (mpInstance.get() == NULL)
        {
            mpInstance.reset(new Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables);
        }
        return mpInstance.get();
    }

    void FreeMemory()
    {

        mNeedsRegeneration.assign(mNeedsRegeneration.size(), true);
    }

    // Row lookup methods
    // using linear-interpolation



    ~Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables()
    {

    }

protected:
    Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables(const Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables&);
    Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables& operator= (const Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables&);
    Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables()
    {
        assert(mpInstance.get() == NULL);
        mKeyingVariableNames.resize(0);
        mNumberOfTables.resize(0);
        mTableMins.resize(0);
        mTableSteps.resize(0);
        mTableStepInverses.resize(0);
        mTableMaxs.resize(0);
        mNeedsRegeneration.resize(0);

        Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables::RegenerateTables();
    }

    void RegenerateTables()
    {
        AbstractLookupTableCollection::EventHandler::BeginEvent(AbstractLookupTableCollection::EventHandler::GENERATE_TABLES);

        AbstractLookupTableCollection::EventHandler::EndEvent(AbstractLookupTableCollection::EventHandler::GENERATE_TABLES);
    }

private:
    /** The single instance of the class */
    static std::shared_ptr<Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables> mpInstance;

};

std::shared_ptr<Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables> Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables::mpInstance;

    boost::shared_ptr<RegularStimulus> Cellbueno_2007_epiFromCellMLCvodeOpt::UseCellMLDefaultStimulus()
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

    Cellbueno_2007_epiFromCellMLCvodeOpt::Cellbueno_2007_epiFromCellMLCvodeOpt(boost::shared_ptr<AbstractIvpOdeSolver> pOdeSolver /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractCvodeCell(
                pOdeSolver,
                4,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        //
        this->mpSystemInfo = OdeSystemInformation<Cellbueno_2007_epiFromCellMLCvodeOpt>::Instance();
        Init();

        // We have a default stimulus specified in the CellML file metadata
        this->mHasDefaultStimulusFromCellML = true;
        mUseAnalyticJacobian = true;
        mHasAnalyticJacobian = true;
        
        NV_Ith_S(this->mParameters, 0) = 1.0; // (var_membrane__C) [uF_per_cm2]
    }

    Cellbueno_2007_epiFromCellMLCvodeOpt::~Cellbueno_2007_epiFromCellMLCvodeOpt()
    {
    }

    AbstractLookupTableCollection* Cellbueno_2007_epiFromCellMLCvodeOpt::GetLookupTableCollection()
    {
        return Cellbueno_2007_epiFromCellMLCvodeOpt_LookupTables::Instance();
    }
    
    double Cellbueno_2007_epiFromCellMLCvodeOpt::GetIIonic(const std::vector<double>* pStateVariables)
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
        // Units: mV; Initial value: 0.0
        double var_chaste_interface__fast_inward_current_v_gate__v = NV_Ith_S(rY, 1);
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__slow_inward_current_w_gate__w = NV_Ith_S(rY, 2);
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__slow_inward_current_s_gate__s = NV_Ith_S(rY, 3);
        // Units: dimensionless; Initial value: 0.0
        
        const double var_membrane__u = var_chaste_interface__membrane__V; // dimensionless
        const double var_fast_inward_current__i_fi = -9.0909090909090917 * (1.55 - var_membrane__u) * (-0.29999999999999999 + var_membrane__u) * ((var_membrane__u < 0.29999999999999999) ? (0) : (1.0)) * var_chaste_interface__fast_inward_current_v_gate__v; // uA_per_cm2
        const double var_p__p = ((var_membrane__u < 0.13) ? (0) : (1.0)); // dimensionless
        const double var_slow_inward_current__i_si = -0.5298013245033113 * var_p__p * var_chaste_interface__slow_inward_current_s_gate__s * var_chaste_interface__slow_inward_current_w_gate__w; // uA_per_cm2
        const double var_slow_outward_current__i_so = var_p__p / (15.5069 - 14.511200000000001 * tanh(-1.3297699999999999 + 2.0457999999999998 * var_membrane__u)) + (1.0 - var_p__p) * var_membrane__u / (400.0 - 394.0 * ((var_membrane__u < 0.0060000000000000001) ? (0) : (1.0))); // uA_per_cm2
        const double var_chaste_interface__i_ionic = var_fast_inward_current__i_fi + var_slow_inward_current__i_si + var_slow_outward_current__i_so; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        if (made_new_cvode_vector)
        {
            DeleteVector(rY);
        }
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellbueno_2007_epiFromCellMLCvodeOpt::EvaluateYDerivatives(double var_chaste_interface__environment__time, const N_Vector rY, N_Vector rDY)
    {
        // Inputs:
        // Time units: millisecond
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, 0));
        // Units: mV; Initial value: 0.0
        double var_chaste_interface__fast_inward_current_v_gate__v = NV_Ith_S(rY, 1);
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__slow_inward_current_w_gate__w = NV_Ith_S(rY, 2);
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__slow_inward_current_s_gate__s = NV_Ith_S(rY, 3);
        // Units: dimensionless; Initial value: 0.0

        // Mathematics
        double d_dt_chaste_interface_var_membrane__V;
        const double var_membrane__u = var_chaste_interface__membrane__V; // dimensionless
        const double var_m__m = ((var_membrane__u < 0.29999999999999999) ? (0) : (1.0)); // dimensionless
        const double var_p__p = ((var_membrane__u < 0.13) ? (0) : (1.0)); // dimensionless
        const double d_dt_chaste_interface_var_fast_inward_current_v_gate__v = -0.68936991589687036 * var_chaste_interface__fast_inward_current_v_gate__v * var_m__m + (1.0 - var_m__m) * (-var_chaste_interface__fast_inward_current_v_gate__v + ((var_membrane__u < 0.0060000000000000001) ? (1.0) : (0))) / (60.0 + 1090.0 * ((var_membrane__u < 0.0060000000000000001) ? (0) : (1.0))); // 1 / ms
        const double var_r__r = ((var_membrane__u < 0.0060000000000000001) ? (0) : (1.0)); // dimensionless
        const double d_dt_chaste_interface_var_slow_inward_current_s_gate__s = (0.5 - var_chaste_interface__slow_inward_current_s_gate__s + 0.5 * tanh(-1.9077247800000001 + 2.0994000000000002 * var_membrane__u)) / (2.7342 + 13.2658 * var_p__p); // 1 / ms
        const double d_dt_chaste_interface_var_slow_inward_current_w_gate__w = -0.0050000000000000001 * var_r__r * var_chaste_interface__slow_inward_current_w_gate__w + (1.0 - var_r__r) * (-var_chaste_interface__slow_inward_current_w_gate__w + 0.93999999999999995 * var_r__r + (1.0 - var_r__r) * (1.0 - 14.285714285714285 * var_membrane__u)) / (37.5 - 22.5 * tanh(-1.95 + 65.0 * var_membrane__u)); // 1 / ms

        if (mSetVoltageDerivativeToZero)
        {
            d_dt_chaste_interface_var_membrane__V = 0.0;
        }
        else
        {
            d_dt_chaste_interface_var_membrane__V = -(var_p__p / (15.5069 - 14.511200000000001 * tanh(-1.3297699999999999 + 2.0457999999999998 * var_membrane__u)) + (1.0 - var_p__p) * var_membrane__u / (400.0 - 394.0 * var_r__r) - 0.5298013245033113 * var_p__p * var_chaste_interface__slow_inward_current_s_gate__s * var_chaste_interface__slow_inward_current_w_gate__w - 9.0909090909090917 * (1.55 - var_membrane__u) * (-0.29999999999999999 + var_membrane__u) * var_chaste_interface__fast_inward_current_v_gate__v * var_m__m + GetIntracellularAreaStimulus(var_chaste_interface__environment__time)) / NV_Ith_S(mParameters, 0); // mV / ms
        }
        
        NV_Ith_S(rDY,0) = d_dt_chaste_interface_var_membrane__V;
        NV_Ith_S(rDY,1) = d_dt_chaste_interface_var_fast_inward_current_v_gate__v;
        NV_Ith_S(rDY,2) = d_dt_chaste_interface_var_slow_inward_current_w_gate__w;
        NV_Ith_S(rDY,3) = d_dt_chaste_interface_var_slow_inward_current_s_gate__s;
    }

    void Cellbueno_2007_epiFromCellMLCvodeOpt::EvaluateAnalyticJacobian(double var_chaste_interface__environment__time, N_Vector rY, N_Vector rDY, CHASTE_CVODE_DENSE_MATRIX rJacobian, N_Vector rTmp1, N_Vector rTmp2, N_Vector rTmp3)
    {
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, 0));
        // Units: mV; Initial value: 0.0
        double var_chaste_interface__fast_inward_current_v_gate__v = NV_Ith_S(rY, 1);
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__slow_inward_current_w_gate__w = NV_Ith_S(rY, 2);
        // Units: dimensionless; Initial value: 1.0
        double var_chaste_interface__slow_inward_current_s_gate__s = NV_Ith_S(rY, 3);
        // Units: dimensionless; Initial value: 0.0
        const double var_x0 = var_chaste_interface__membrane__V;
        const double var_x1 = ((var_x0 < 0.0060000000000000001) ? (0) : (1.0));
        const double var_x2 = ((var_x0 < 0.13) ? (0) : (1.0));
        const double var_x3 = 9.0909090909090917 * var_chaste_interface__membrane__V;
        const double var_x4 = var_x0 < 0.29999999999999999;
        const double var_x5 = ((var_x4) ? (0) : (1.0));
        const double var_x6 = var_x5 * var_chaste_interface__fast_inward_current_v_gate__v;
        const double var_x7 = -14.090909090909092 + var_x3;
        const double var_x8 = tanh(-1.3297699999999999 + 2.0457999999999998 * var_chaste_interface__membrane__V);
        const double var_x9 = 1 / NV_Ith_S(mParameters, 0);
        const double var_x10 = var_x9;
        const double var_x11 = 0.5298013245033113 * var_x2 * var_x9;
        const double var_x12 = tanh(-1.95 + 65.0 * var_chaste_interface__membrane__V);
        const double var_x13 = 1.0 - var_x1;
        const double var_x14 = var_x13 / (37.5 - 22.5 * var_x12);
        const double var_x15 = 1 / (2.7342 + 13.2658 * var_x2);
        
        // Matrix entries
        IJth(rJacobian, 0, 0) = mSetVoltageDerivativeToZero ? 0.0 : (-var_x10 * (var_x6 * var_x7 + var_x6 * (-2.7272727272727271 + var_x3) + (1.0 - var_x2) / (400.0 - 394.0 * var_x1) + 0.0041586275611754688 * var_x2 * (29.687012959999997 - 29.687012959999997 * pow(var_x8, 2)) / pow((1 - 0.93578987418504023 * var_x8), 2)));
        IJth(rJacobian, 2, 0) = var_x14 * (-14.285714285714285 + 14.285714285714285 * var_x1) + 0.00071111111111111115 * var_x13 * (1462.5 - 1462.5 * pow(var_x12, 2)) * (-var_chaste_interface__slow_inward_current_w_gate__w + 0.93999999999999995 * var_x1 + var_x13 * (1.0 - 14.285714285714285 * var_chaste_interface__membrane__V)) / pow((1 - 0.59999999999999998 * var_x12), 2);
        IJth(rJacobian, 3, 0) = var_x15 * (1.0497000000000001 - 1.0497000000000001 * pow(tanh(-1.9077247800000001 + 2.0994000000000002 * var_chaste_interface__membrane__V), 2));
        IJth(rJacobian, 0, 1) = mSetVoltageDerivativeToZero ? 0.0 : (-var_x10 * var_x5 * var_x7 * (-0.29999999999999999 + var_x0));
        IJth(rJacobian, 1, 1) = ((var_chaste_interface__membrane__V < 0.0060000000000000001) ? (-0.016666666666666666) : ((var_x4) ? (-0.00086956521739130438) : (-0.68936991589687036)));
        IJth(rJacobian, 0, 2) = mSetVoltageDerivativeToZero ? 0.0 : (var_x11 * var_chaste_interface__slow_inward_current_s_gate__s);
        IJth(rJacobian, 2, 2) = -var_x14 - 0.0050000000000000001 * var_x1;
        IJth(rJacobian, 0, 3) = mSetVoltageDerivativeToZero ? 0.0 : (var_x11 * var_chaste_interface__slow_inward_current_w_gate__w);
        IJth(rJacobian, 3, 3) = -var_x15;
    }

    N_Vector Cellbueno_2007_epiFromCellMLCvodeOpt::ComputeDerivedQuantities(double var_chaste_interface__environment__time, const N_Vector & rY)
    {
        // Inputs:
        // Time units: millisecond
        
        // Mathematics
        const double var_membrane__i_stim = GetIntracellularAreaStimulus(var_chaste_interface__environment__time); // uA_per_cm2

        N_Vector dqs = N_VNew_Serial(2);
        NV_Ith_S(dqs, 0) = var_membrane__i_stim;
        NV_Ith_S(dqs, 1) = var_chaste_interface__environment__time;
        return dqs;
    }

template<>
void OdeSystemInformation<Cellbueno_2007_epiFromCellMLCvodeOpt>::Initialise(void)
{
    this->mSystemName = "bueno_2007";
    this->mFreeVariableName = "time";
    this->mFreeVariableUnits = "ms";

    // NV_Ith_S(rY, 0):
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("mV");
    this->mInitialConditions.push_back(0.0);

    // NV_Ith_S(rY, 1):
    this->mVariableNames.push_back("fast_inward_current_v_gate__v");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(1.0);

    // NV_Ith_S(rY, 2):
    this->mVariableNames.push_back("slow_inward_current_w_gate__w");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(1.0);

    // NV_Ith_S(rY, 3):
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
CHASTE_CLASS_EXPORT(Cellbueno_2007_epiFromCellMLCvodeOpt)

#endif // CHASTE_CVODE
