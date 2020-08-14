#ifndef CELLASLANIDI_MODEL_2009FROMCELLML_HPP_
#define CELLASLANIDI_MODEL_2009FROMCELLML_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: aslanidi_model_2009
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: Normal)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractCardiacCellWithModifiers.hpp"
#include "AbstractModifier.hpp"
#include "AbstractStimulusFunction.hpp"
#include "AbstractCardiacCell.hpp"

class Cellaslanidi_model_2009FromCellML : public AbstractCardiacCellWithModifiers<AbstractCardiacCell >
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractCardiacCellWithModifiers<AbstractCardiacCell > >(*this);
        
        // Despite this class having modifier member variables, they are all added to the
        // abstract class by the constructor, and archived via that, instead of here.
    }

    //
    // Settable parameters and readable variables
    //
    boost::shared_ptr<AbstractModifier> mp_membrane_capacitance_modifier;
    boost::shared_ptr<AbstractModifier> mp_membrane_voltage_modifier;

public:

    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
    Cellaslanidi_model_2009FromCellML(boost::shared_ptr<AbstractIvpOdeSolver> pSolver, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Cellaslanidi_model_2009FromCellML();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);
    void EvaluateYDerivatives(double var_chaste_interface__environment__time_converted, const std::vector<double>& rY, std::vector<double>& rDY);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time_converted, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Cellaslanidi_model_2009FromCellML)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Cellaslanidi_model_2009FromCellML * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Cellaslanidi_model_2009FromCellML * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Cellaslanidi_model_2009FromCellML(p_solver, p_stimulus);
        }

    }

}

#endif // CELLASLANIDI_MODEL_2009FROMCELLML_HPP_