# cython: profile=True
## @file
## 
## This source file was generated from CellML.
## 
## Model: beeler_reuter_model_1977
## 
## Processed by pycml - CellML Tools in Python
##     (translators: , pycml: , optimize: )
## on Fri May 18 13:12:54 2018
## 
## <autogenerated>

import numpy as np

import fc.simulations.model as Model
import fc.utility.environment as Env
import fc.language.values as V

cimport libc.math as math
cimport numpy as np
import os
import shutil
import sys

from fc.sundials.solver cimport CvodeSolver
cimport fc.sundials.sundials as Sundials
from fc.utility.error_handling import ProtocolError

cdef int _EvaluateRhs(Sundials.realtype var_environment__time, Sundials.N_Vector y, Sundials.N_Vector ydot, void* user_data):
    model = <object>user_data
    cdef np.ndarray[Sundials.realtype, ndim=1] parameters = <np.ndarray>model.parameters
    # State variables
    
    
    # Mathematics
    

cdef class GeneratedModel_Proto_tmpO__F2W(CvodeSolver):
    cdef public char* freeVariableName
    cdef public double freeVariable
    cdef public object stateVarMap
    cdef public np.ndarray initialState
    cdef public object parameterMap
    cdef public np.ndarray parameters
    cdef public object outputNames
    
    cdef public object savedStates
    cdef public object env
    cdef public bint dirty
    cdef public char* outputPath
    cdef public object indentLevel
    
    cdef public object _module
    cdef public object simEnv
    
    cdef Sundials.N_Vector _parameters
    cdef public object _outputs
    
    def __init__(self):
        self.freeVariableName = "time"
        self.freeVariable = 0.0
        self.state = np.zeros(0)
        self.stateVarMap = {}
        self.initialState = np.zeros(0)
        
        self.parameterMap = {}
        self.parameters = np.zeros(1)
        self.parameterMap["input"] = 0
        self.parameters[0] = 0 # (c,protocol__input) dimensionless
        
        self.outputNames = []
        outputs = self._outputs = []
        self.outputNames.append("abs")
        outputs.append(np.array(0.0))
        self.outputNames.append("divide")
        outputs.append(np.array(0.0))
        self.outputNames.append("exp")
        outputs.append(np.array(0.0))
        self.outputNames.append("expm1")
        outputs.append(np.array(0.0))
        self.outputNames.append("ln")
        outputs.append(np.array(0.0))
        self.outputNames.append("log")
        outputs.append(np.array(0.0))
        self.outputNames.append("log1p")
        outputs.append(np.array(0.0))
        self.outputNames.append("minus")
        outputs.append(np.array(0.0))
        self.outputNames.append("plus")
        outputs.append(np.array(0.0))
        self.outputNames.append("power2")
        outputs.append(np.array(0.0))
        self.outputNames.append("power3")
        outputs.append(np.array(0.0))
        self.outputNames.append("power4")
        outputs.append(np.array(0.0))
        self.outputNames.append("power_half")
        outputs.append(np.array(0.0))
        self.outputNames.append("root")
        outputs.append(np.array(0.0))
        self.outputNames.append("time")
        outputs.append(np.array(0.0))
        self.outputNames.append("times")
        outputs.append(np.array(0.0))
        self.outputNames.append("uminus")
        outputs.append(np.array(0.0))
        
        self.state = self.initialState.copy()
        self.savedStates = {}
        self.dirty = False
        self.indentLevel = 0
        self.AssociateWithModel(self)
        self._parameters = Sundials.N_VMake_Serial(len(self.parameters), <Sundials.realtype*>(<np.ndarray>self.parameters).data)
        self.env = Env.ModelWrapperEnvironment(self)
    
    def SetRhsWrapper(self):
        flag = Sundials.CVodeInit(self.cvode_mem, _EvaluateRhs, 0.0, self._state)
        self.CheckFlag(flag, "CVodeInit")
    
    def __dealloc__(self):
        if self._parameters != NULL:
            Sundials.N_VDestroy_Serial(self._parameters)
    
    def SetOutputFolder(self, path):
        if os.path.isdir(path) and path.startswith('/tmp'):
            shutil.rmtree(path)
        os.mkdir(path)
        self.outputPath = path
    
    def SetIndentLevel(self, indentLevel):
        self.indentLevel = indentLevel
    
    def SetSolver(self, solver):
        print >>sys.stderr, "  " * self.indentLevel, "SetSolver: Models implemented using Cython contain a built-in ODE solver, so ignoring setting."
    
    def GetEnvironmentMap(self):
        return {'pycml': self.env, 'cmeta': self.env, 'cg': self.env, 'csub': self.env, 'cs': self.env, 'oxmeta': self.env, 'lut': self.env, 'proto': self.env, 'None': self.env, 'bqs': self.env, 'pe': self.env, 'dcterms': self.env, 'local': self.env, 'xml': self.env, 'dc': self.env, 'bqbiol': self.env, 'cml': self.env, 'solver': self.env, 'doc': self.env, 'm': self.env, 'rdf': self.env, 'cellml': self.env, 'vCard': self.env}
    
    cpdef SetFreeVariable(self, double t):
        self.freeVariable = t
        CvodeSolver.SetFreeVariable(self, t)
    
    def SaveState(self, name):
        self.savedStates[name] = self.state.copy()
    
    cpdef ResetState(self, name=None):
        if name is None:
            CvodeSolver.ResetSolver(self, self.initialState)
        else:
            CvodeSolver.ResetSolver(self, self.savedStates[name])
    
    cpdef GetOutputs(self):
        cdef np.ndarray[Sundials.realtype, ndim=1] parameters = self.parameters
        cdef double var_environment__time = self.freeVariable
        # State variables
        
        # Mathematics computing outputs of interest
        cdef double var_protocol__exp = math.exp(parameters[0]) # dimensionless
        cdef double var_protocol__root = math.sqrt(parameters[0]) # dimensionless
        cdef double var_protocol__abs = abs(parameters[0]) # dimensionless
        cdef double var_protocol__power2 = math.pow(parameters[0], 2.0) # dimensionless
        cdef double var_protocol__power_half = math.pow(parameters[0], 0.5) # dimensionless
        cdef double var_protocol__plus = parameters[0] + parameters[0] # dimensionless
        cdef double var_protocol__power3 = math.pow(parameters[0], 3.0) # dimensionless
        cdef double var_protocol__power4 = math.pow(parameters[0], 4.0) # dimensionless
        cdef double var_protocol__minus = parameters[0] - 10.01 # dimensionless
        cdef double var_protocol__log = math.log10(parameters[0]) # dimensionless
        cdef double var_protocol__uminus = -parameters[0] # dimensionless
        cdef double var_protocol__times = parameters[0] * parameters[0] # dimensionless
        cdef double var_protocol__expm1 = math.exp(parameters[0]) - 1.0 # dimensionless
        cdef double var_protocol__ln = math.log(parameters[0]) # dimensionless
        cdef double var_protocol__divide = parameters[0] * 0.099900099900099903 # dimensionless
        cdef double var_protocol__log1p = 1.0 + math.log(parameters[0]) # dimensionless
        
        outputs = self._outputs
        outputs[0][()] = var_protocol__abs
        outputs[1][()] = var_protocol__divide
        outputs[2][()] = var_protocol__exp
        outputs[3][()] = var_protocol__expm1
        outputs[4][()] = var_protocol__ln
        outputs[5][()] = var_protocol__log
        outputs[6][()] = var_protocol__log1p
        outputs[7][()] = var_protocol__minus
        outputs[8][()] = var_protocol__plus
        outputs[9][()] = var_protocol__power2
        outputs[10][()] = var_protocol__power3
        outputs[11][()] = var_protocol__power4
        outputs[12][()] = var_protocol__power_half
        outputs[13][()] = var_protocol__root
        outputs[14][()] = var_environment__time
        outputs[15][()] = var_protocol__times
        outputs[16][()] = var_protocol__uminus
        return outputs
    
