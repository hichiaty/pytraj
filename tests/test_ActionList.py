#!/usr/bin/env python

from __future__ import print_function
import unittest
import pytraj as pt
from pytraj import adict, allactions
from pytraj import ArgList, Trajectory, Frame
from pytraj.utils import eq, aa_eq
from pytraj.actions import CpptrajActions as CA
from pytraj.datasets import DatasetList as CpptrajDatasetList
from pytraj.datafiles.datafiles import DataFileList
from pytraj.core.ActionList import ActionList


class TestActionList(unittest.TestCase):
    def test_distances(self):
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")[:]

        trajin = pt.datafiles.tc5b_trajin + """
        distance @CB @CA
        distance @CA @H
        """

        cout = pt.datafiles.load_cpptraj_output(trajin)[1:]

        mask_list = ('@CB @CA', '@CA @H')
        dslist = pt.calc_distance(traj, mask_list)
        dslist3_0 = pt.calc_distance(traj, mask_list[0])
        dslist3_1 = pt.calc_distance(traj, mask_list[1])

        # compare to cpptraj output
        aa_eq(dslist.flatten(), cout.values.flatten())
        aa_eq(dslist3_0, dslist[0])
        aa_eq(dslist3_1, dslist[1])

    def test_run_0(self):
        # load traj
        farray = pt.load(
            filename="./data/tz2.truncoct.nc",
            top="./data/tz2.truncoct.parm7")[:2]
        fold = farray.copy()

        act = allactions.Action_Image()
        ptrajin = """                                                     
        center :2-11
        image center familiar com :6                                      
        """

        # create 'strip' action
        stripact = allactions.Action_Strip()

        # creat datasetlist to hold distance data
        dsetlist = CpptrajDatasetList()
        dflist = DataFileList()

        # creat ActionList to hold actions
        alist = ActionList()

        top = farray.top

        # add two actions: Action_Strip and Action_Distance
        alist.add_action(
            allactions.Action_Center(), ArgList(":2-11"),
            top=top)
        alist.add_action(
            allactions.Action_Image(), ArgList("center familiar com :6"),
            top=top)

        #
        assert alist.n_actions == 2

        # do checking
        alist.process(top)

        farray2 = Trajectory()
        frame0 = Frame()
        # testing how fast to do the actions

        # loop all frames
        # use iterator to make faster loop
        # don't use "for i in range(farray.n_frames)"
        for frame in farray:
            # perform actions for each frame
            # we make a copy since we want to keep orginal Frame
            frame0 = frame.copy()
            alist.do_actions(frame0)
            # alist.do_actions(frame)

            # we need to keep the modified frame in farray2
            # farray2.append(frame)
            farray2.append(frame0)

        # make sure that Action_Strip does its job in stripping
        assert farray2.n_frames == farray.n_frames

        fsaved = pt.iterload("./CpptrajTest/Test_Image/image4.crd.save",
                               "./data/tz2.truncoct.parm7")
        assert fsaved.n_frames == 2

    def test_run_1(self):
        # load traj
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")
        dslist = CpptrajDatasetList()
        dflist = DataFileList()

        # creat ActionList to hold actions
        alist = ActionList()
        # add two actions: Action_Dihedral and Action_Distance
        alist.add_action(adict['distance'],
                         ":2@CA :10@CA out ./output/_dist.out", traj.top,
                         dslist, dflist)
        alist.add_action(adict['dihedral'],
                         ":2@CA :3@CA :4@CA :5@CA out ./output/_dih.out",
                         traj.top, dslist, dflist)

        # using string for action 'dssp'
        alist.add_action('dssp', "out ./output/_dssp_alist.out", traj.top,
                         dslist, dflist)
        alist.add_action('matrix', "out ./output/_mat_alist.out", traj.top,
                         dslist, dflist)
        # does not work with `strip` (output traj have the same n_atoms as originl traj)
        #alist.add_action("strip", "!CA", traj.top)
        # turn off for now
        # Error: Could not get associated topology for ./output/test_trajout.nc
        #alist.add_action("outtraj", "./output/test_trajout.nc", traj.top)
        #alist.do_actions([traj[[0, 1]], traj, traj.iterchunk(chunksize=4,
        #                                                     stop=8),
        #                  traj.iterframe()])
        #Nframes = 1 + 1 + traj.n_frames + 8 + traj.n_frames
        #traj2 = pt.iterload("./output/test_trajout.nc", traj.top)
        #assert traj2.n_frames == Nframes

    def test_run_2(self):
        # load traj
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")
        dslist = CpptrajDatasetList()
        dflist = DataFileList()

        # creat ActionList to hold actions
        alist = ActionList()
        alist.add_action(adict['distance'],
                         ":2@CA :10@CA out ./output/_dist.out", traj.top,
                         dslist, dflist)
        alist.do_actions([traj.iterchunk()])
        assert len(dslist) == 1
        assert dslist[0].size == traj.n_frames

    def test_run_3(self):
        dslist = CpptrajDatasetList()
        actlist = ActionList()
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")
        mask_list = ['@CB @CA @N', '@CA @H @N']

        for mask in mask_list:
            actlist.add_action(
                CA.Action_Angle(), mask, traj.top,
                dslist=dslist)
        actlist.do_actions(traj)

        dslist2 = pt.calc_angle(traj, mask_list)

        dslist3_0 = pt.calc_angle(traj, mask_list[0])
        dslist3_1 = pt.calc_angle(traj, mask_list[1])
        aa_eq(dslist3_0, dslist[0].to_ndarray())
        aa_eq(dslist3_1, dslist[1].to_ndarray())

        aa_eq(dslist3_0, dslist[0].to_ndarray())
        aa_eq(dslist3_1, dslist[1].to_ndarray())

    def test_run_4(self):
        dslist = CpptrajDatasetList()
        actlist = ActionList()
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")
        mask_list = ['@CB @CA @N @H', '@CA @H @N @H=']

        for mask in mask_list:
            actlist.add_action(
                CA.Action_Dihedral(), mask, traj.top,
                dslist=dslist)
        actlist.do_actions(traj)

        dslist2 = pt.calc_dihedral(traj, mask_list)

        dslist3_0 = pt.calc_dihedral(traj, mask_list[0])
        dslist3_1 = pt.calc_dihedral(traj, mask_list[1])
        aa_eq(dslist3_0, dslist2[0])
        aa_eq(dslist3_1, dslist2[1])

        aa_eq(dslist3_0, dslist[0].to_ndarray())
        aa_eq(dslist3_1, dslist[1].to_ndarray())

    def test_run_5(self):
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")
        mask_list = ('@CB @CA', '@CA @H')
        dslist = CpptrajDatasetList()
        actlist = ActionList()

        for mask in mask_list:
            actlist.add_action(
                CA.Action_Distance(), mask, traj.top,
                dslist=dslist)
        actlist.do_actions(traj)

        dslist2 = pt.calc_distance(traj, mask_list)
        aa_eq(dslist.values, dslist2)

    def test_6(self):
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")
        mask_list = ('@CB @CA', '@CA @H')
        dslist = pt.calc_distance(traj, mask_list)
        dslist3_0 = pt.calc_distance(traj, mask_list[0])
        dslist3_1 = pt.calc_distance(traj, mask_list[1])

        aa_eq(dslist3_0, dslist[0])
        aa_eq(dslist3_1, dslist[1])

    def test_constructor_from_command_list_TrajectoryIterator(self):
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")

        commands = ['rmsd @CA',
                    'distance :3 :7',
                    'distance     :3 :7',
                    'vector :2 :3']

        dslist = CpptrajDatasetList()
        actlist = ActionList(commands, traj.top, dslist=dslist)

        d0 = dslist.add_set('ref_frame', 'my_ref')
        d0.add_frame(traj[3])

        for frame in traj:
            actlist.do_actions(frame)

        aa_eq(pt.rmsd(traj, mask='@CA'), dslist[0])
        aa_eq(pt.distance(traj, ':3 :7'), dslist[1])
        aa_eq(pt.distance(traj, ':3 :7'), dslist[2])
        aa_eq(pt.vector.vector_mask(traj(rmsfit=(0, '@CA')), ':2 :3'),
              dslist[3].values)

    def test_constructor_from_command_list_Trajectory(self):
        '''mutable Trajectory'''
        # use `load` method rather `iterload`
        traj = pt.load("data/tz2.ortho.nc", "data/tz2.ortho.parm7")

        # make sure no space-sensitivity
        commands = [
                    'autoimage ',
                    'autoimage',
                    'rmsd @CA',
                    'distance :3 :7',
                    'distance     :3 :7',
                    'vector :2 :3',
                    '  distance :3 :7',
                    ]

        dslist = CpptrajDatasetList()
        actlist = ActionList(commands, traj.top, dslist=dslist)

        for frame in traj:
            actlist.do_actions(frame)

        aa_eq(pt.rmsd(traj, mask='@CA'), dslist[0])
        aa_eq(pt.distance(traj, ':3 :7'), dslist[1])
        aa_eq(pt.distance(traj, ':3 :7'), dslist[2])
        # do not need to perform rmsfit again.
        aa_eq(pt.vector.vector_mask(traj, ':2 :3'),
              dslist[3].values)
        aa_eq(pt.distance(traj, ':3 :7'), dslist[4])

    def test_constructor_from_command_list_TrajectoryIterator_no_DatasetList(self):
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")

        commands = ['rmsd @CA',
                    'distance :3 :7',
                    'distance     :3 :7',
                    'vector :2 :3']

        actlist = ActionList(commands, top=traj.top)

        for frame in traj:
            actlist.do_actions(frame)

        aa_eq(pt.rmsd(traj, mask='@CA'), actlist.data[0])
        aa_eq(pt.distance(traj, ':3 :7'), actlist.data[1])
        aa_eq(pt.distance(traj, ':3 :7'), actlist.data[2])
        aa_eq(pt.vector.vector_mask(traj(rmsfit=(0, '@CA')), ':2 :3'),
              actlist.data[3].values)

if __name__ == "__main__":
    unittest.main()