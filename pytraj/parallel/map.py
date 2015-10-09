import numpy as np
from pytraj.utils import split_range

def map_mpi(func, traj, command, dtype='ndarray', *args, **kwd):
    """parallel with MPI (mpi4py)

    Parameters
    ----------
    func : a function
    traj : pytraj.TrajectoryIterator
    command : str
    dtype : default 'ndarray'
        dtype of return output
    *args, **kwd: additional arguments

    Examples
    --------
    .. code-block:: bash

        $ # create test_radgyr.py file
        $ cat > test_radgyr.py <<EOF
        import pytraj as pt
        from pytraj.parallel import map_mpi
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        
        traj = pt.iterload('tz2.nc', 'tz2.parm7')
        
        result_arr = map_mpi(pt.radgyr, traj, "@CA")
        
        if comm.rank == 0:
            # save data to disk to read later by pytraj.read_pickle
            # pt.to_pickle(result_arr, 'output.pk')
            print(result_arr)
        EOF

        $ # run in parallel
        $ mpirun -n 4 python ./test_radgyr.py  
        [array([ 8.10916061,  7.7643485 ,  8.09693108, ...,  9.70825678,
                9.3161563 ,  8.86720964]), array([ 8.82037273,  8.89008289,  9.48540176, ...,  9.29585981,
                9.53138062,  9.19155977]), array([ 9.13735723,  8.94651001,  8.97810478, ...,  7.68751186,
                8.31361647,  7.83763754]), array([ 7.37423766,  7.05637263,  6.52135566, ...,  6.38061648,
                6.24139008,  6.48994552])]
    """
    from mpi4py import MPI
    comm = MPI.COMM_WORLD 
    size = comm.size
    rank = comm.rank

    # split traj to ``size`` chunks, perform calculation 
    # for rank-th chunk
    start, stop = split_range(size, 0, traj.n_frames)[rank]
    fa_chunk = traj(start=start, stop=stop) 

    dslist = func(fa_chunk, command, dtype=dtype, *args, **kwd)

    # gather data to root
    total = comm.gather(dslist, root=0)
    return total