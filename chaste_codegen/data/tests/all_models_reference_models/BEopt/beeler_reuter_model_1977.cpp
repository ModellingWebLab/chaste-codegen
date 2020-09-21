//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: beeler_reuter_model_1977
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: BackwardEuler)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "beeler_reuter_model_1977.hpp"
#include <cmath>
#include <cassert>
#include <memory>
#include "Exception.hpp"
#include "OdeSystemInformation.hpp"
#include "RegularStimulus.hpp"
#include "HeartConfig.hpp"
#include "IsNan.hpp"
#include "MathsCustomFunctions.hpp"
#include "CardiacNewtonSolver.hpp"

class Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables : public AbstractLookupTableCollection
{
public:
    static Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables* Instance()
    {
        if (mpInstance.get() == NULL)
        {
            mpInstance.reset(new Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables);
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
        for (unsigned j=0; j<24; j++)
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
        const double* const _lt_0_row = Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables::Instance()->_lookup_0_row(_table_index_0, _factor_0);
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

    ~Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables()
    {

        if (_lookup_table_0)
        {
            delete[] _lookup_table_0;
            _lookup_table_0 = NULL;
        }

    }

protected:
    Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables(const Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables&);
    Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables& operator= (const Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables&);
    Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables()
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
        mNumberOfTables[0] = 24;
        mTableMins[0] = -250.0001;
        mTableMaxs[0] = 549.9999;
        mTableSteps[0] = 0.001;
        mTableStepInverses[0] = 1000.0;
        mNeedsRegeneration[0] = true;
        _lookup_table_0 = NULL;

        Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables::RegenerateTables();
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
            _lookup_table_0 = new double[_table_size_0][24];

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][0] = 1 / exp(1.4000000000000001 + 0.040000000000000001 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][1] = -1.0 + exp(3.0800000000000001 + 0.040000000000000001 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][2] = 0.014 * (-1.0 + exp(3.3999999999999999 + 0.040000000000000001 * var_chaste_interface__membrane__V)) / (exp(2.1200000000000001 + 0.040000000000000001 * var_chaste_interface__membrane__V) + exp(4.2400000000000002 + 0.080000000000000002 * var_chaste_interface__membrane__V)) + 0.0007000000000000001 * (23.0 + var_chaste_interface__membrane__V) / (1.0 - exp(-0.92000000000000004 - 0.040000000000000001 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][3] = 1 / (1.0 + exp(0.35997120230381568 - 0.071994240460763137 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][4] = exp(0.050000000000000003 - 0.01 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][5] = 1 / (1.0 + exp(2.2000000000000002 + 0.050000000000000003 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][6] = exp(-0.74576271186440679 - 0.016949152542372881 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][7] = 1 / (1.0 + exp(4.197901049475262 + 0.14992503748125938 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][8] = exp(-0.224 - 0.0080000000000000002 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][9] = 1 / (1.0 + exp(-6.0 - 0.20000000000000001 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][10] = exp(-0.59999999999999998 - 0.02 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][11] = exp(-19.25 - 0.25 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][12] = 1 / (1.0 + exp(-1.845 - 0.082000000000000003 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][13] = 1 / (1.0 + exp(-3.2000000000000002 - 0.10000000000000001 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][14] = 1 / (1.0 + exp(-15.600000000000001 - 0.20000000000000001 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][15] = exp(-19.5 - 0.25 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][16] = exp(-4.032 - 0.056000000000000001 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][17] = 1 / (-1.0 + exp(-4.7000000000000002 - 0.10000000000000001 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][18] = 1 / (1.0 + exp(2.8571428571428572 + 0.057142857142857141 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][19] = exp(4.1322314049586781 + 0.082644628099173556 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][20] = 1 / (1.0 + exp(-0.80000000000000004 - 0.040000000000000001 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][21] = exp(-1.1997600479904018 - 0.059988002399520089 * var_chaste_interface__membrane__V);
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][22] = -0.070000000000000007 * (23.0 + var_chaste_interface__membrane__V) / (1.0 - exp(-0.92000000000000004 - 0.040000000000000001 * var_chaste_interface__membrane__V));
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                _lookup_table_0[i][23] = -1.3999999999999999 * (-1.0 + exp(3.3999999999999999 + 0.040000000000000001 * var_chaste_interface__membrane__V)) / (exp(2.1200000000000001 + 0.040000000000000001 * var_chaste_interface__membrane__V) + exp(4.2400000000000002 + 0.080000000000000002 * var_chaste_interface__membrane__V));
            }

            mNeedsRegeneration[0] = false;
        }

        AbstractLookupTableCollection::EventHandler::EndEvent(AbstractLookupTableCollection::EventHandler::GENERATE_TABLES);
    }

private:
    /** The single instance of the class */
    static std::shared_ptr<Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables> mpInstance;

    // Row lookup methods memory
    double _lookup_table_0_row[24];

    // Lookup tables
    double (*_lookup_table_0)[24];

};

std::shared_ptr<Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables> Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables::mpInstance;

    boost::shared_ptr<RegularStimulus> Cellbeeler_reuter_model_1977FromCellMLBackwardEuler::UseCellMLDefaultStimulus()
    {
        // Use the default stimulus specified by CellML metadata
        const double var_chaste_interface__stimulus_protocol__IstimAmplitude_converted = 50.000000000000007; // uA_per_cm2
        const double var_chaste_interface__stimulus_protocol__IstimPeriod = 1000.0; // ms
        const double var_chaste_interface__stimulus_protocol__IstimPulseDuration = 1.0; // ms
        const double var_chaste_interface__stimulus_protocol__IstimStart = 10.0; // ms
        boost::shared_ptr<RegularStimulus> p_cellml_stim(new RegularStimulus(
                -fabs(var_chaste_interface__stimulus_protocol__IstimAmplitude_converted),
                var_chaste_interface__stimulus_protocol__IstimPulseDuration,
                var_chaste_interface__stimulus_protocol__IstimPeriod,
                var_chaste_interface__stimulus_protocol__IstimStart
                ));
        mpIntracellularStimulus = p_cellml_stim;
        return p_cellml_stim;
    }
    double Cellbeeler_reuter_model_1977FromCellMLBackwardEuler::GetIntracellularCalciumConcentration()
    {
        return mStateVariables[1];
    }
    Cellbeeler_reuter_model_1977FromCellMLBackwardEuler::Cellbeeler_reuter_model_1977FromCellMLBackwardEuler(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractBackwardEulerCardiacCell<1>(
                8,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        //
        this->mpSystemInfo = OdeSystemInformation<Cellbeeler_reuter_model_1977FromCellMLBackwardEuler>::Instance();
        Init();

        // We have a default stimulus specified in the CellML file metadata
        this->mHasDefaultStimulusFromCellML = true;
        
    }

    Cellbeeler_reuter_model_1977FromCellMLBackwardEuler::~Cellbeeler_reuter_model_1977FromCellMLBackwardEuler()
    {
    }

    AbstractLookupTableCollection* Cellbeeler_reuter_model_1977FromCellMLBackwardEuler::GetLookupTableCollection()
    {
        return Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables::Instance();
    }
    
    double Cellbeeler_reuter_model_1977FromCellMLBackwardEuler::GetIIonic(const std::vector<double>* pStateVariables)
    {
        // For state variable interpolation (SVI) we read in interpolated state variables,
        // otherwise for ionic current interpolation (ICI) we use the state variables of this model (node).
        if (!pStateVariables) pStateVariables = &rGetStateVariables();
        const std::vector<double>& rY = *pStateVariables;
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: mV; Initial value: -84.624
        double var_chaste_interface__slow_inward_current__Cai = rY[1];
        // Units: concentration_units; Initial value: 0.0001
        double var_chaste_interface__sodium_current_m_gate__m = rY[2];
        // Units: dimensionless; Initial value: 0.011
        double var_chaste_interface__sodium_current_h_gate__h = rY[3];
        // Units: dimensionless; Initial value: 0.988
        double var_chaste_interface__sodium_current_j_gate__j = rY[4];
        // Units: dimensionless; Initial value: 0.975
        double var_chaste_interface__slow_inward_current_d_gate__d = rY[5];
        // Units: dimensionless; Initial value: 0.003
        double var_chaste_interface__slow_inward_current_f_gate__f = rY[6];
        // Units: dimensionless; Initial value: 0.994
        double var_chaste_interface__time_dependent_outward_current_x1_gate__x1 = rY[7];
        // Units: dimensionless; Initial value: 0.0001
        
        // Lookup table indexing
        const bool _oob_0 = Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

        const double var_slow_inward_current__i_s = 0.00089999999999999998 * (-7.6990712032745758 + 13.028700000000001 * log(var_chaste_interface__slow_inward_current__Cai) + var_chaste_interface__membrane__V) * var_chaste_interface__slow_inward_current_d_gate__d * var_chaste_interface__slow_inward_current_f_gate__f; // uA_per_mm2
        const double var_sodium_current__i_Na = (3.0000000000000001e-5 + 0.040000000000000001 * pow(var_chaste_interface__sodium_current_m_gate__m, 3) * var_chaste_interface__sodium_current_h_gate__h * var_chaste_interface__sodium_current_j_gate__j) * (-50.0 + var_chaste_interface__membrane__V); // uA_per_mm2
        const double var_time_dependent_outward_current__i_x1 = 0.0080000000000000002 * _lt_0_row[0] * (_lt_0_row[1]) * var_chaste_interface__time_dependent_outward_current_x1_gate__x1; // uA_per_mm2
        const double var_time_independent_outward_current__i_K1 = _lt_0_row[2]; // uA_per_mm2
        const double var_chaste_interface__i_ionic = 100.00000000000001 * var_slow_inward_current__i_s + 100.00000000000001 * var_sodium_current__i_Na + 100.00000000000001 * var_time_dependent_outward_current__i_x1 + 100.00000000000001 * var_time_independent_outward_current__i_K1; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellbeeler_reuter_model_1977FromCellMLBackwardEuler::ComputeResidual(double var_chaste_interface__environment__time, const double rCurrentGuess[1], double rResidual[1])
    {
        std::vector<double>& rY = rGetStateVariables();
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: mV; Initial value: -84.624
        double var_chaste_interface__slow_inward_current_d_gate__d = rY[5];
        // Units: dimensionless; Initial value: 0.003
        double var_chaste_interface__slow_inward_current_f_gate__f = rY[6];
        // Units: dimensionless; Initial value: 0.994
        

        //output_nonlinear_state_assignments
        double var_chaste_interface__slow_inward_current__Cai = rCurrentGuess[0];
        
        //output_equations
        const double var_slow_inward_current__i_s = 0.00089999999999999998 * (-7.6990712032745758 + 13.028700000000001 * log(var_chaste_interface__slow_inward_current__Cai) + var_chaste_interface__membrane__V) * var_chaste_interface__slow_inward_current_d_gate__d * var_chaste_interface__slow_inward_current_f_gate__f; // uA_per_mm2
        const double d_dt_chaste_interface_var_slow_inward_current__Cai = 7.0000000000000007e-6 - 0.070000000000000007 * var_chaste_interface__slow_inward_current__Cai - 0.01 * var_slow_inward_current__i_s; // concentration_units / ms
        
        rResidual[0] = rCurrentGuess[0] - rY[1] - mDt*d_dt_chaste_interface_var_slow_inward_current__Cai;
    }

    void Cellbeeler_reuter_model_1977FromCellMLBackwardEuler::ComputeJacobian(double var_chaste_interface__environment__time, const double rCurrentGuess[1], double rJacobian[1][1])
    {
        std::vector<double>& rY = rGetStateVariables();
        double var_chaste_interface__slow_inward_current_d_gate__d = rY[5];
        // Units: dimensionless; Initial value: 0.003
        double var_chaste_interface__slow_inward_current_f_gate__f = rY[6];
        // Units: dimensionless; Initial value: 0.994
        

        double var_chaste_interface__slow_inward_current__Cai = rCurrentGuess[0];
        
        
        
        rJacobian[0][0] = 1.0 - (mDt * (-0.070000000000000007 - 0.0001172583 * var_chaste_interface__slow_inward_current_d_gate__d * var_chaste_interface__slow_inward_current_f_gate__f / var_chaste_interface__slow_inward_current__Cai));
    }

    void Cellbeeler_reuter_model_1977FromCellMLBackwardEuler::UpdateTransmembranePotential(double var_chaste_interface__environment__time)
    {
        // Time units: millisecond
        std::vector<double>& rY = rGetStateVariables();
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: mV; Initial value: -84.624
        double var_chaste_interface__slow_inward_current__Cai = rY[1];
        // Units: concentration_units; Initial value: 0.0001
        double var_chaste_interface__sodium_current_m_gate__m = rY[2];
        // Units: dimensionless; Initial value: 0.011
        double var_chaste_interface__sodium_current_h_gate__h = rY[3];
        // Units: dimensionless; Initial value: 0.988
        double var_chaste_interface__sodium_current_j_gate__j = rY[4];
        // Units: dimensionless; Initial value: 0.975
        double var_chaste_interface__slow_inward_current_d_gate__d = rY[5];
        // Units: dimensionless; Initial value: 0.003
        double var_chaste_interface__slow_inward_current_f_gate__f = rY[6];
        // Units: dimensionless; Initial value: 0.994
        double var_chaste_interface__time_dependent_outward_current_x1_gate__x1 = rY[7];
        // Units: dimensionless; Initial value: 0.0001
        
        // Lookup table indexing
        const bool _oob_0 = Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY , var_chaste_interface__environment__time));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

        const double var_slow_inward_current__i_s = 0.00089999999999999998 * (-7.6990712032745758 + 13.028700000000001 * log(var_chaste_interface__slow_inward_current__Cai) + var_chaste_interface__membrane__V) * var_chaste_interface__slow_inward_current_d_gate__d * var_chaste_interface__slow_inward_current_f_gate__f; // uA_per_mm2
        const double d_dt_chaste_interface_var_membrane__V = -0.99999999999999989 * GetIntracellularAreaStimulus(var_chaste_interface__environment__time) - 100.0 * var_slow_inward_current__i_s + _lt_0_row[22] + _lt_0_row[23] - 100.0 * (3.0000000000000001e-5 + 0.040000000000000001 * pow(var_chaste_interface__sodium_current_m_gate__m, 3) * var_chaste_interface__sodium_current_h_gate__h * var_chaste_interface__sodium_current_j_gate__j) * (-50.0 + var_chaste_interface__membrane__V) - 0.80000000000000004 * _lt_0_row[0] * (_lt_0_row[1]) * var_chaste_interface__time_dependent_outward_current_x1_gate__x1; // mV / ms
        
        rY[0] += mDt*d_dt_chaste_interface_var_membrane__V;
    }
    
    void Cellbeeler_reuter_model_1977FromCellMLBackwardEuler::ComputeOneStepExceptVoltage(double var_chaste_interface__environment__time)
    {
        // Time units: millisecond
        std::vector<double>& rY = rGetStateVariables();
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: mV; Initial value: -84.624
        double var_chaste_interface__sodium_current_m_gate__m = rY[2];
        // Units: dimensionless; Initial value: 0.011
        double var_chaste_interface__sodium_current_h_gate__h = rY[3];
        // Units: dimensionless; Initial value: 0.988
        double var_chaste_interface__sodium_current_j_gate__j = rY[4];
        // Units: dimensionless; Initial value: 0.975
        double var_chaste_interface__slow_inward_current_d_gate__d = rY[5];
        // Units: dimensionless; Initial value: 0.003
        double var_chaste_interface__slow_inward_current_f_gate__f = rY[6];
        // Units: dimensionless; Initial value: 0.994
        double var_chaste_interface__time_dependent_outward_current_x1_gate__x1 = rY[7];
        // Units: dimensionless; Initial value: 0.0001
        
        // Lookup table indexing
        const bool _oob_0 = Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY , var_chaste_interface__environment__time));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellbeeler_reuter_model_1977FromCellMLBackwardEuler_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

        const double var_slow_inward_current_d_gate__alpha_d = 0.095000000000000001 * _lt_0_row[3] * _lt_0_row[4];
        const double var_slow_inward_current_d_gate__beta_d = 0.070000000000000007 * _lt_0_row[5] * _lt_0_row[6];
        const double var_slow_inward_current_f_gate__alpha_f = 0.012 * _lt_0_row[7] * _lt_0_row[8];
        const double var_slow_inward_current_f_gate__beta_f = 0.0064999999999999997 * _lt_0_row[9] * _lt_0_row[10];
        const double var_sodium_current_h_gate__alpha_h = 0.126 * _lt_0_row[11];
        const double var_sodium_current_h_gate__beta_h = 1.7 * _lt_0_row[12];
        const double var_sodium_current_j_gate__alpha_j = 0.055 * _lt_0_row[14] * _lt_0_row[15];
        const double var_sodium_current_j_gate__beta_j = 0.29999999999999999 * _lt_0_row[13];
        const double var_sodium_current_m_gate__alpha_m = -_lt_0_row[17] * (47.0 + var_chaste_interface__membrane__V);
        const double var_sodium_current_m_gate__beta_m = 40.0 * _lt_0_row[16];
        const double var_time_dependent_outward_current_x1_gate__alpha_x1 = 0.00050000000000000001 * _lt_0_row[18] * _lt_0_row[19];
        const double var_time_dependent_outward_current_x1_gate__beta_x1 = 0.0012999999999999999 * _lt_0_row[20] * _lt_0_row[21];
        
        
        rY[5] = (var_chaste_interface__slow_inward_current_d_gate__d + ((var_slow_inward_current_d_gate__alpha_d) * mDt)) / (1.0 - ((-var_slow_inward_current_d_gate__alpha_d - var_slow_inward_current_d_gate__beta_d) * mDt));
        rY[6] = (var_chaste_interface__slow_inward_current_f_gate__f + ((var_slow_inward_current_f_gate__alpha_f) * mDt)) / (1.0 - ((-var_slow_inward_current_f_gate__alpha_f - var_slow_inward_current_f_gate__beta_f) * mDt));
        rY[3] = (var_chaste_interface__sodium_current_h_gate__h + ((var_sodium_current_h_gate__alpha_h) * mDt)) / (1.0 - ((-var_sodium_current_h_gate__alpha_h - var_sodium_current_h_gate__beta_h) * mDt));
        rY[4] = (var_chaste_interface__sodium_current_j_gate__j + ((var_sodium_current_j_gate__alpha_j) * mDt)) / (1.0 - ((-var_sodium_current_j_gate__alpha_j - var_sodium_current_j_gate__beta_j) * mDt));
        rY[2] = (var_chaste_interface__sodium_current_m_gate__m + ((var_sodium_current_m_gate__alpha_m) * mDt)) / (1.0 - ((-var_sodium_current_m_gate__alpha_m - var_sodium_current_m_gate__beta_m) * mDt));
        rY[7] = (var_chaste_interface__time_dependent_outward_current_x1_gate__x1 + ((var_time_dependent_outward_current_x1_gate__alpha_x1) * mDt)) / (1.0 - ((-var_time_dependent_outward_current_x1_gate__alpha_x1 - var_time_dependent_outward_current_x1_gate__beta_x1) * mDt));
        
        double _guess[1] = {rY[1]};
        CardiacNewtonSolver<1,Cellbeeler_reuter_model_1977FromCellMLBackwardEuler>* _p_solver = CardiacNewtonSolver<1,Cellbeeler_reuter_model_1977FromCellMLBackwardEuler>::Instance();
        _p_solver->Solve(*this, var_chaste_interface__environment__time, _guess);
        rY[1] = _guess[0];
    }

    std::vector<double> Cellbeeler_reuter_model_1977FromCellMLBackwardEuler::ComputeDerivedQuantities(double var_chaste_interface__environment__time, const std::vector<double> & rY)
    {
        // Inputs:
        // Time units: millisecond
        

        // Mathematics
        const double var_stimulus_protocol__Istim_converted = -GetIntracellularAreaStimulus(var_chaste_interface__environment__time); // uA_per_cm2

        std::vector<double> dqs(2);
        dqs[0] = var_chaste_interface__environment__time;
        dqs[1] = var_stimulus_protocol__Istim_converted;
        return dqs;
    }

template<>
void OdeSystemInformation<Cellbeeler_reuter_model_1977FromCellMLBackwardEuler>::Initialise(void)
{
    this->mSystemName = "beeler_reuter_model_1977";
    this->mFreeVariableName = "environment__time";
    this->mFreeVariableUnits = "ms";

    // rY[0]:
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("mV");
    this->mInitialConditions.push_back(-84.624);

    // rY[1]:
    this->mVariableNames.push_back("cytosolic_calcium_concentration");
    this->mVariableUnits.push_back("concentration_units");
    this->mInitialConditions.push_back(0.0001);

    // rY[2]:
    this->mVariableNames.push_back("sodium_current_m_gate__m");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.011);

    // rY[3]:
    this->mVariableNames.push_back("sodium_current_h_gate__h");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.988);

    // rY[4]:
    this->mVariableNames.push_back("sodium_current_j_gate__j");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.975);

    // rY[5]:
    this->mVariableNames.push_back("slow_inward_current_d_gate__d");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.003);

    // rY[6]:
    this->mVariableNames.push_back("slow_inward_current_f_gate__f");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.994);

    // rY[7]:
    this->mVariableNames.push_back("time_dependent_outward_current_x1_gate__x1");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0001);

    // Derived Quantity index [0]:
    this->mDerivedQuantityNames.push_back("environment__time");
    this->mDerivedQuantityUnits.push_back("ms");

    // Derived Quantity index [1]:
    this->mDerivedQuantityNames.push_back("membrane_stimulus_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    this->mInitialised = true;
}

// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Cellbeeler_reuter_model_1977FromCellMLBackwardEuler)

