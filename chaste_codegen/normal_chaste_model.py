from chaste_codegen.chaste_model import ChasteModel


class NormalChasteModel(ChasteModel):
    """ Holds template and information specific for the Normal model type"""

    def __init__(self, model, file_name, **kwargs):
        super().__init__(model, file_name, **kwargs)
        self._hpp_template = 'normal_model.hpp'
        self._cpp_template = 'normal_model.cpp'
        self._vars_for_template['base_class'] = 'AbstractCardiacCell'
        self._vars_for_template['model_type'] = 'Normal'
