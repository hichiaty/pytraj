from __future__ import absolute_import
# TODO: rename this file
from functools import wraps

# do not import anything else here.
from pytraj.externals.six import string_types, integer_types
from pytraj.utils.convert import array_to_cpptraj_atommask

def _load_Topology(filename):
    from pytraj import Topology, ParmFile
    top = Topology()
    parm = ParmFile()
    parm.readparm(filename, top)
    return top

def _get_topology(traj, top):
    if isinstance(top, string_types):
        _top = _load_Topology(top)
    elif top is None:
        if hasattr(traj, 'top'):
            _top = traj.top
        else:
            # list, tuple of traj objects
            try:
                for tmp in traj:
                    if hasattr(tmp, 'top'):
                        _top = tmp.top
                        break
            except:
                #print("Topology is None")
                _top = None
    else:
        _top = top
    return _top


def _get_data_from_dtype(d0, dtype='dataset'):
    from pytraj.datasets import Dataset
    from pytraj.datasetlist import DatasetList as DSL

    if dtype is None or dtype == 'dataset':
        pass
        if hasattr(d0, 'set__own_memory'):
            d0.set__own_memory(False)
        elif hasattr(d0, '_own_memory'):
            d0._own_memory = False
    if dtype is None:
        return DSL(d0)
    elif not isinstance(dtype, string_types):
        raise ValueError("dtype must a None or a string")
    else:
        dtype = dtype.lower()
        if dtype == 'dataset':
            if isinstance(d0, Dataset):
                return d0
            else:
                return DSL(d0)
        elif dtype == 'ndarray':
            return d0.to_ndarray()
        elif dtype == 'dict':
            return d0.to_dict()
        elif dtype == 'dataframe':
            if hasattr(d0, 'key'):
                d0.key = d0.key.replace(':', '_')
                d0.key = d0.key.replace('-', '_')
            else:
                for _d in d0:
                    _d.key = _d.key.replace(':', '_')
                    _d.key = _d.key.replace('-', '_')
            return d0.to_dataframe()
        elif dtype == 'cpptraj_dataset':
            return d0
        else:
            raise NotImplementedError()


def _get_list_of_commands(mask_or_commands):
    if isinstance(mask_or_commands, string_types):
        return (mask_or_commands, )
    elif isinstance(mask_or_commands, (list, tuple)):
        return tuple(mask_or_commands)
    else:
        raise ValueError("must be string or list/tuple of strings")


def _get_matrix_from_dataset(dset, mat_type='full'):
    # dset in DatasetMatrixDouble object
    if mat_type == 'full':
        return dset.values
    elif mat_type == 'half':
        return dset.to_half_matrix()
    elif mat_type == 'cpptraj':
        return dset._to_cpptraj_sparse_matrix()
    else:
        raise ValueError()


def _get_reference_from_traj(traj, ref):
    if isinstance(ref, integer_types):
        try:
            return traj[ref]
        except IndexError:
            raise IndexError("%s does not support indexing" % traj.__str__())
    elif ref is None:
        try:
            return traj[0]
        except IndexError:
            raise IndexError("If reference is an integer, %s must support indexing" % traj.__str__())
    elif isinstance(ref, string_types):
        raise ValueError("Reference must a an integer or a Frame")
    elif 'Trajectory' in ref.__class__.__name__:
        assert ref.n_frames == 1, "only support 1-frame Trajectory as reference"
        return ref[0]
    else:
        return ref


def _get_fiterator(traj, frame_indices=None):
    from pytraj import Trajectory, TrajectoryIterator
    if frame_indices is None:
        return traj
    else:
        if not isinstance(traj, (Trajectory, TrajectoryIterator)):
            raise ValueError('only support frame_indices for TrajectoryIterator or Trajectory')
        return traj.iterframe(frame_indices=frame_indices)

def _get_resrange(resrange):
    '''return resrange as a string

    Examples
    --------
    >>> _get_resrange('1-3')
    'resrange 1-3'
    >>> _get_resrange(0)
    'resrange 1'
    >>> _get_resrange(range(3))
    'resrange 1,2,3'
    >>> _get_resrange([2, 5, 7])
    'resrange 3,6,8'
    >>> _get_resrange(None)
    ''
    '''
    from pytraj.utils import convert, is_int

    if resrange is not None:
        if is_int(resrange):
            resrange = [resrange, ]
        if isinstance(resrange, string_types):
            _resrange = "resrange " + resrange
        else:
            _resrange = convert.array_to_cpptraj_range(resrange)
            _resrange = "resrange " + str(_resrange)
    else:
        _resrange = ""
    return _resrange

