# distutil: language = c++

from libcpp.string cimport string
from .cpp_core cimport _DispatchObject, DispatchObject, DispatchAllocatorType, FunctPtr
from .Box cimport Box
from ..datafiles.datafiles cimport _DataFileList, DataFileList
from ..Topology cimport _Topology, Topology
from ..Frame cimport _Frame, Frame
from .cpp_core cimport _ArgList, ArgList, _AtomMask, AtomMask
from ..datasets.DatasetList cimport _DatasetList, DatasetList
from ..actions.CpptrajActions cimport _ActionInit, _ActionSetup, _ActionFrame, CoordinateInfo

cdef extern from "ActionList.h":
    cdef cppclass _ActionList "ActionList":
        _ActionList()
        void Clear()
        void SetDebug(int)
        int Debug()
        int AddAction(DispatchAllocatorType, _ArgList&,
                      _ActionInit&,)
        int SetupActions(_ActionSetup, bint exit_on_error)
        bint DoActions(int, _ActionFrame)
        void Print()
        void List()
        bint Empty()
        int Naction()
        const string& CmdString(int)
        DispatchAllocatorType ActionAlloc(int i)

cdef class ActionList:
    cdef _ActionList* thisptr

    # alias for TopologyList (self.process(top))
    cdef object top

    # check if self.process is already called or not
    cdef bint top_is_processed
    cdef public object _dslist
    cdef public object _dflist
    cdef public object _crdinfo