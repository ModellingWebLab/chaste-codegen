#ifdef CHASTE_CVODE
//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: mcallister_noble_tsien_1975_modelB
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: CvodeCellWithDataClampOpt)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "mcallister_noble_tsien_1975_b.hpp"
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

class Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables : public AbstractLookupTableCollection
{
public:
    static Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables* Instance()
    {
        if (mpInstance.get() == NULL)
        {
            mpInstance.reset(new Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables);
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
        for (unsigned j=0; j<25; j++)
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
        const double* const _lt_0_row = Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables::Instance()->_lookup_0_row(_table_index_0, _factor_0);
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

    ~Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables()
    {

        if (_lookup_table_0)
        {
            delete[] _lookup_table_0;
            _lookup_table_0 = NULL;
        }

    }

protected:
    Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables(const Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables&);
    Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables& operator= (const Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables&);
    Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables()
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
        mNumberOfTables[0] = 25;
        mTableMins[0] = -250.0001;
        mTableMaxs[0] = 549.9999;
        mTableSteps[0] = 0.001;
        mTableStepInverses[0] = 1000.0;
        mNeedsRegeneration[0] = true;
        _lookup_table_0 = NULL;

        Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables::RegenerateTables();
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
            _lookup_table_0 = new double[_table_size_0][25];

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 2.7999999999999998 * (-1.0 + exp(4.4000000000000004 + 0.040000000000000001 * var_chaste_interface__membrane__V)) / (exp(2.3999999999999999 + 0.040000000000000001 * var_chaste_interface__membrane__V) + exp(4.7999999999999998 + 0.080000000000000002 * var_chaste_interface__membrane__V));

                _lookup_table_0[i][0] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = exp(1.8 + 0.040000000000000001 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][1] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = -1.0 + exp(3.7999999999999998 + 0.040000000000000001 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][2] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 0.040000000000000001 * (-70.0 + var_chaste_interface__membrane__V) / (1.0 + exp(-6.0 - 0.14999999999999999 * var_chaste_interface__membrane__V));

                _lookup_table_0[i][3] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 0.20000000000000001 * (30.0 + var_chaste_interface__membrane__V) / (1.0 - exp(-1.2 - 0.040000000000000001 * var_chaste_interface__membrane__V));

                _lookup_table_0[i][4] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = exp(-13.064 - 0.184 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][5] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 1.0 + exp(-0.82000000000000006 - 0.082000000000000003 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][6] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = exp(-4.032 - 0.056000000000000001 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][7] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 1.0 - exp(-4.7000000000000002 - 0.10000000000000001 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][8] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = exp(-3.484 - 0.067000000000000004 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][9] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 1.0 - exp(-10.4 - 0.20000000000000001 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][10] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 1.0 + exp(2.8571428571428572 + 0.057142857142857141 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][11] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = exp(4.1322314049586781 + 0.082644628099173556 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][12] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 1.0 + exp(-0.80000000000000004 - 0.040000000000000001 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][13] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = exp(-1.1997600479904018 - 0.059988002399520089 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][14] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 1.0 + exp(-3.7999999999999998 - 0.20000000000000001 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][15] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = exp(-3.552 - 0.088800000000000004 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][16] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 1.0 - exp(-4.0 - 0.10000000000000001 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][17] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = exp(-2.3999999999999999 - 0.040000000000000001 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][18] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 1.0 + exp(-2.262 - 0.086999999999999994 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][19] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = exp(-0.088800000000000004 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][20] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 1.0 - exp(-0.10000000000000001 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][21] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = exp(-0.058823529411764705 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][22] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = 1.0 + exp(-3.75 - 0.125 * var_chaste_interface__membrane__V);

                _lookup_table_0[i][23] = val;
            }

            for (unsigned i=0 ; i<_table_size_0; i++)
            {
                const double var_chaste_interface__membrane__V = mTableMins[0] + i*mTableSteps[0];
                double val = -0.20000000000000001 * (30.0 + var_chaste_interface__membrane__V) / (1.0 - exp(-1.2 - 0.040000000000000001 * var_chaste_interface__membrane__V));

                _lookup_table_0[i][24] = val;
            }

            mNeedsRegeneration[0] = false;
        }

        AbstractLookupTableCollection::EventHandler::EndEvent(AbstractLookupTableCollection::EventHandler::GENERATE_TABLES);
    }

private:
    /** The single instance of the class */
    static std::shared_ptr<Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables> mpInstance;

    // Row lookup methods memory
    double _lookup_table_0_row[25];

    // Lookup tables
    double (*_lookup_table_0)[25];
    int _lookup_table_0_num_misshit_piecewise[25] = {0};

};

std::shared_ptr<Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables> Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables::mpInstance;


    Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt::Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt(boost::shared_ptr<AbstractIvpOdeSolver> pOdeSolver /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractCvodeCellWithDataClamp(
                pOdeSolver,
                10,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        //
        this->mpSystemInfo = OdeSystemInformation<Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt>::Instance();
        Init();
        
        NV_Ith_S(this->mParameters, 0) = 1.0; // (var_secondary_inward_current__g_si_mult) [dimensionless]
        NV_Ith_S(this->mParameters, 1) = 10.0; // (var_membrane__C) [microF_per_cm2]
        NV_Ith_S(this->mParameters, 2) = 0.0; // (var_membrane_data_clamp_current_conductance) [dimensionless]
        NV_Ith_S(this->mParameters, 3) = 150.0; // (var_fast_sodium_current__g_Na) [milliS_per_cm2]
        NV_Ith_S(this->mParameters, 4) = 25.0; // (var_plateau_potassium_current2__g_x2) [microA_per_cm2]
    }

    Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt::~Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt()
    {
    }

    AbstractLookupTableCollection* Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt::GetLookupTableCollection()
    {
        return Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables::Instance();
    }
    
    double Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt::GetIIonic(const std::vector<double>* pStateVariables)
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
        // Units: millivolt; Initial value: -78.041367
        double var_chaste_interface__fast_sodium_current_m_gate__m = NV_Ith_S(rY, 1);
        // Units: dimensionless; Initial value: 0.02566853
        double var_chaste_interface__fast_sodium_current_h_gate__h = NV_Ith_S(rY, 2);
        // Units: dimensionless; Initial value: 0.78656359
        double var_chaste_interface__secondary_inward_current_d_gate__d = NV_Ith_S(rY, 3);
        // Units: dimensionless; Initial value: 0.00293135
        double var_chaste_interface__secondary_inward_current_f_gate__f = NV_Ith_S(rY, 4);
        // Units: dimensionless; Initial value: 0.80873917
        double var_chaste_interface__pacemaker_potassium_current_s_gate__s = NV_Ith_S(rY, 5);
        // Units: dimensionless; Initial value: 0.75473994
        double var_chaste_interface__plateau_potassium_current1_x1_gate__x1 = NV_Ith_S(rY, 6);
        // Units: dimensionless; Initial value: 0.02030289
        double var_chaste_interface__plateau_potassium_current2_x2_gate__x2 = NV_Ith_S(rY, 7);
        // Units: dimensionless; Initial value: 0.0176854
        double var_chaste_interface__transient_chloride_current_q_gate__q = NV_Ith_S(rY, 8);
        // Units: dimensionless; Initial value: 3.11285794
        double var_chaste_interface__transient_chloride_current_r_gate__r = NV_Ith_S(rY, 9);
        // Units: dimensionless; Initial value: 0.13500116
        
        // Lookup table indexing
        const bool _oob_0 = Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

        const double var_fast_sodium_current__i_Na = pow(var_chaste_interface__fast_sodium_current_m_gate__m, 3) * (-40.0 + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 3) * var_chaste_interface__fast_sodium_current_h_gate__h; // microA_per_cm2
        const double var_pacemaker_potassium_current__I_K2 = _lt_0_row[0]; // microA_per_cm2
        const double var_pacemaker_potassium_current__i_K2 = var_pacemaker_potassium_current__I_K2 * var_chaste_interface__pacemaker_potassium_current_s_gate__s; // microA_per_cm2
        const double var_plateau_potassium_current1__i_x1 = 1.2 * (_lt_0_row[2]) * var_chaste_interface__plateau_potassium_current1_x1_gate__x1 / _lt_0_row[1]; // microA_per_cm2
        const double var_plateau_potassium_current2__i_x2 = (25.0 + 0.38500000000000001 * var_chaste_interface__membrane__V + NV_Ith_S(mParameters, 4)) * var_chaste_interface__plateau_potassium_current2_x2_gate__x2; // microA_per_cm2
        const double var_secondary_inward_current__i_si = (_lt_0_row[3] + 0.80000000000000004 * (-70.0 + var_chaste_interface__membrane__V) * var_chaste_interface__secondary_inward_current_d_gate__d * var_chaste_interface__secondary_inward_current_f_gate__f) * NV_Ith_S(mParameters, 0); // microA_per_cm2
        const double var_sodium_background_current__i_Na_b = -4.2000000000000002 + 0.105 * var_chaste_interface__membrane__V; // microA_per_cm2
        const double var_time_independent_outward_current__i_K1 = 0.35714285714285715 * var_pacemaker_potassium_current__I_K2 + _lt_0_row[4]; // microA_per_cm2
        const double var_chloride_background_current__i_Cl_b = 0.70000000000000007 + 0.01 * var_chaste_interface__membrane__V; // microA_per_cm2
        const double var_transient_chloride_current__i_qr = 2.5 * (70.0 + var_chaste_interface__membrane__V) * var_chaste_interface__transient_chloride_current_q_gate__q * var_chaste_interface__transient_chloride_current_r_gate__r; // microA_per_cm2
        const double var_chaste_interface__i_ionic = var_chloride_background_current__i_Cl_b + var_fast_sodium_current__i_Na + var_pacemaker_potassium_current__i_K2 + var_plateau_potassium_current1__i_x1 + var_plateau_potassium_current2__i_x2 + var_secondary_inward_current__i_si + var_sodium_background_current__i_Na_b + var_time_independent_outward_current__i_K1 + var_transient_chloride_current__i_qr; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        if (made_new_cvode_vector)
        {
            DeleteVector(rY);
        }
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt::EvaluateYDerivatives(double var_chaste_interface__environment__time, const N_Vector rY, N_Vector rDY)
    {
        // Inputs:
        // Time units: millisecond
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, 0));
        // Units: millivolt; Initial value: -78.041367
        double var_chaste_interface__fast_sodium_current_m_gate__m = NV_Ith_S(rY, 1);
        // Units: dimensionless; Initial value: 0.02566853
        double var_chaste_interface__fast_sodium_current_h_gate__h = NV_Ith_S(rY, 2);
        // Units: dimensionless; Initial value: 0.78656359
        double var_chaste_interface__secondary_inward_current_d_gate__d = NV_Ith_S(rY, 3);
        // Units: dimensionless; Initial value: 0.00293135
        double var_chaste_interface__secondary_inward_current_f_gate__f = NV_Ith_S(rY, 4);
        // Units: dimensionless; Initial value: 0.80873917
        double var_chaste_interface__pacemaker_potassium_current_s_gate__s = NV_Ith_S(rY, 5);
        // Units: dimensionless; Initial value: 0.75473994
        double var_chaste_interface__plateau_potassium_current1_x1_gate__x1 = NV_Ith_S(rY, 6);
        // Units: dimensionless; Initial value: 0.02030289
        double var_chaste_interface__plateau_potassium_current2_x2_gate__x2 = NV_Ith_S(rY, 7);
        // Units: dimensionless; Initial value: 0.0176854
        double var_chaste_interface__transient_chloride_current_q_gate__q = NV_Ith_S(rY, 8);
        // Units: dimensionless; Initial value: 3.11285794
        double var_chaste_interface__transient_chloride_current_r_gate__r = NV_Ith_S(rY, 9);
        // Units: dimensionless; Initial value: 0.13500116

        // Lookup table indexing
        const bool _oob_0 = Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables::Instance()->CheckIndex0(var_chaste_interface__membrane__V);
// LCOV_EXCL_START
        if (_oob_0)
            EXCEPTION(DumpState("membrane_voltage outside lookup table range", rY , var_chaste_interface__environment__time));
// LCOV_EXCL_STOP
        const double* const _lt_0_row = Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt_LookupTables::Instance()->IndexTable0(var_chaste_interface__membrane__V);

        // Mathematics
        double d_dt_chaste_interface_var_membrane__V;
        const double d_dt_chaste_interface_var_fast_sodium_current_h_gate__h = 0.0085000000000000006 * (1.0 - var_chaste_interface__fast_sodium_current_h_gate__h) * _lt_0_row[5] - 2.5 * var_chaste_interface__fast_sodium_current_h_gate__h / (_lt_0_row[6]); // 1 / millisecond
        const double d_dt_chaste_interface_var_fast_sodium_current_m_gate__m = -40.0 * var_chaste_interface__fast_sodium_current_m_gate__m * _lt_0_row[7] + (1.0 - var_chaste_interface__fast_sodium_current_m_gate__m) * (47.0 + var_chaste_interface__membrane__V) / (_lt_0_row[8]); // 1 / millisecond
        const double d_dt_chaste_interface_var_pacemaker_potassium_current_s_gate__s = -5.0000000000000002e-5 * var_chaste_interface__pacemaker_potassium_current_s_gate__s * _lt_0_row[9] + 0.001 * (1.0 - var_chaste_interface__pacemaker_potassium_current_s_gate__s) * (52.0 + var_chaste_interface__membrane__V) / (_lt_0_row[10]); // 1 / millisecond
        const double d_dt_chaste_interface_var_plateau_potassium_current1_x1_gate__x1 = 0.00050000000000000001 * (1.0 - var_chaste_interface__plateau_potassium_current1_x1_gate__x1) * _lt_0_row[12] / (_lt_0_row[11]) - 0.0012999999999999999 * var_chaste_interface__plateau_potassium_current1_x1_gate__x1 * _lt_0_row[14] / (_lt_0_row[13]); // 1 / millisecond
        const double d_dt_chaste_interface_var_plateau_potassium_current2_x2_gate__x2 = 0.000127 * (1.0 - var_chaste_interface__plateau_potassium_current2_x2_gate__x2) / (_lt_0_row[15]) - 0.00029999999999999997 * var_chaste_interface__plateau_potassium_current2_x2_gate__x2 * _lt_0_row[14] / (_lt_0_row[13]); // 1 / millisecond
        const double d_dt_chaste_interface_var_secondary_inward_current_d_gate__d = -0.02 * var_chaste_interface__secondary_inward_current_d_gate__d * _lt_0_row[16] + 0.002 * (1.0 - var_chaste_interface__secondary_inward_current_d_gate__d) * (40.0 + var_chaste_interface__membrane__V) / (_lt_0_row[17]); // 1 / millisecond
        const double d_dt_chaste_interface_var_secondary_inward_current_f_gate__f = 0.00098700000000000003 * (1.0 - var_chaste_interface__secondary_inward_current_f_gate__f) * _lt_0_row[18] - 0.02 * var_chaste_interface__secondary_inward_current_f_gate__f / (_lt_0_row[19]); // 1 / millisecond
        const double d_dt_chaste_interface_var_transient_chloride_current_q_gate__q = -0.080000000000000002 * var_chaste_interface__transient_chloride_current_q_gate__q * _lt_0_row[20] + 0.0080000000000000002 * (1.0 - var_chaste_interface__transient_chloride_current_q_gate__q) * var_chaste_interface__membrane__V / (_lt_0_row[21]); // 1 / millisecond
        const double d_dt_chaste_interface_var_transient_chloride_current_r_gate__r = 3.3000000000000003e-5 * (1.0 - var_chaste_interface__transient_chloride_current_r_gate__r) * _lt_0_row[22] - 0.033000000000000002 * var_chaste_interface__transient_chloride_current_r_gate__r / (_lt_0_row[23]); // 1 / millisecond

        if (mSetVoltageDerivativeToZero)
        {
            d_dt_chaste_interface_var_membrane__V = 0.0;
        }
        else
        {
            const double var_pacemaker_potassium_current__I_K2 = _lt_0_row[0]; // microA_per_cm2
            d_dt_chaste_interface_var_membrane__V = (3.5 - 0.11499999999999999 * var_chaste_interface__membrane__V - 0.35714285714285715 * var_pacemaker_potassium_current__I_K2 - (-GetExperimentalVoltageAtTimeT(var_chaste_interface__environment__time) + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 2) - (_lt_0_row[3] + 0.80000000000000004 * (-70.0 + var_chaste_interface__membrane__V) * var_chaste_interface__secondary_inward_current_d_gate__d * var_chaste_interface__secondary_inward_current_f_gate__f) * NV_Ith_S(mParameters, 0) - (25.0 + 0.38500000000000001 * var_chaste_interface__membrane__V + NV_Ith_S(mParameters, 4)) * var_chaste_interface__plateau_potassium_current2_x2_gate__x2 - var_pacemaker_potassium_current__I_K2 * var_chaste_interface__pacemaker_potassium_current_s_gate__s + _lt_0_row[24] - 2.5 * (70.0 + var_chaste_interface__membrane__V) * var_chaste_interface__transient_chloride_current_q_gate__q * var_chaste_interface__transient_chloride_current_r_gate__r - 1.2 * (_lt_0_row[2]) * var_chaste_interface__plateau_potassium_current1_x1_gate__x1 / _lt_0_row[1] - pow(var_chaste_interface__fast_sodium_current_m_gate__m, 3) * (-40.0 + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 3) * var_chaste_interface__fast_sodium_current_h_gate__h) / NV_Ith_S(mParameters, 1); // millivolt / millisecond
        }
        
        NV_Ith_S(rDY,0) = d_dt_chaste_interface_var_membrane__V;
        NV_Ith_S(rDY,1) = d_dt_chaste_interface_var_fast_sodium_current_m_gate__m;
        NV_Ith_S(rDY,2) = d_dt_chaste_interface_var_fast_sodium_current_h_gate__h;
        NV_Ith_S(rDY,3) = d_dt_chaste_interface_var_secondary_inward_current_d_gate__d;
        NV_Ith_S(rDY,4) = d_dt_chaste_interface_var_secondary_inward_current_f_gate__f;
        NV_Ith_S(rDY,5) = d_dt_chaste_interface_var_pacemaker_potassium_current_s_gate__s;
        NV_Ith_S(rDY,6) = d_dt_chaste_interface_var_plateau_potassium_current1_x1_gate__x1;
        NV_Ith_S(rDY,7) = d_dt_chaste_interface_var_plateau_potassium_current2_x2_gate__x2;
        NV_Ith_S(rDY,8) = d_dt_chaste_interface_var_transient_chloride_current_q_gate__q;
        NV_Ith_S(rDY,9) = d_dt_chaste_interface_var_transient_chloride_current_r_gate__r;
    }

    N_Vector Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt::ComputeDerivedQuantities(double var_chaste_interface__environment__time, const N_Vector & rY)
    {
        // Inputs:
        // Time units: millisecond
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : NV_Ith_S(rY, 0));
        // Units: millivolt; Initial value: -78.041367
        double var_chaste_interface__fast_sodium_current_m_gate__m = NV_Ith_S(rY, 1);
        // Units: dimensionless; Initial value: 0.02566853
        double var_chaste_interface__fast_sodium_current_h_gate__h = NV_Ith_S(rY, 2);
        // Units: dimensionless; Initial value: 0.78656359
        

        // Mathematics
        const double var_fast_sodium_current__E_Na = 40.0; // millivolt
        const double var_fast_sodium_current__i_Na = pow(var_chaste_interface__fast_sodium_current_m_gate__m, 3) * (-var_fast_sodium_current__E_Na + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 3) * var_chaste_interface__fast_sodium_current_h_gate__h; // microA_per_cm2
        // Special handling of data clamp current here
        // (we want to save expense of calling the interpolation method if possible.)
        double var_chaste_interface__membrane_data_clamp_current = 0.0;
        if (mDataClampIsOn)
        {
            var_chaste_interface__membrane_data_clamp_current = (-GetExperimentalVoltageAtTimeT(var_chaste_interface__environment__time) + var_chaste_interface__membrane__V) * NV_Ith_S(mParameters, 2); // uA_per_cm2
        }
        const double var_pacemaker_potassium_current__E_K = -110.0; // millivolt
        const double var_pacemaker_potassium_current__I_K2 = 2.7999999999999998 * (-1.0 + exp(0.040000000000000001 * var_chaste_interface__membrane__V - 0.040000000000000001 * var_pacemaker_potassium_current__E_K)) / (exp(2.3999999999999999 + 0.040000000000000001 * var_chaste_interface__membrane__V) + exp(4.7999999999999998 + 0.080000000000000002 * var_chaste_interface__membrane__V)); // microA_per_cm2
        const double var_time_independent_outward_current__E_K1 = -30.0; // millivolt
        const double var_time_independent_outward_current__i_K1 = 0.35714285714285715 * var_pacemaker_potassium_current__I_K2 + 0.20000000000000001 * (-var_time_independent_outward_current__E_K1 + var_chaste_interface__membrane__V) / (1.0 - exp(0.040000000000000001 * var_time_independent_outward_current__E_K1 - 0.040000000000000001 * var_chaste_interface__membrane__V)); // microA_per_cm2

        N_Vector dqs = N_VNew_Serial(4);
        NV_Ith_S(dqs, 0) = var_chaste_interface__membrane_data_clamp_current;
        NV_Ith_S(dqs, 1) = var_fast_sodium_current__i_Na;
        NV_Ith_S(dqs, 2) = var_time_independent_outward_current__i_K1;
        NV_Ith_S(dqs, 3) = var_chaste_interface__environment__time;
        return dqs;
    }

template<>
void OdeSystemInformation<Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt>::Initialise(void)
{
    this->mSystemName = "mcallister_noble_tsien_1975_modelB";
    this->mFreeVariableName = "time";
    this->mFreeVariableUnits = "millisecond";

    // NV_Ith_S(rY, 0):
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("millivolt");
    this->mInitialConditions.push_back(-78.041367);

    // NV_Ith_S(rY, 1):
    this->mVariableNames.push_back("fast_sodium_current_m_gate__m");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.02566853);

    // NV_Ith_S(rY, 2):
    this->mVariableNames.push_back("fast_sodium_current_h_gate__h");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.78656359);

    // NV_Ith_S(rY, 3):
    this->mVariableNames.push_back("secondary_inward_current_d_gate__d");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.00293135);

    // NV_Ith_S(rY, 4):
    this->mVariableNames.push_back("secondary_inward_current_f_gate__f");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.80873917);

    // NV_Ith_S(rY, 5):
    this->mVariableNames.push_back("pacemaker_potassium_current_s_gate__s");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.75473994);

    // NV_Ith_S(rY, 6):
    this->mVariableNames.push_back("plateau_potassium_current1_x1_gate__x1");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.02030289);

    // NV_Ith_S(rY, 7):
    this->mVariableNames.push_back("plateau_potassium_current2_x2_gate__x2");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0176854);

    // NV_Ith_S(rY, 8):
    this->mVariableNames.push_back("transient_chloride_current_q_gate__q");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(3.11285794);

    // NV_Ith_S(rY, 9):
    this->mVariableNames.push_back("transient_chloride_current_r_gate__r");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.13500116);

    // mParameters[0]:
    this->mParameterNames.push_back("membrane_L_type_calcium_current_conductance");
    this->mParameterUnits.push_back("dimensionless");

    // mParameters[1]:
    this->mParameterNames.push_back("membrane_capacitance");
    this->mParameterUnits.push_back("microF_per_cm2");

    // mParameters[2]:
    this->mParameterNames.push_back("membrane_data_clamp_current_conductance");
    this->mParameterUnits.push_back("dimensionless");

    // mParameters[3]:
    this->mParameterNames.push_back("membrane_fast_sodium_current_conductance");
    this->mParameterUnits.push_back("milliS_per_cm2");

    // mParameters[4]:
    this->mParameterNames.push_back("membrane_rapid_delayed_rectifier_potassium_current_conductance");
    this->mParameterUnits.push_back("microA_per_cm2");

    // Derived Quantity index [0]:
    this->mDerivedQuantityNames.push_back("membrane_data_clamp_current");
    this->mDerivedQuantityUnits.push_back("uA_per_cm2");

    // Derived Quantity index [1]:
    this->mDerivedQuantityNames.push_back("membrane_fast_sodium_current");
    this->mDerivedQuantityUnits.push_back("microA_per_cm2");

    // Derived Quantity index [2]:
    this->mDerivedQuantityNames.push_back("membrane_inward_rectifier_potassium_current");
    this->mDerivedQuantityUnits.push_back("microA_per_cm2");

    // Derived Quantity index [3]:
    this->mDerivedQuantityNames.push_back("time");
    this->mDerivedQuantityUnits.push_back("millisecond");

    
    this->mAttributes["SuggestedCycleLength"] = 2000;
    this->mInitialised = true;
}

// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Cellmcallister_noble_tsien_1975_bFromCellMLCvodeDataClampOpt)

#endif // CHASTE_CVODE