#ifndef DYNAMICASLANIDI_PURKINJE_MODEL_2009FROMCELLMLOPT_HPP_
#define DYNAMICASLANIDI_PURKINJE_MODEL_2009FROMCELLMLOPT_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: aslanidi_2009
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: NormalOpt)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractCardiacCellWithModifiers.hpp"
#include "AbstractModifier.hpp"
#include "AbstractDynamicallyLoadableEntity.hpp"
#include "AbstractStimulusFunction.hpp"
#include "AbstractCardiacCell.hpp"

class Dynamicaslanidi_Purkinje_model_2009FromCellMLOpt : public AbstractCardiacCellWithModifiers<AbstractCardiacCell >, public AbstractDynamicallyLoadableEntity
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractCardiacCellWithModifiers<AbstractCardiacCell > >(*this);
        archive & boost::serialization::base_object<AbstractDynamicallyLoadableEntity>(*this);
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
    boost::shared_ptr<AbstractModifier> mp_concentration_clamp_onoff_modifier;
    boost::shared_ptr<AbstractModifier> mp_cytosolic_calcium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_cytosolic_potassium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_cytosolic_sodium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_dyadic_space_calcium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_extracellular_calcium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_extracellular_potassium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_extracellular_sodium_concentration_modifier;
    boost::shared_ptr<AbstractModifier> mp_i_Ca_L__i_Ca_L_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_d_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_f2_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_f2_gate_tau_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_fCa2_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_fCa2_gate_tau_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_fCa_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_fCa_gate_tau_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_f_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_L_type_calcium_current_f_gate_tau_modifier;
    boost::shared_ptr<AbstractModifier> mp_i_Na__i_Na_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_h_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_h_gate_tau_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_j_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_j_gate_tau_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_m_gate_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_reduced_inactivation_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_fast_sodium_current_shift_inactivation_modifier;
    boost::shared_ptr<AbstractModifier> mp_i_K1__i_K1_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_inward_rectifier_potassium_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_i_Kr__i_Kr_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_rapid_delayed_rectifier_potassium_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_i_Ks__i_Ks_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_slow_delayed_rectifier_potassium_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_i_NaCa__i_NaCa_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_sodium_calcium_exchanger_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_i_to_1__i_to_1_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_transient_outward_current_conductance_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_voltage_modifier;

private:
    static AbstractCardiacCellWithModifiers<AbstractCardiacCell >* CreateMethod(boost::shared_ptr<AbstractIvpOdeSolver> p_solver, boost::shared_ptr<AbstractStimulusFunction> p_stimulus);
    static bool registered;
public:

    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
    double GetIntracellularCalciumConcentration();
    Dynamicaslanidi_Purkinje_model_2009FromCellMLOpt(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Dynamicaslanidi_Purkinje_model_2009FromCellMLOpt();
    AbstractLookupTableCollection* GetLookupTableCollection();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);
    void EvaluateYDerivatives(double var_chaste_interface__environment__time, const std::vector<double>& rY, std::vector<double>& rDY);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Dynamicaslanidi_Purkinje_model_2009FromCellMLOpt)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Dynamicaslanidi_Purkinje_model_2009FromCellMLOpt * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Dynamicaslanidi_Purkinje_model_2009FromCellMLOpt * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Dynamicaslanidi_Purkinje_model_2009FromCellMLOpt(p_solver, p_stimulus);
        }

    }

}

#endif // DYNAMICASLANIDI_PURKINJE_MODEL_2009FROMCELLMLOPT_HPP_