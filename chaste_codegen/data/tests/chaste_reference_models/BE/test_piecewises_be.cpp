//! @file
//!
//! This source file was generated from CellML by chaste_codegen version 0.0.1
//!
//! Model: test_piecewise_BE
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: normal)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "test_piecewises_be.hpp"
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


    Celltest_piecewises_beFromCellMLBackwardEuler::Celltest_piecewises_beFromCellMLBackwardEuler(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus)
        : AbstractBackwardEulerCardiacCell<2>(
                4,
                0,
                pIntracellularStimulus)
    {
        // Time units: millisecond
        // 
        this->mpSystemInfo = OdeSystemInformation<Celltest_piecewises_beFromCellMLBackwardEuler>::Instance();
        Init();
        
    }

    Celltest_piecewises_beFromCellMLBackwardEuler::~Celltest_piecewises_beFromCellMLBackwardEuler()
    {
    }
    
    double Celltest_piecewises_beFromCellMLBackwardEuler::GetIIonic(const std::vector<double>* pStateVariables)
    {
        // For state variable interpolation (SVI) we read in interpolated state variables,
        // otherwise for ionic current interpolation (ICI) we use the state variables of this model (node).
        if (!pStateVariables) pStateVariables = &rGetStateVariables();
        const std::vector<double>& rY = *pStateVariables;
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -69.1865
        
        const double var_membrane__V_orig_deriv = var_chaste_interface__membrane__V; // millivolt / second
        const double var_chaste_interface__i_ionic = 0.001 * HeartConfig::Instance()->GetCapacitance() * var_membrane__V_orig_deriv; // uA_per_cm2

        const double i_ionic = var_chaste_interface__i_ionic;
        EXCEPT_IF_NOT(!std::isnan(i_ionic));
        return i_ionic;
    }

    void Celltest_piecewises_beFromCellMLBackwardEuler::ComputeResidual(double var_chaste_interface__environment__time_converted, const double rCurrentGuess[2], double rResidual[2])
    {
        std::vector<double>& rY = rGetStateVariables();
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -69.1865
        
        //output_nonlinear_state_assignments
        double var_chaste_interface__fast_sodium_current_m_gate2__m = rCurrentGuess[0];
        double var_chaste_interface__fast_sodium_current_m_gate__m = rCurrentGuess[1];
        
        //output_equations
        const double var_fast_sodium_current_m_gate__alpha_m = ((fabs(pow(var_chaste_interface__fast_sodium_current_m_gate__m, 2) * var_chaste_interface__membrane__V) < 0) ? (2000.0) : (200.0 * var_chaste_interface__membrane__V / (1.0 - exp(-0.10000000000000001 * var_chaste_interface__membrane__V)))); // per_second
        const double var_fast_sodium_current_m_gate__m_orig_deriv = var_fast_sodium_current_m_gate__alpha_m; // 1 / second
        const double d_dt_chaste_interface_var_fast_sodium_current_m_gate__m = 0.001 * var_fast_sodium_current_m_gate__m_orig_deriv; // 1 / millisecond
        const double var_fast_sodium_current_m_gate2__alpha_m = ((fabs(var_chaste_interface__membrane__V) < 0) ? (2000.0 * pow(var_chaste_interface__fast_sodium_current_m_gate2__m, 2)) : (200.0 * var_chaste_interface__membrane__V / (1.0 - exp(-0.10000000000000001 * var_chaste_interface__membrane__V)))); // per_second
        const double var_fast_sodium_current_m_gate2__m_orig_deriv = var_fast_sodium_current_m_gate2__alpha_m; // 1 / second
        const double d_dt_chaste_interface_var_fast_sodium_current_m_gate2__m = 0.001 * var_fast_sodium_current_m_gate2__m_orig_deriv; // 1 / millisecond
        
        rResidual[1] = rCurrentGuess[1] - rY[2] - mDt*d_dt_chaste_interface_var_fast_sodium_current_m_gate__m;
        rResidual[0] = rCurrentGuess[0] - rY[3] - mDt*d_dt_chaste_interface_var_fast_sodium_current_m_gate2__m;
    }

    void Celltest_piecewises_beFromCellMLBackwardEuler::ComputeJacobian(double var_chaste_interface__environment__time_converted, const double rCurrentGuess[2], double rJacobian[2][2])
    {
        std::vector<double>& rY = rGetStateVariables();
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -69.1865
        
        double var_chaste_interface__fast_sodium_current_m_gate2__m = rCurrentGuess[0];
        
        
        
        rJacobian[0][0] = 1.0 - (mDt * (0.001 * ((fabs(var_chaste_interface__membrane__V) < 0) ? (4000.0 * var_chaste_interface__fast_sodium_current_m_gate2__m) : (0))));
        rJacobian[0][1] = 0.0;
        rJacobian[1][0] = 0.0;
        rJacobian[1][1] = 1.0;
    }

    void Celltest_piecewises_beFromCellMLBackwardEuler::UpdateTransmembranePotential(double var_chaste_interface__environment__time_converted)
    {
        // Time units: millisecond
        std::vector<double>& rY = rGetStateVariables();
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -69.1865
        
        const double var_membrane__V_orig_deriv = var_chaste_interface__membrane__V; // millivolt / second
        const double d_dt_chaste_interface_var_membrane__V = 0.001 * var_membrane__V_orig_deriv; // millivolt / millisecond
        
        rY[0] += mDt*d_dt_chaste_interface_var_membrane__V;
    }
    
    void Celltest_piecewises_beFromCellMLBackwardEuler::ComputeOneStepExceptVoltage(double var_chaste_interface__environment__time_converted)
    {
        // Time units: millisecond
        std::vector<double>& rY = rGetStateVariables();
        double var_chaste_interface__membrane__V = (mSetVoltageDerivativeToZero ? this->mFixedVoltage : rY[0]);
        // Units: millivolt; Initial value: -69.1865
        double var_chaste_interface__fast_sodium_current_h_gate__h = rY[1];
        // Units: dimensionless; Initial value: 0.1969
        
        
        
        rY[1] = (var_chaste_interface__fast_sodium_current_h_gate__h + ((((var_chaste_interface__membrane__V > 9999999.0) ? (0.001 * var_chaste_interface__membrane__V) : (0))) * mDt)) / (1.0 - ((0.001) * mDt));
        
        double _guess[2] = {rY[3],rY[2]};
        CardiacNewtonSolver<2,Celltest_piecewises_beFromCellMLBackwardEuler>* _p_solver = CardiacNewtonSolver<2,Celltest_piecewises_beFromCellMLBackwardEuler>::Instance();
        _p_solver->Solve(*this, var_chaste_interface__environment__time_converted, _guess);
        rY[3] = _guess[0];
        rY[2] = _guess[1];
    }

    std::vector<double> Celltest_piecewises_beFromCellMLBackwardEuler::ComputeDerivedQuantities(double var_chaste_interface__environment__time_converted, const std::vector<double> & rY)
    {
        // Inputs:
        // Time units: millisecond
        

        // Mathematics

        std::vector<double> dqs(1);
        dqs[0] = var_chaste_interface__environment__time_converted;
        return dqs;
    }

template<>
void OdeSystemInformation<Celltest_piecewises_beFromCellMLBackwardEuler>::Initialise(void)
{
    this->mSystemName = "test_piecewise_BE";
    this->mFreeVariableName = "environment__time";
    this->mFreeVariableUnits = "millisecond";

    // rY[0]:
    this->mVariableNames.push_back("membrane_voltage");
    this->mVariableUnits.push_back("millivolt");
    this->mInitialConditions.push_back(-69.1865);

    // rY[1]:
    this->mVariableNames.push_back("fast_sodium_current_h_gate__h");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.1969);

    // rY[2]:
    this->mVariableNames.push_back("fast_sodium_current_m_gate__m");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0365);

    // rY[3]:
    this->mVariableNames.push_back("fast_sodium_current_m_gate2__m");
    this->mVariableUnits.push_back("dimensionless");
    this->mInitialConditions.push_back(0.0365);

    // Derived Quantity index [0]:
    this->mDerivedQuantityNames.push_back("environment__time");
    this->mDerivedQuantityUnits.push_back("millisecond");

    this->mInitialised = true;
}

// Serialization for Boost >= 1.36
#include "SerializationExportWrapperForCpp.hpp"
CHASTE_CLASS_EXPORT(Celltest_piecewises_beFromCellMLBackwardEuler)
