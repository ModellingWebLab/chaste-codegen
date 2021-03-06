//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: hodgkin_huxley_squid_axon_model_1952_modified
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: GeneralizedRushLarsenSecondOrderOpt)
//! on (date omitted as unimportant)
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

class Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables : public AbstractLookupTableCollection
{
public:
    static Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables* Instance()
    {
        if (mpInstance.get() == NULL)
        {
            mpInstance.reset(new Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables);
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
        const double* const _lt_0_row = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->_lookup_0_row(_table_index_0, _factor_0);
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

    ~Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables()
    {

        if (_lookup_table_0)
        {
            delete[] _lookup_table_0;
            _lookup_table_0 = NULL;
        }

    }

protected:
    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables(const Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables&);
    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables& operator= (const Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables&);
    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables()
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
        mTableMins[0] = -250.0001;
        mTableMaxs[0] = 549.9999;
        mTableSteps[0] = 0.001;
        mTableStepInverses[0] = 1000.0;
        mNeedsRegeneration[0] = true;
        _lookup_table_0 = NULL;

        Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::RegenerateTables();
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
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][0] = exp(0.9375 + 0.012500000000000001 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][1] = 1 / (-1.0 + exp(-6.5 - 0.10000000000000001 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][2] = exp(-3.75 - 0.050000000000000003 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][3] = 1 / (1.0 + exp(-4.5 - 0.10000000000000001 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][4] = exp(-4.166666666666667 - 0.055555555555555552 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][5] = 1 / (-1.0 + exp(-5.0 - 0.10000000000000001 * var_chaste_interface__membrane__V));
            }

            mNeedsRegeneration[0] = false;
        }

        AbstractLookupTableCollection::EventHandler::EndEvent(AbstractLookupTableCollection::EventHandler::GENERATE_TABLES);
    }

private:
    /** The single instance of the class */
    static std::shared_ptr<Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables> mpInstance;

    // Row lookup methods memory
    double _lookup_table_0_row[6];

    // Lookup tables
    double (*_lookup_table_0)[6];

};

std::shared_ptr<Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables> Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::mpInstance;


    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractGeneralizedRushLarsenCardiacCell(
                4,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        //
        this->mpSystemInfo = OdeSystemInformation<Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt>::Instance();
        Init();
        
    }

    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::~Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt()
    {
    }

    AbstractLookupTableCollection* Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::GetLookupTableCollection()
    {
        return Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance();
    }
    
    double Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::GetIIonic(const std::vector<double>* pStateVariables)
    {
        // For state variable interpolation (SVI) we read in interpolated state variables,
        // otherwise for ionic current interpolation (ICI) we use the state variables of this model (node).
        if (!pStateVariables) pStateVariables = &rGetStateVariables();
        const std::vector<double>& rY = *pStateVariables;
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -75.0
        double var_chaste_interface__sodium_channel_m_gate__m = rY[1];
        // Units: dimensionless; Initial value: 0.05
        double var_chaste_interface__sodium_channel_h_gate__h = rY[2];
        // Units: dimensionless; Initial value: 0.6
        double var_chaste_interface__potassium_channel_n_gate__n = rY[3];
        // Units: dimensionless; Initial value: 0.325
        

        const double var_leakage_current__i_L = 19.316099999999999 + 0.29999999999999999 * var_chaste_interface__membrane__V; // microA_per_cm2
        const double var_potassium_channel__i_K = 36.0 * pow(var_chaste_interface__potassium_channel_n_gate__n, 4) * (87.0 + var_chaste_interface__membrane__V); // microA_per_cm2
        const double var_sodium_channel__i_Na = 120.0 * pow(var_chaste_interface__sodium_channel_m_gate__m, 3) * (-40.0 + var_chaste_interface__membrane__V) * var_chaste_interface__sodium_channel_h_gate__h; // microA_per_cm2
        const double var_chaste_interface__i_ionic = var_leakage_current__i_L + var_potassium_channel__i_K + var_sodium_channel__i_Na; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::UpdateTransmembranePotential(double var_chaste_interface__environment__time)
    {
        std::vector<double>& rY = rGetStateVariables();
        const unsigned v_index = GetVoltageIndex();
        const double delta = 1e-8;
        const double yinit = rY[v_index];

        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -75.0
        double var_chaste_interface__sodium_channel_m_gate__m = rY[1];
        // Units: dimensionless; Initial value: 0.05
        double var_chaste_interface__sodium_channel_h_gate__h = rY[2];
        // Units: dimensionless; Initial value: 0.6
        double var_chaste_interface__potassium_channel_n_gate__n = rY[3];
        // Units: dimensionless; Initial value: 0.325
        


        // Mathematics
        double d_dt_chaste_interface_var_membrane__V;
        d_dt_chaste_interface_var_membrane__V = -19.316099999999999 - GetIntracellularAreaStimulus(var_chaste_interface__environment__time) - 0.29999999999999999 * var_chaste_interface__membrane__V - 36.0 * pow(var_chaste_interface__potassium_channel_n_gate__n, 4) * (87.0 + var_chaste_interface__membrane__V) - 120.0 * pow(var_chaste_interface__sodium_channel_m_gate__m, 3) * (-40.0 + var_chaste_interface__membrane__V) * var_chaste_interface__sodium_channel_h_gate__h; // millivolt / millisecond

        double evalF = d_dt_chaste_interface_var_membrane__V;
        mEvalF[0] = d_dt_chaste_interface_var_membrane__V;
        double partialF = EvaluatePartialDerivative0(var_chaste_interface__environment__time, rY, delta, true);
        if (fabs(partialF) < delta)
        {
            rY[v_index] += 0.5*evalF*mDt;
        }
        else
        {
            rY[v_index] += (evalF/partialF)*(exp(partialF*0.5*mDt)-1.0);
        }

        rY[v_index] = yinit;
        evalF = EvaluateYDerivative0(var_chaste_interface__environment__time, rY);
        mEvalF[0] = evalF;
        partialF = EvaluatePartialDerivative0(var_chaste_interface__environment__time, rY, delta, true);
        if (fabs(partialF) < delta)
        {
            rY[v_index] = yinit + evalF*mDt;
        }
        else
        {
            rY[v_index] = yinit + (evalF/partialF)*(exp(partialF*mDt)-1.0);
        }
    }

    void Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::ComputeOneStepExceptVoltage(double var_chaste_interface__environment__time)
    {
        std::vector<double>& rY = rGetStateVariables();
        const double delta=1e-8;
        const unsigned size = GetNumberOfStateVariables();
        mYInit = rY;
        double y_save;

        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -75.0
        double var_chaste_interface__sodium_channel_m_gate__m = rY[1];
        // Units: dimensionless; Initial value: 0.05
        double var_chaste_interface__sodium_channel_h_gate__h = rY[2];
        // Units: dimensionless; Initial value: 0.6
        double var_chaste_interface__potassium_channel_n_gate__n = rY[3];
        // Units: dimensionless; Initial value: 0.325
        

        // Lookup table indexing
        const bool _oob_0 = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY , var_chaste_interface__environment__time));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

        // Mathematics
        double d_dt_chaste_interface_var_membrane__V;
        const double d_dt_chaste_interface_var_potassium_channel_n_gate__n = -0.125 * var_chaste_interface__potassium_channel_n_gate__n * _lt_0_row[0] - 0.01 * _lt_0_row[1] * (1.0 - var_chaste_interface__potassium_channel_n_gate__n) * (65.0 + var_chaste_interface__membrane__V); // 1 / millisecond
        const double d_dt_chaste_interface_var_sodium_channel_h_gate__h = 0.070000000000000007 * (1.0 - var_chaste_interface__sodium_channel_h_gate__h) * _lt_0_row[2] - _lt_0_row[3] * var_chaste_interface__sodium_channel_h_gate__h; // 1 / millisecond
        const double d_dt_chaste_interface_var_sodium_channel_m_gate__m = -4.0 * var_chaste_interface__sodium_channel_m_gate__m * _lt_0_row[4] - 0.10000000000000001 * _lt_0_row[5] * (1.0 - var_chaste_interface__sodium_channel_m_gate__m) * (50.0 + var_chaste_interface__membrane__V); // 1 / millisecond

        if (mSetVoltageDerivativeToZero)
        {
            d_dt_chaste_interface_var_membrane__V = 0.0;
        }
        else
        {
            d_dt_chaste_interface_var_membrane__V = -19.316099999999999 - GetIntracellularAreaStimulus(var_chaste_interface__environment__time) - 0.29999999999999999 * var_chaste_interface__membrane__V - 36.0 * pow(var_chaste_interface__potassium_channel_n_gate__n, 4) * (87.0 + var_chaste_interface__membrane__V) - 120.0 * pow(var_chaste_interface__sodium_channel_m_gate__m, 3) * (-40.0 + var_chaste_interface__membrane__V) * var_chaste_interface__sodium_channel_h_gate__h; // millivolt / millisecond
        }
        
        mEvalF[0] = d_dt_chaste_interface_var_membrane__V;
        mEvalF[1] = d_dt_chaste_interface_var_sodium_channel_m_gate__m;
        mEvalF[2] = d_dt_chaste_interface_var_sodium_channel_h_gate__h;
        mEvalF[3] = d_dt_chaste_interface_var_potassium_channel_n_gate__n;

        
        mPartialF[0] = EvaluatePartialDerivative0(var_chaste_interface__environment__time, rY, delta);
        mPartialF[1] = EvaluatePartialDerivative1(var_chaste_interface__environment__time, rY, delta);
        mPartialF[2] = EvaluatePartialDerivative2(var_chaste_interface__environment__time, rY, delta);
        mPartialF[3] = EvaluatePartialDerivative3(var_chaste_interface__environment__time, rY, delta);
        for (unsigned var=0; var<size; var++)
        {
            if (var == 0) continue;
            if (fabs(mPartialF[var]) < delta)
            {
                rY[var] = mYInit[var] + 0.5*mDt*mEvalF[var];
            }
            else
            {
                rY[var] = mYInit[var] + (mEvalF[var]/mPartialF[var])*(exp(mPartialF[var]*0.5*mDt)-1.0);
            }
            
        }
        
        
        y_save = rY[1];
        rY[1] = mYInit[1];
        mEvalF[1] = EvaluateYDerivative1(var_chaste_interface__environment__time, rY);
        mPartialF[1] = EvaluatePartialDerivative1(var_chaste_interface__environment__time, rY, delta);
        rY[1] = y_save;
        
        
        y_save = rY[2];
        rY[2] = mYInit[2];
        mEvalF[2] = EvaluateYDerivative2(var_chaste_interface__environment__time, rY);
        mPartialF[2] = EvaluatePartialDerivative2(var_chaste_interface__environment__time, rY, delta);
        rY[2] = y_save;
        
        
        y_save = rY[3];
        rY[3] = mYInit[3];
        mEvalF[3] = EvaluateYDerivative3(var_chaste_interface__environment__time, rY);
        mPartialF[3] = EvaluatePartialDerivative3(var_chaste_interface__environment__time, rY, delta);
        rY[3] = y_save;
                
        for (unsigned var=0; var<size; var++)
        {
            if (var == 0) continue;
            if (fabs(mPartialF[var]) < delta)
            {
                rY[var] = mYInit[var] + mDt*mEvalF[var];
            }
            else
            {
                rY[var] = mYInit[var] + (mEvalF[var]/mPartialF[var])*(exp(mPartialF[var]*mDt)-1.0);
            }
            
        }


    }
   
    
    double Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::EvaluateYDerivative0(double var_chaste_interface__environment__time, std::vector<double>& rY)
    {
        double d_dt_chaste_interface_var_membrane__V;
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -75.0
        double var_chaste_interface__sodium_channel_m_gate__m = rY[1];
        // Units: dimensionless; Initial value: 0.05
        double var_chaste_interface__sodium_channel_h_gate__h = rY[2];
        // Units: dimensionless; Initial value: 0.6
        double var_chaste_interface__potassium_channel_n_gate__n = rY[3];
        // Units: dimensionless; Initial value: 0.325
        


        // Mathematics
        d_dt_chaste_interface_var_membrane__V = -19.316099999999999 - GetIntracellularAreaStimulus(var_chaste_interface__environment__time) - 0.29999999999999999 * var_chaste_interface__membrane__V - 36.0 * pow(var_chaste_interface__potassium_channel_n_gate__n, 4) * (87.0 + var_chaste_interface__membrane__V) - 120.0 * pow(var_chaste_interface__sodium_channel_m_gate__m, 3) * (-40.0 + var_chaste_interface__membrane__V) * var_chaste_interface__sodium_channel_h_gate__h; // millivolt / millisecond

        return d_dt_chaste_interface_var_membrane__V;
    }

    double Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::EvaluatePartialDerivative0(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical)
    {
        double partialF;
        if (!forceNumerical && this->mUseAnalyticJacobian)
        {
            double var_chaste_interface__sodium_channel_m_gate__m = rY[1];
            // Units: dimensionless; Initial value: 0.05
            double var_chaste_interface__sodium_channel_h_gate__h = rY[2];
            // Units: dimensionless; Initial value: 0.6
            double var_chaste_interface__potassium_channel_n_gate__n = rY[3];
            // Units: dimensionless; Initial value: 0.325
            


            const double var_x0 = 120.0 * pow(var_chaste_interface__sodium_channel_m_gate__m, 3);
            
            partialF = -0.29999999999999999 - 36.0 * pow(var_chaste_interface__potassium_channel_n_gate__n, 4) - var_x0 * var_chaste_interface__sodium_channel_h_gate__h;
        }
        else
        {
            const double y_save = rY[0];
            rY[0] += delta;
            const double temp = EvaluateYDerivative0(var_chaste_interface__environment__time, rY);
            partialF = (temp-mEvalF[0])/delta;
            rY[0] = y_save;
        }
        return partialF;
    }
    double Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::EvaluateYDerivative1(double var_chaste_interface__environment__time, std::vector<double>& rY)
    {
        
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -75.0
        double var_chaste_interface__sodium_channel_m_gate__m = rY[1];
        // Units: dimensionless; Initial value: 0.05
        

        // Lookup table indexing
        const bool _oob_0 = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY , var_chaste_interface__environment__time));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

        // Mathematics
        const double d_dt_chaste_interface_var_sodium_channel_m_gate__m = -4.0 * var_chaste_interface__sodium_channel_m_gate__m * _lt_0_row[4] - 0.10000000000000001 * _lt_0_row[5] * (1.0 - var_chaste_interface__sodium_channel_m_gate__m) * (50.0 + var_chaste_interface__membrane__V); // 1 / millisecond

        return d_dt_chaste_interface_var_sodium_channel_m_gate__m;
    }

    double Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::EvaluatePartialDerivative1(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical)
    {
        double partialF;
        if (!forceNumerical && this->mUseAnalyticJacobian)
        {
            double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
            // Units: millivolt; Initial value: -75.0
            

        // Lookup table indexing
        const bool _oob_0 = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY , var_chaste_interface__environment__time));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

            const double var_x2 = _lt_0_row[4];
            const double var_x4 = -0.10000000000000001 * var_chaste_interface__membrane__V;
            const double var_x5 = exp(-5.0 + var_x4);
            const double var_x6 = -1.0 + var_x5;
            const double var_x7 = 0.10000000000000001 / var_x6;
            const double var_x8 = 50.0 + var_chaste_interface__membrane__V;
            
            partialF = -4.0 * var_x2 + var_x7 * var_x8;
        }
        else
        {
            const double y_save = rY[1];
            rY[1] += delta;
            const double temp = EvaluateYDerivative1(var_chaste_interface__environment__time, rY);
            partialF = (temp-mEvalF[1])/delta;
            rY[1] = y_save;
        }
        return partialF;
    }
    double Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::EvaluateYDerivative2(double var_chaste_interface__environment__time, std::vector<double>& rY)
    {
        
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -75.0
        double var_chaste_interface__sodium_channel_h_gate__h = rY[2];
        // Units: dimensionless; Initial value: 0.6
        

        // Lookup table indexing
        const bool _oob_0 = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY , var_chaste_interface__environment__time));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

        // Mathematics
        const double d_dt_chaste_interface_var_sodium_channel_h_gate__h = 0.070000000000000007 * (1.0 - var_chaste_interface__sodium_channel_h_gate__h) * _lt_0_row[2] - _lt_0_row[3] * var_chaste_interface__sodium_channel_h_gate__h; // 1 / millisecond

        return d_dt_chaste_interface_var_sodium_channel_h_gate__h;
    }

    double Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::EvaluatePartialDerivative2(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical)
    {
        double partialF;
        if (!forceNumerical && this->mUseAnalyticJacobian)
        {
            double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
            // Units: millivolt; Initial value: -75.0
            

        // Lookup table indexing
        const bool _oob_0 = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY , var_chaste_interface__environment__time));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

            const double var_x4 = -0.10000000000000001 * var_chaste_interface__membrane__V;
            const double var_x9 = _lt_0_row[2];
            const double var_x10 = exp(-4.5 + var_x4);
            const double var_x11 = 1.0 + var_x10;
            
            partialF = -1 / var_x11 - 0.070000000000000007 * var_x9;
        }
        else
        {
            const double y_save = rY[2];
            rY[2] += delta;
            const double temp = EvaluateYDerivative2(var_chaste_interface__environment__time, rY);
            partialF = (temp-mEvalF[2])/delta;
            rY[2] = y_save;
        }
        return partialF;
    }
    double Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::EvaluateYDerivative3(double var_chaste_interface__environment__time, std::vector<double>& rY)
    {
        
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -75.0
        double var_chaste_interface__potassium_channel_n_gate__n = rY[3];
        // Units: dimensionless; Initial value: 0.325
        

        // Lookup table indexing
        const bool _oob_0 = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY , var_chaste_interface__environment__time));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

        // Mathematics
        const double d_dt_chaste_interface_var_potassium_channel_n_gate__n = -0.125 * var_chaste_interface__potassium_channel_n_gate__n * _lt_0_row[0] - 0.01 * _lt_0_row[1] * (1.0 - var_chaste_interface__potassium_channel_n_gate__n) * (65.0 + var_chaste_interface__membrane__V); // 1 / millisecond

        return d_dt_chaste_interface_var_potassium_channel_n_gate__n;
    }

    double Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::EvaluatePartialDerivative3(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical)
    {
        double partialF;
        if (!forceNumerical && this->mUseAnalyticJacobian)
        {
            double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
            // Units: millivolt; Initial value: -75.0
            

        // Lookup table indexing
        const bool _oob_0 = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY , var_chaste_interface__environment__time));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

            const double var_x4 = -0.10000000000000001 * var_chaste_interface__membrane__V;
            const double var_x13 = exp(-6.5 + var_x4);
            const double var_x14 = -1.0 + var_x13;
            const double var_x15 = 0.01 / var_x14;
            const double var_x16 = _lt_0_row[0];
            const double var_x17 = 65.0 + var_chaste_interface__membrane__V;
            
            partialF = -0.125 * var_x16 + var_x15 * var_x17;
        }
        else
        {
            const double y_save = rY[3];
            rY[3] += delta;
            const double temp = EvaluateYDerivative3(var_chaste_interface__environment__time, rY);
            partialF = (temp-mEvalF[3])/delta;
            rY[3] = y_save;
        }
        return partialF;
    }

    std::vector<double> Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt::ComputeDerivedQuantities(double var_chaste_interface__environment__time, const std::vector<double> & rY)
    {
        // Inputs:
        // Time units: millisecond
        

        // Mathematics
        const double var_membrane__i_Stim = GetIntracellularAreaStimulus(var_chaste_interface__environment__time); // microA_per_cm2

        std::vector<double> dqs(2);
        dqs[0] = var_membrane__i_Stim;
        dqs[1] = var_chaste_interface__environment__time;
        return dqs;
    }

template<>
void OdeSystemInformation<Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt>::Initialise(void)
{
    this->mSystemName = "hodgkin_huxley_squid_axon_model_1952_modified";
    this->mFreeVariableName = "time";
    this->mFreeVariableUnits = "millisecond";

    // rY[0]:
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("millivolt");
    this->mInitialConditions.push_back(-75.0);

    // rY[1]:
    this->mVariableNames.push_back("sodium_channel_m_gate__m");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.05);

    // rY[2]:
    this->mVariableNames.push_back("sodium_channel_h_gate__h");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.6);

    // rY[3]:
    this->mVariableNames.push_back("potassium_channel_n_gate__n");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.325);

    // Derived Quantity index [0]:
    this->mDerivedQuantityNames.push_back("membrane_stimulus_current");
    this->mDerivedQuantityUnits.push_back("microA_per_cm2");

    // Derived Quantity index [1]:
    this->mDerivedQuantityNames.push_back("time");
    this->mDerivedQuantityUnits.push_back("millisecond");

    this->mInitialised = true;
}

// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL2Opt)

