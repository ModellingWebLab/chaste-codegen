#ifdef CHASTE_CVODE
#ifndef CELLSHANNON2004FROMCELLMLCVODEDATACLAMP_HPP_
#define CELLSHANNON2004FROMCELLMLCVODEDATACLAMP_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version 0.0.1
//!
//! Model: shannon_2004
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractCardiacCellWithModifiers.hpp"
#include "AbstractModifier.hpp"
#include "AbstractStimulusFunction.hpp"
#include "AbstractCvodeCellWithDataClamp.hpp"

class CellShannon2004FromCellMLCvodeDataClamp : public AbstractCardiacCellWithModifiers<AbstractCvodeCellWithDataClamp >
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractCardiacCellWithModifiers<AbstractCvodeCellWithDataClamp > >(*this);
        
        // Despite this class having modifier member variables, they are all added to the
        // abstract class by the constructor, and archived via that, instead of here.
    }

    //
    // Settable parameters and readable variables
    //
    boost::shared_ptr<AbstractModifier> mp_JSR_calcium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_SR_leak_current_max_modifier;
    boost::shared_ptr<AbstractModifier> mp_SR_release_current_modifier;
    boost::shared_ptr<AbstractModifier> mp_SR_release_current_max_modifier;
    boost::shared_ptr<AbstractModifier> mp_SR_uptake_current_max_modifier;
    boost::shared_ptr<AbstractModifier> mp_cytosolic_calcium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_cytosolic_potassium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_cytosolic_sodium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_extracellular_calcium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_extracellular_potassium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_extracellular_sodium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_ICaL__i_CaL_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_d_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_fCa_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_f_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_f_gate_tau_modifier;
    boost::shared_ptr<AbstractModifier> mp_INa__i_Na_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_h_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_j_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_m_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_IK1__i_K1_modifier;
    boost::shared_ptr<AbstractModifier> mp_IKr__i_Kr_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_rapid_delayed_rectifier_potassium_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_IKs__i_Ks_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_slow_delayed_rectifier_potassium_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_INaCa__i_NaCa_modifier;
    boost::shared_ptr<AbstractModifier> mp_INaCa__V_max_modifier;
    boost::shared_ptr<AbstractModifier> mp_Itos__i_tos_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_transient_outward_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_voltage_modifier;

public:

    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
    double GetIntracellularCalciumConcentration();
    CellShannon2004FromCellMLCvodeDataClamp(boost::shared_ptr<AbstractIvpOdeSolver> pOdeSolver /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~CellShannon2004FromCellMLCvodeDataClamp();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);
    void EvaluateYDerivatives(double var_chaste_interface__environment__time, const N_Vector rY, N_Vector rDY);
    N_Vector ComputeDerivedQuantities(double var_chaste_interface__environment__time, const N_Vector & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(CellShannon2004FromCellMLCvodeDataClamp)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const CellShannon2004FromCellMLCvodeDataClamp * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, CellShannon2004FromCellMLCvodeDataClamp * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)CellShannon2004FromCellMLCvodeDataClamp(p_solver, p_stimulus);
        }

    }

}

#endif // CELLSHANNON2004FROMCELLMLCVODEDATACLAMP_HPP_
#endif // CHASTE_CVODE