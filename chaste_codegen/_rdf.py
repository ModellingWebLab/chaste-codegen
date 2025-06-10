"""
RDF handling routines, including parsing the 'oxmeta' ontology.
"""
import os

import rdflib
from cellmlmanip.model import Model
from cellmlmanip.rdf import create_rdf_node

from chaste_codegen import MODULE_DIR, CodegenError


_ONTOLOGY = None  # The 'oxmeta' ontology graph
_MULTI_USES_ALLOWED_TAGS = None

PYCMLMETA = 'https://chaste.comlab.ox.ac.uk/cellml/ns/pycml#'
OXMETA = 'https://chaste.comlab.ox.ac.uk/cellml/ns/oxford-metadata#'
BQBIOL = 'http://biomodels.net/biology-qualifiers/'

PRED_IS = create_rdf_node((BQBIOL, 'is'))
PRED_IS_VERSION_OF = create_rdf_node((BQBIOL, 'isVersionOf'))


def _load_ontoloty():
    global _ONTOLOGY

    if _ONTOLOGY is None:
        # Load oxmeta ontology
        _ONTOLOGY = rdflib.Graph()
        ttl_file = os.path.join(MODULE_DIR, 'ontologies', 'oxford-metadata.ttl')
        _ONTOLOGY.parse(ttl_file, format='turtle')


def get_variables_transitively(model, term):
    """Return a list of variables annotated (directly or otherwise) with the given ontology term.

    Direct annotations are those variables annotated with the term via the bqbiol:is or
    bqbiol:isVersionOf predicates.

    However we also look transitively through the 'oxmeta' ontology for terms belonging to the RDF
    class given by ``term``, i.e. are connected to it by a path of ``rdf:type`` predicates, and
    return variables annotated with those terms.

    For example, the oxmeta ontology has a term ``oxmeta:ExtracellularConcentration``, and triples:
    - ``oxmeta:extracellular_calcium_concentration rdf:type oxmeta:ExtracellularConcentration``
    - ``oxmeta:extracellular_sodium_concentration rdf:type oxmeta:ExtracellularConcentration``
    So if you have variables ``Ca_o`` annotated with ``oxmeta:extracellular_calcium_concentration``
    and ``Na_o`` annotated with ``oxmeta:extracellular_sodium_concentration``, then calling
    ``get_variables_transitively(model, oxmeta:ExtracellularConcentration)`` would give you the list
    ``[Ca_o, Na_o]``.

    :param term: the ontology term to search for. Can be anything suitable as input to
        :meth:`create_rdf_node`, typically a :class:`rdflib.term.Node` or ``(ns_uri, local_name)`` pair.
    :return: a list of :class:`cellmlmanip.model.Variable` objects, sorted by order added to the model.
    """

    assert isinstance(term, tuple), "Expecting term to be a namespace tuple"
    assert isinstance(model, Model), "Expecting model to be a cellmlmanip Model"

    _load_ontoloty()

    term = create_rdf_node(term)

    cmeta_ids = set()
    for annotation in _ONTOLOGY.transitive_subjects(rdflib.RDF.type, term):
        cmeta_ids.update(model.rdf.subjects(PRED_IS, annotation))
        cmeta_ids.update(model.rdf.subjects(PRED_IS_VERSION_OF, annotation))

    variables = []
    for cmeta_id in cmeta_ids:
        try:
            variables.append(model.get_variable_by_cmeta_id(cmeta_id))
        except KeyError as e:
            assert 'cmeta id' in str(e) and str(cmeta_id).replace('#', '', 1) in str(e), str(e)
            raise CodegenError('Rdf subject %s does not refer to any existing variable in the model.' % cmeta_id)
    variables.sort(key=lambda sym: sym.order_added)
    return variables


def get_MultipleUsesAllowed_tags():
    global _MULTI_USES_ALLOWED_TAGS
    if _MULTI_USES_ALLOWED_TAGS is None:
        _load_ontoloty()
        _MULTI_USES_ALLOWED_TAGS = set(str(term).replace(OXMETA, '')
                                       for term in _ONTOLOGY.subjects(rdflib.RDF.type,
                                                                      create_rdf_node((OXMETA, 'MultipleUsesAllowed'))))

    return _MULTI_USES_ALLOWED_TAGS
