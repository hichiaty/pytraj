import unittest
import numpy as np
import pytraj as pt
from pytraj.base import *
from pytraj.testing import test_if_having, no_test
from pytraj.testing import aa_eq
from pytraj import Trajectory, TrajectoryIterator

class TestSimpleRMSD(unittest.TestCase):
    def setUp(self):
        self.traj = pt.iterload("./data/md1_prod.Tc5b.x",
                                "./data/Tc5b.top")

    def test_rmsd_with_mask(self):
        TRAJ = pt.iterload(
            filename="./data/md1_prod.Tc5b.x",
            top="./data/Tc5b.top")
        cpptraj_rmsd = np.loadtxt(
            "./data/rmsd_to_firstFrame_CA_allres.Tc5b.dat",
            skiprows=1).transpose()[1]
        f0 = TRAJ[0]
        arr0 = np.zeros(TRAJ.n_frames)
        arr1 = np.zeros(TRAJ.n_frames)
        mask = "@CA"
        atm = AtomMask(mask)
        TRAJ.top.set_integer_mask(atm)

        for i, frame in enumerate(TRAJ):
            arr0[i] = frame.rmsd(f0, mask=mask, top=TRAJ.top)
            arr1[i] = frame.rmsd(f0, atommask=atm)

        arr2 = pt.rmsd(TRAJ, mask=mask, ref=f0)
        arr3 = pt.rmsd(TRAJ, mask=mask, ref=0)
        aa_eq(arr0, cpptraj_rmsd, decimal=3)
        aa_eq(arr1, cpptraj_rmsd, decimal=3)
        aa_eq(arr2, cpptraj_rmsd, decimal=3)
        aa_eq(arr3, cpptraj_rmsd, decimal=3)

    @test_if_having("mdtraj")
    def test_ComparetoMDtraj(self):
        # use `mdtraj` for rerefence values
        import mdtraj as md
        from pytraj import Trajectory
        traj = pt.load(
            filename="./data/md1_prod.Tc5b.x",
            top="./data/Tc5b.top")
        m_top = md.load_prmtop("./data/Tc5b.top")
        m_traj = md.load_mdcrd("./data/md1_prod.Tc5b.x", m_top)
        m_traj.xyz = m_traj.xyz * 10  # convert `nm` to `Angstrom` unit

        arr0 = pt.rmsd(traj, 0)
        arr1 = pt.rmsd(traj, ref=0)
        arr2 = pt.rmsd(traj, )
        a_md0 = md.rmsd(m_traj, m_traj, 0)
        aa_eq(arr0, arr1)
        aa_eq(arr0, arr2)
        aa_eq(arr0, a_md0)

        arr0 = pt.rmsd(traj, ref=-1)
        arr1 = pt.rmsd(traj, ref=-1)
        a_md = md.rmsd(m_traj, m_traj, -1)
        aa_eq(arr0, arr1)
        aa_eq(arr0, a_md)

        mask = ":3-18@CA,C"
        atm = traj.top(mask)
        arr0 = pt.rmsd(traj, ref=-1, mask=mask)
        arr1 = pt.rmsd(traj, mask=atm.indices, ref=-1)
        arr2 = pt.rmsd(traj, mask=list(atm.indices), ref=-1)
        arr3 = pt.rmsd(traj, mask=tuple(atm.indices), ref=-1)
        a_md = md.rmsd(m_traj, m_traj, -1, atm.indices)
        aa_eq(arr0, a_md)
        aa_eq(arr1, a_md)
        aa_eq(arr2, a_md)
        aa_eq(arr3, a_md)

        fa = Trajectory(traj)
        arr0 = pt.rmsd(fa, ref=-1, mask=mask)
        arr1 = pt.rmsd(fa, mask=atm.indices, ref=-1)
        arr2 = pt.rmsd(fa, mask=list(atm.indices), ref=-1)
        arr3 = pt.rmsd(fa, mask=tuple(atm.indices), ref=-1)
        a_md = md.rmsd(m_traj, m_traj, -1, atm.indices)
        aa_eq(arr0, a_md)
        aa_eq(arr1, a_md)
        aa_eq(arr2, a_md)
        aa_eq(arr3, a_md)

        fa = Trajectory(traj)
        mask = "!@H="
        atm = fa.top(mask)
        arr0 = pt.rmsd(fa, ref=4, mask=mask)
        a_md = md.rmsd(m_traj, m_traj, 4, atm.indices)

        # exclude 0-th frame for ref
        aa_eq(arr0, a_md)

    def test_list_of_masks(self):
        traj = self.traj.copy()
        mask = ['@CA', '@CB', ':3-18@CA,C']
        arr = pt.rmsd(traj, mask=mask)
        for idx, m in enumerate(mask):
            aa_eq(arr[idx], pt.rmsd(traj, mask=m))
            aa_eq(arr[idx], pt.rmsd(traj, mask=traj.top.select(m)))

        mask = ['@CA', '@CB', ':3-18@CA,C', [0, 3, 5]]
        self.assertRaises(ValueError, lambda: pt.rmsd(traj, mask=mask))

class TestRMSDPerRes(unittest.TestCase):
    def test_0(self):
        from pytraj.datafiles import load_cpptraj_output, tz2_ortho_trajin
        traj = pt.iterload("./data/tz2.ortho.nc", "./data/tz2.ortho.parm7")
        cout = load_cpptraj_output(tz2_ortho_trajin + """
        rmsd first @CA perres range 2-7""")
        d = pt.rmsd_perres(traj, ref=0, mask='@CA', resrange='2-7')
        aa_eq(cout.values, d)


class TestRMSDnofit(unittest.TestCase):
    def test_0(self):
        traj = pt.iterload("./data/tz2.ortho.nc", "./data/tz2.ortho.parm7")

        cout = pt.datafiles.load_cpptraj_output("""
        parm ./data/tz2.ortho.parm7
        trajin ./data/tz2.ortho.nc
        rms first nofit
        rms first mass
        """)
        aa_eq(pt.rmsd(traj, nofit=True), cout[0])
        aa_eq(pt.rmsd(traj, mass=True), cout[1])


class TestPairwiseRMSD(unittest.TestCase):
    def testTwoTrajTypes(self):
        '''test different metrics with different traj objects
        '''
        funclist = [pt.iterload, pt.load]
        txt = '''
        parm ./data/Tc5b.top
        trajin ./data/md1_prod.Tc5b.x
        rms2d @CA metric_holder rmsout tmp.out
        '''
        for func in funclist: 
            traj = func("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")
            for metric in ['rms', 'nofit', 'dme']:
                d0 = pt.pairwise_rmsd(traj(mask='@CA'), metric=metric)
                d1 = pt.pairwise_rmsd(traj, mask='@CA', metric=metric)
                d2 = pt.pairwise_rmsd(traj(), mask='@CA', metric=metric)

                txt0 = txt.replace('metric_holder', metric)
                state = pt.datafiles.load_cpptraj_output(txt0, dtype='state')
                d3 = state.datasetlist[-1].values

                aa_eq(d0, d1)
                aa_eq(d0, d2)
                aa_eq(d0, d3)


class TestActionListRMSD(unittest.TestCase):
    def test_0(self):
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")
        standard_rmsd = pt.rmsd(traj, mask='@CA')

        def test_rmsd(input_traj):
            from pytraj.actions.CpptrajActions import Action_Rmsd
            from pytraj.datasets import DatasetList
            dslist = DatasetList()
            act = Action_Rmsd()
            act.read_input('first @CA', top=input_traj.top, dslist=dslist)
            act.process(input_traj.top)

            for frame in input_traj:
                act.do_action(frame)
            return (dslist.values)

        def test_rmsd_actlist(input_traj):
            from pytraj.actions.CpptrajActions import Action_Rmsd
            from pytraj.core.ActionList import ActionList
            from pytraj.datasets import DatasetList

            alist = ActionList()
            dslist = DatasetList()
            act = Action_Rmsd()
            alist.add_action(act, 'first @CA',
                             top=input_traj.top,
                             dslist=dslist)

            for frame in input_traj:
                alist.do_actions(frame)
            return (dslist.values)

        rmsd0 = test_rmsd(traj)
        rmsd1 = test_rmsd(traj[:])
        rmsd2 = test_rmsd_actlist(traj)
        rmsd3 = test_rmsd_actlist(traj[:])
        t0 = traj[:]
        rmsd4 = test_rmsd_actlist(t0)
        aa_eq(standard_rmsd, rmsd0)
        aa_eq(standard_rmsd, rmsd1)
        aa_eq(standard_rmsd, rmsd2)
        aa_eq(standard_rmsd, rmsd3)
        aa_eq(standard_rmsd, rmsd4)


if __name__ == "__main__":
    unittest.main()