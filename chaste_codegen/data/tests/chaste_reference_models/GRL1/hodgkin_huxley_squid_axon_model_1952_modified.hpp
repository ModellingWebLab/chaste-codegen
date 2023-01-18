#ifndef CELLHODGKIN_HUXLEY_SQUID_AXON_MODEL_1952_MODIFIEDFROMCELLMLGRL1_HPP_
#define CELLHODGKIN_HUXLEY_SQUID_AXON_MODEL_1952_MODIFIEDFROMCELLMLGRL1_HPP_

//! @file
//!
//! This source file was generated from CellML by chaste_codegen version (version omitted as unimportant)
//!
//! Model: hodgkin_huxley_squid_axon_model_1952_modified
//!
//! Processed by chaste_codegen: https://github.com/ModellingWebLab/chaste-codegen
//!     (translator: chaste_codegen, model type: GeneralizedRushLarsenFirstOrder)
//! on (date omitted as unimportant)
//!
//! <autogenerated>

#include "ChasteSerialization.hpp"
#include <boost/serialization/base_object.hpp>
#include "AbstractStimulusFunction.hpp"
#include "AbstractGeneralizedRushLarsenCardiacCell.hpp"

class Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL1 : public AbstractGeneralizedRushLarsenCardiacCell
{
    friend class boost::serialization::access;
    template<class Archive>
    void serialize(Archive & archive, const unsigned int version)
    {
        archive & boost::serialization::base_object<AbstractGeneralizedRushLarsenCardiacCell >(*this);
        
    }

    //
    // Settable parameters and readable variables
    //


private:
const bool is_concentration[4] = {false, false, false, false};
const bool is_probability[4] = {false, false, false, false};
public:

    boost::shared_ptr<RegularStimulus> UseCellMLDefaultStimulus();
    Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL1(boost::shared_ptr<AbstractIvpOdeSolver> /* unused; should be empty */, boost::shared_ptr<AbstractStimulusFunction> pIntracellularStimulus);
    ~Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL1();
    void VerifyStateVariables();
    double GetIIonic(const std::vector<double>* pStateVariables=NULL);
    void UpdateTransmembranePotential(double var_chaste_interface__environment__time);
    void ComputeOneStepExceptVoltage(double var_chaste_interface__environment__time);
    
    double EvaluateYDerivative0(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative0(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative1(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative1(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative2(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative2(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);
    double EvaluateYDerivative3(double var_chaste_interface__environment__time, std::vector<double>& rY);
    double EvaluatePartialDerivative3(double var_chaste_interface__environment__time, std::vector<double>& rY, double delta, bool forceNumerical=false);

    std::vector<double> ComputeDerivedQuantities(double var_chaste_interface__environment__time, const std::vector<double> & rY);
};

// Needs to be included last
#include "SerializationExportWrapper.hpp"
CHASTE_CLASS_EXPORT(Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL1)

namespace boost
{
    namespace serialization
    {
        template<class Archive>
        inline void save_construct_data(
            Archive & ar, const Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL1 * t, const unsigned int fileVersion)
        {
            const boost::shared_ptr<AbstractIvpOdeSolver> p_solver = t->GetSolver();
            const boost::shared_ptr<AbstractStimulusFunction> p_stimulus = t->GetStimulusFunction();
            ar << p_solver;
            ar << p_stimulus;
        }

        template<class Archive>
        inline void load_construct_data(
            Archive & ar, Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL1 * t, const unsigned int fileVersion)
        {
            boost::shared_ptr<AbstractIvpOdeSolver> p_solver;
            boost::shared_ptr<AbstractStimulusFunction> p_stimulus;
            ar >> p_solver;
            ar >> p_stimulus;
            ::new(t)Cellhodgkin_huxley_squid_axon_model_1952_modifiedFromCellMLGRL1(p_solver, p_stimulus);
        }

    }

}

#endif // CELLHODGKIN_HUXLEY_SQUID_AXON_MODEL_1952_MODIFIEDFROMCELLMLGRL1_HPP_