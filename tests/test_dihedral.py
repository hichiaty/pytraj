from __future__ import print_function
import pytraj as pt
import unittest
import pytraj as pt
from pytraj.base import *
from pytraj import adict
from pytraj import io as mdio
from pytraj.utils import eq, aa_eq
from pytraj.testing import cpptraj_test_dir
import pytraj.common_actions as pyca
from pytraj.misc import from_legends_to_indices


class Test(unittest.TestCase):
    def test_0(self):
        import numpy as np
        traj = mdio.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")
        fa = traj[:]
        mask = ':2@CA :14@CA :15@CA :16@CA'
        txt = '''
        parm ./data/Tc5b.top
        trajin ./data/md1_prod.Tc5b.x
        dihedral %s
        ''' % mask
        d0 = pyca.calc_dihedral(traj, mask, dtype='dataset').to_ndarray()
        d1 = pt.dihedral(traj, mask)
        d2 = pt.calc_dihedral(fa, mask)
        state = pt.load_cpptraj_state(txt)
        state.run()
        dcpp = state.data[1:].values

        aa_eq(d0, d1)
        aa_eq(d0, d2)
        aa_eq(d0, dcpp)

        Nsize = 10
        np.random.seed(1)
        arr = np.random.randint(0, 300, size=Nsize * 4).reshape(Nsize, 4)
        d3 = pt.calc_dihedral(fa, arr)
        d4 = pt.dihedral(traj, arr)
        d5 = pt.dihedral(traj, arr)
        d6 = pt.dihedral(fa, arr)
        d7 = pt.dihedral([fa, traj], arr, n_frames=2 * fa.n_frames)
        aa_eq(d3, d4)
        aa_eq(d3, d5)
        aa_eq(d3, d6)
        aa_eq(d3.T, d7.T[:fa.n_frames])
        aa_eq(d3.T, d7.T[fa.n_frames:])


if __name__ == "__main__":
    unittest.main()