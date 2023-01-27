#ifdef CHASTE_CVODE
//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: hodgkin_huxley_squid_axon_model_1952_modified
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: CvodeCellWithDataClampOpt)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "hodgkin_huxley_squid_axon_model_1952_modified.hpp"
#include <cmath>
#include <cfloat>
#include <cassert>
#include <memory>
#include "Exception.hpp"
#include "OdeSystemInformation.hpp"
#include "RegularStimulus.hpp"
#include "HeartConfig.hpp"
#include "IsNan.hpp"
#include "MathsCustomFunctions.hpp"

#if CHASTE_SUNDIALS_VERSION >= 60000
#include "CvodeContextManager.hpp"
#endif



class Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables : public AbstractLookupTableCollection
{
public:
    static Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables* Instance()
    {
        if (mpInstance.get() == NULL)
        {
            mpInstance.reset(new Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables);
        }
        return mpInstance.get();
    }

    void FreeMemory()
    {

        if (_lookup_table_0)
        {
            delete[] _lookup_table_0;
            _lookup_table_0 = NULL;
        }

        mNeedsRegeneration.assign(mNeedsRegeneration.size(), true);
    }

    // Row lookup methods
    // using linear-interpolation

    double* _lookup_0_row(unsigned i, double _factor_)
    {
        for (unsigned j=0; j<6; j++)
        {
            const double y1 = _lookup_table_0[i][j];
            const double y2 = _lookup_table_0[i+1][j];
            _lookup_table_0_row[j] = y1 + (y2-y1)*_factor_;
        }
        return _lookup_table_0_row;
    }


    const double * IndexTable0(double var_chaste_interface__membrane__V)
    {
        const double _offset_0 = var_chaste_interface__membrane__V - mTableMins[0];
        const double _offset_0_over_table_step = _offset_0 * mTableStepInverses[0];
        const unsigned _table_index_0 = (unsigned)(_offset_0_over_table_step);
        const double _factor_0 = _offset_0_over_table_step - _table_index_0;
        const double* const _lt_0_row = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables::Instance()->_lookup_0_row(_table_index_0, _factor_0);
        return _lt_0_row;
    }


// LCOV_EXCL_START
    bool CheckIndex0(double& var_chaste_interface__membrane__V)
    {
        bool _oob_0 = false;
        if (var_chaste_interface__membrane__V>mTableMaxs[0] || var_chaste_interface__membrane__V<mTableMins[0])
        {
// LCOV_EXCL_START
            _oob_0 = true;
// LCOV_EXCL_STOP
        }
        return _oob_0;
    }
// LCOV_EXCL_STOP

    ~Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables()
    {

        if (_lookup_table_0)
        {
            delete[] _lookup_table_0;
            _lookup_table_0 = NULL;
        }

    }

protected:
    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables(const Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables&);
    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables& operator= (const Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables&);
    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables()
    {
        assert(mpInstance.get() == NULL);
        mKeyingVariableNames.resize(1);
        mNumberOfTables.resize(1);
        mTableMins.resize(1);
        mTableSteps.resize(1);
        mTableStepInverses.resize(1);
        mTableMaxs.resize(1);
        mNeedsRegeneration.resize(1);

        mKeyingVariableNames[0] = "membrane_voltage";
        mNumberOfTables[0] = 6;
        mTableMins[0] = -250.0;
        mTableMaxs[0] = 550.0;
        mTableSteps[0] = 0.001;
        mTableStepInverses[0] = 1000.0;
        mNeedsRegeneration[0] = true;
        _lookup_table_0 = NULL;

        Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables::RegenerateTables();
    }

    void RegenerateTables()
    {
        AbstractLookupTableCollection::EventHandler::BeginEvent(AbstractLookupTableCollection::EventHandler::GENERATE_TABLES);


        if (mNeedsRegeneration[0])
        {
            if (_lookup_table_0)
            {
                delete[] _lookup_table_0;
                _lookup_table_0 = NULL;
            }
            const unsigned _table_size_0 = 1 + (unsigned)((mTableMaxs[0]-mTableMins[0])/mTableSteps[0]+0.5);
            _lookup_table_0 = new double[_table_size_0][6];

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                auto f = [](double var_chaste_interface__membrane__V) {
                    return (((6.5 + 0.10000000000000001 * var_chaste_interface__membrane__V >= -9.9999999999999995e-8) && (6.5 + 0.10000000000000001 * var_chaste_interface__membrane__V <= 9.9999999999999995e-8)) ? (0.42499999999999999 + 0.0050000000000000001 * var_chaste_interface__membrane__V) : (-0.099999999999999992 * (6.5 + 0.10000000000000001 * var_chaste_interface__membrane__V) / (-1 + exp(-6.5 - 0.10000000000000001 * var_chaste_interface__membrane__V))));
                };
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = f(var_chaste_interface__membrane__V);
                //Expressions which are part of a piecewise could be inf / nan, this is generally accptable, due to the piecewise, however occasionally interpolation of the lookup table from a nan/inf version can give problems.
                //To avoid this values stored in the table are intrpolated. Occurances of this to at most 2 per expression.
                if (!std::isfinite(val) && _lookup_table_0_num_misshit_piecewise[0] < 2){
                    double left = f(var_chaste_interface__membrane__V - mTableSteps[0]);
                    double right = f(var_chaste_interface__membrane__V + mTableSteps[0]);
                    val = (left + right) / 2.0;
                   // count and limit number of misshits
                  _lookup_table_0_num_misshit_piecewise[0] +=1;
                }
                else if (!std::isfinite(val) && _lookup_table_0_num_misshit_piecewise[0] >= 2){
                    EXCEPTION("Lookup table 0 at ["<<i<<"][0] has non-finite value: " << val);
                }
                _lookup_table_0[i][0] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                auto f = [](double var_chaste_interface__membrane__V) {
                    return exp(0.9375 + 0.012500000000000001 * var_chaste_interface__membrane__V);
                };
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = f(var_chaste_interface__membrane__V);

                _lookup_table_0[i][1] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                auto f = [](double var_chaste_interface__membrane__V) {
                    return exp(-3.75 - 0.050000000000000003 * var_chaste_interface__membrane__V);
                };
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = f(var_chaste_interface__membrane__V);

                _lookup_table_0[i][2] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                auto f = [](double var_chaste_interface__membrane__V) {
                    return 1 + exp(-4.5 - 0.10000000000000001 * var_chaste_interface__membrane__V);
                };
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = f(var_chaste_interface__membrane__V);

                _lookup_table_0[i][3] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                auto f = [](double var_chaste_interface__membrane__V) {
                    return (((5 + 0.10000000000000001 * var_chaste_interface__membrane__V >= -9.9999999999999995e-8) && (5 + 0.10000000000000001 * var_chaste_interface__membrane__V <= 9.9999999999999995e-8)) ? (3.5 + 0.050000000000000003 * var_chaste_interface__membrane__V) : (-(5 + 0.10000000000000001 * var_chaste_interface__membrane__V) / (-1 + exp(-5 - 0.10000000000000001 * var_chaste_interface__membrane__V))));
                };
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = f(var_chaste_interface__membrane__V);
                //Expressions which are part of a piecewise could be inf / nan, this is generally accptable, due to the piecewise, however occasionally interpolation of the lookup table from a nan/inf version can give problems.
                //To avoid this values stored in the table are intrpolated. Occurances of this to at most 2 per expression.
                if (!std::isfinite(val) && _lookup_table_0_num_misshit_piecewise[4] < 2){
                    double left = f(var_chaste_interface__membrane__V - mTableSteps[0]);
                    double right = f(var_chaste_interface__membrane__V + mTableSteps[0]);
                    val = (left + right) / 2.0;
                   // count and limit number of misshits
                  _lookup_table_0_num_misshit_piecewise[4] +=1;
                }
                else if (!std::isfinite(val) && _lookup_table_0_num_misshit_piecewise[4] >= 2){
                    EXCEPTION("Lookup table 4 at ["<<i<<"][4] has non-finite value: " << val);
                }
                _lookup_table_0[i][4] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                auto f = [](double var_chaste_interface__membrane__V) {
                    return exp(-4.166666666666667 - 0.055555555555555552 * var_chaste_interface__membrane__V);
                };
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = f(var_chaste_interface__membrane__V);

                _lookup_table_0[i][5] = val;
            }

            mNeedsRegeneration[0] = false;
        }

        AbstractLookupTableCollection::EventHandler::EndEvent(AbstractLookupTableCollection::EventHandler::GENERATE_TABLES);
    }

private:
    /** The single instance of the class */
    static std::shared_ptr<Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables> mpInstance;

    // Row lookup methods memory
    double _lookup_table_0_row[6];

    // Lookup tables
    double (*_lookup_table_0)[6];
    int _lookup_table_0_num_misshit_piecewise[6] = {0};

};

std::shared_ptr<Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables> Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables::mpInstance;


    boost::shared_ptr<RegularStimulus> Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt::UseCellMLDefaultStimulus()
    {
        // Use the default stimulus specified by CellML metadata
        const double var_chaste_interface__membrane__stim_amplitude = -20; // microA_per_cm2
        const double var_chaste_interface__membrane__stim_duration = 0.5; // millisecond
        const double var_chaste_interface__membrane__stim_period = 1000; // millisecond
        const double var_chaste_interface__membrane__stim_start = 10; // millisecond
        boost::shared_ptr<RegularStimulus> p_cellml_stim(new RegularStimulus(
                -fabs(var_chaste_interface__membrane__stim_amplitude),
                var_chaste_interface__membrane__stim_duration,
                var_chaste_interface__membrane__stim_period,
                var_chaste_interface__membrane__stim_start
                ));
        mpIntracellularStimulus = p_cellml_stim;
        return p_cellml_stim;
    }

    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt::Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt(boost::shared_ptr<AbstractIvpOdeSolver> pOdeSolver /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractCvodeCellWithDataClamp(
                pOdeSolver,
                4,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        //
        this->mpSystemInfo = OdeSystemInformation<Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt>::Instance();
        Init();

        // We have a default stimulus specified in the CellML file metadata
        this->mHasDefaultStimulusFromCellML = true;
        
        NV_Ith_S(this->mParameters, 0) = 1; // (var_membrane__Cm) [microF_per_cm2]
        NV_Ith_S(this->mParameters, 1) = 0; // (var_membrane_data_clamp_current_conductance) [dimensionless]
        NV_Ith_S(this->mParameters, 2) = 120; // (var_sodium_channel__g_Na) [milliS_per_cm2]
        NV_Ith_S(this->mParameters, 3) = 0.29999999999999999; // (var_leakage_current__g_L) [milliS_per_cm2]
        NV_Ith_S(this->mParameters, 4) = 36; // (var_potassium_channel__g_K) [milliS_per_cm2]
    }

    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt::~Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt()
    {
    }

    AbstractLookupTableCollection* Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt::GetLookupTableCollection()
    {
        return Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables::Instance();
    }

    void Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt::VerifyStateVariables()
    {
        
        const double tol = 100*this->mAbsTol;
        N_Vector rY = rGetStateVariables();
        std::string error_message = "";
        
        for (unsigned i=0; i < 4; i++)
        {
            if(std::isnan(NV_Ith_S(rY, i))){
                error_message += "State variable " + this->rGetStateVariableNames()[i] + " is not a number\n";
            }
            if(std::isinf(NV_Ith_S(rY, i))){
                error_message += "State variable " + this->rGetStateVariableNames()[i] + " has become INFINITE\n";
            }
            if(this->is_concentration[i] && NV_Ith_S(rY, i) < -tol)
            {
                error_message += "Concentration " + this->rGetStateVariableNames()[i] + " below 0\n";
            }
            if(this->is_probability[i] && NV_Ith_S(rY, i) < -tol)
            {
                error_message += "Probability " + this->rGetStateVariableNames()[i] + " below 0\n";
            }
            if(this->is_probability[i] && NV_Ith_S(rY, i) > 1 + tol)
            {
                error_message += "Probability " + this->rGetStateVariableNames()[i] + " above 1\n";
            }
        }
        if (error_message != ""){
            EXCEPTION(DumpState(error_message));
        }
    }

    double Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt::GetIIonic(const std::vector<double>* pStateVariables)
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
        

        const double var_leakage_current__i_L = (64.387 + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 3); // microA_per_cm2
        const double var_potassium_channel__i_K = pow(var_chaste_interface__potassium_channel_n_gate__n, 4) * (87 + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 4); // microA_per_cm2
        const double var_sodium_channel__i_Na = pow(var_chaste_interface__sodium_channel_m_gate__m, 3) * (-40 + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 2) * var_chaste_interface__sodium_channel_h_gate__h; // microA_per_cm2
        const double var_chaste_interface__i_ionic = var_leakage_current__i_L + var_potassium_channel__i_K + var_sodium_channel__i_Na; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        if (made_new_cvode_vector)
        {
            DeleteVector(rY);
        }
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt::EvaluateYDerivatives(double var_chaste_interface__environment__time, const N_Vector rY, N_Vector rDY)
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

        // Lookup table indexing
        const bool _oob_0 = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY , var_chaste_interface__environment__time));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

        // Mathematics
        double d_dt_chaste_interface_var_membrane__V;
        const double d_dt_chaste_interface_var_potassium_channel_n_gate__n = (1 - var_chaste_interface__potassium_channel_n_gate__n) * _lt_0_row[0] - 0.125 * var_chaste_interface__potassium_channel_n_gate__n * _lt_0_row[1]; // 1 / millisecond
        const double d_dt_chaste_interface_var_sodium_channel_h_gate__h = 0.070000000000000007 * (1 - var_chaste_interface__sodium_channel_h_gate__h) * _lt_0_row[2] - var_chaste_interface__sodium_channel_h_gate__h / (_lt_0_row[3]); // 1 / millisecond
        const double d_dt_chaste_interface_var_sodium_channel_m_gate__m = (1 - var_chaste_interface__sodium_channel_m_gate__m) * _lt_0_row[4] - 4 * var_chaste_interface__sodium_channel_m_gate__m * _lt_0_row[5]; // 1 / millisecond

        if (mSetVoltageDerivativeToZero)
        {
            d_dt_chaste_interface_var_membrane__V = 0.0;
        }
        else
        {
            d_dt_chaste_interface_var_membrane__V = (-GetIntracellularAreaStimulus(var_chaste_interface__environment__time) - (64.387 + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 3) - (-GetExperimentalVoltageAtTimeT(var_chaste_interface__environment__time) + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 1) - pow(var_chaste_interface__potassium_channel_n_gate__n, 4) * (87 + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 4) - pow(var_chaste_interface__sodium_channel_m_gate__m, 3) * (-40 + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 2) * var_chaste_interface__sodium_channel_h_gate__h) / NV_Ith_S(mParameters, 0); // millivolt / millisecond
        }
        
        NV_Ith_S(rDY,0) = d_dt_chaste_interface_var_membrane__V;
        NV_Ith_S(rDY,1) = d_dt_chaste_interface_var_sodium_channel_m_gate__m;
        NV_Ith_S(rDY,2) = d_dt_chaste_interface_var_sodium_channel_h_gate__h;
        NV_Ith_S(rDY,3) = d_dt_chaste_interface_var_potassium_channel_n_gate__n;
    }

    N_Vector Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt::ComputeDerivedQuantities(double var_chaste_interface__environment__time, const N_Vector & rY)
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
        const double var_membrane__E_R = -75; // millivolt
        const double var_leakage_current__E_L = 10.613 + var_membrane__E_R; // millivolt
        const double var_leakage_current__i_L = (-var_leakage_current__E_L + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 3); // microA_per_cm2
        const double var_membrane__i_Stim = GetIntracellularAreaStimulus(var_chaste_interface__environment__time); // microA_per_cm2
        // Special handling of data clamp current here
        // (we want to save expense of calling the interpolation method if possible.)
        double var_chaste_interface__membrane_data_clamp_current = 0.0;
        if (mDataClampIsOn)
        {
            var_chaste_interface__membrane_data_clamp_current = (-GetExperimentalVoltageAtTimeT(var_chaste_interface__environment__time) + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 1); // uA_per_cm2
        }
        const double var_potassium_channel__E_K = -12 + var_membrane__E_R; // millivolt
        const double var_potassium_channel__i_K = pow(var_chaste_interface__potassium_channel_n_gate__n, 4) * (-var_potassium_channel__E_K + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 4); // microA_per_cm2
        const double var_sodium_channel__E_Na = 115 + var_membrane__E_R; // millivolt
        const double var_sodium_channel__i_Na = pow(var_chaste_interface__sodium_channel_m_gate__m, 3) * (-var_sodium_channel__E_Na + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 2) * var_chaste_interface__sodium_channel_h_gate__h; // microA_per_cm2

#if CHASTE_SUNDIALS_VERSION >= 60000
        N_Vector dqs = N_VNew_Serial(6, CvodeContextManager::Instance()->GetSundialsContext());
#else
        N_Vector dqs = N_VNew_Serial(6);
#endif
        NV_Ith_S(dqs, 0) = var_chaste_interface__membrane_data_clamp_current;
        NV_Ith_S(dqs, 1) = var_sodium_channel__i_Na;
        NV_Ith_S(dqs, 2) = var_leakage_current__i_L;
        NV_Ith_S(dqs, 3) = var_potassium_channel__i_K;
        NV_Ith_S(dqs, 4) = var_membrane__i_Stim;
        NV_Ith_S(dqs, 5) = var_chaste_interface__environment__time;
        return dqs;
    }

template<>
void OdeSystemInformation<Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt>::Initialise(void)
{
    this->mSystemName = "hodgkin_huxley_squid_axon_model_1952_modified";
    this->mFreeVariableName = "time";
    this->mFreeVariableUnits = "millisecond";

    // NV_Ith_S(rY, 0):
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("millivolt");
    this->mInitialConditions.push_back(-75.0);

    // NV_Ith_S(rY, 1):
    this->mVariableNames.push_back("sodium_channel_m_gate__m");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.05);

    // NV_Ith_S(rY, 2):
    this->mVariableNames.push_back("sodium_channel_h_gate__h");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.6);

    // NV_Ith_S(rY, 3):
    this->mVariableNames.push_back("potassium_channel_n_gate__n");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.325);

    // mParameters[0]:
    this->mParameterNames.push_back("membrane_capacitance");
    this->mParameterUnits.push_back("microF_per_cm2");

    // mParameters[1]:
    this->mParameterNames.push_back("membrane_data_clamp_current_conductance");
    this->mParameterUnits.push_back("dimensionless");

    // mParameters[2]:
    this->mParameterNames.push_back("membrane_fast_sodium_current_conductance");
    this->mParameterUnits.push_back("milliS_per_cm2");

    // mParameters[3]:
    this->mParameterNames.push_back("membrane_leakage_current_conductance");
    this->mParameterUnits.push_back("milliS_per_cm2");

    // mParameters[4]:
    this->mParameterNames.push_back("membrane_potassium_current_conductance");
    this->mParameterUnits.push_back("milliS_per_cm2");

    // Derived Quantity index [0]:
    this->mDerivedQuantityNames.push_back("membrane_data_clamp_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [1]:
    this->mDerivedQuantityNames.push_back("membrane_fast_sodium_current");
    this->mDerivedQuantityUnits.push_back("microA_per_cm2");

    // Derived Quantity index [2]:
    this->mDerivedQuantityNames.push_back("membrane_leakage_current");
    this->mDerivedQuantityUnits.push_back("microA_per_cm2");

    // Derived Quantity index [3]:
    this->mDerivedQuantityNames.push_back("membrane_potassium_current");
    this->mDerivedQuantityUnits.push_back("microA_per_cm2");

    // Derived Quantity index [4]:
    this->mDerivedQuantityNames.push_back("membrane_stimulus_current");
    this->mDerivedQuantityUnits.push_back("microA_per_cm2");

    // Derived Quantity index [5]:
    this->mDerivedQuantityNames.push_back("time");
    this->mDerivedQuantityUnits.push_back("millisecond");

    this->mInitialised = true;
}

// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLCvodeDataClampOpt)

#endif // CHASTE_CVODE
