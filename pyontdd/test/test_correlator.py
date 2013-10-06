import unittest
import os
import numpy.random as nprnd
import numpy as np
from pyontdd.lib.io import hadron_from_pickle, write_pickle_file, hadron_collection_from_folder
from pyontdd.lib.fitfunc import PP, AA, AP
from pyontdd.lib.lattice import Lattice24c


class CorrelatorTests(unittest.TestCase):
    @staticmethod
    def makePPCorrelator(m, z, T):
        corr = [PP(t, m, z, T) + nprnd.normal(0., 1e-5) for t in range(T)]
        return corr

    @staticmethod
    def makeSimCorrelator(m, z, Z, f, T):
        corr = [[PP(t, m, z, T) + nprnd.normal(0., 1e-4) for t in range(T)],
                [AA(t, m, f, Z, T) + nprnd.normal(0., 1e-4) for t in range(T)],
                [AP(t, m, z, f, Z, T) + nprnd.normal(0., 1e-4) for t in range(T)]]
        return corr

    def setUp(self):
        self.N_CONFIG = 100
        self.folder_name = "files"
        self.folder_name_sim = "files_sim"
        try:
            os.rmdir(self.folder_name)
            os.rmdir(self.folder_name_sim)
        except OSError:
            pass
        if not os.path.exists(self.folder_name):
            os.mkdir(self.folder_name)
        if not os.path.exists(self.folder_name_sim):
            os.mkdir(self.folder_name_sim)
        self.data = []
        self.data_sim = []
        self.file_names = []
        myLattice = Lattice24c()
        self.mass = nprnd.uniform(0.01, 0.3)
        for i in range(self.N_CONFIG):
            # Individual correlators
            numbers = self.makePPCorrelator(self.mass, 1.0, 64)
            params = {"masses": (0.005, 0.01), "config_number": self.N_CONFIG-i,
                      "hadron_type": "PseudoscalarMeson", "gamma_type": "PP",
                      "lattice": myLattice}
            data = {"data": numbers}
            data.update(params)
            self.data.append(data)
            file_name = str(i) + '.pickle'
            self.file_names.append(file_name)
            write_pickle_file(data, os.path.join(self.folder_name, file_name))
            # Do the same for simultaneous
            numbers_sim = self.makeSimCorrelator(self.mass, 1.0, 0.71732, 1.0, 64)
            params_sim = {"masses": (0.005, 0.01), "config_number": self.N_CONFIG-i, "hadron_type": "PseudoscalarMeson",
                          "lattice": myLattice}
            data_sim = {"data": numbers_sim}
            data_sim.update(params_sim)
            self.data_sim.append(data_sim)
            write_pickle_file(data_sim, os.path.join(self.folder_name_sim, file_name))

    def tearDown(self):
        for i in range(self.N_CONFIG):
            file_name = str(i) + '.pickle'
            os.remove(os.path.join(self.folder_name, file_name))
            os.remove(os.path.join(self.folder_name_sim, file_name))
        os.rmdir(self.folder_name)
        os.rmdir(self.folder_name_sim)

    def testFitOneCorrelator(self):
        c = hadron_from_pickle(os.path.join(self.folder_name, self.file_names[0]))
        params = {"fit_range": (3, 32), "guess": {"m": self.mass, "z": 1.0}, "covariant_fit": False,
                  'fit_type': 'Individual'}
        fit_params = c.fit(**params)
        tol = 1e-3
        self.failUnless(np.abs((fit_params['m'] - self.mass)) < tol)
        self.failIf(np.abs((fit_params['m'] - 123.45)) < tol)

    def testCorrelatorIO(self):
        self.assertRaises(IOError, hadron_from_pickle, "doesntexist")

    def testManyCorrelatorIO(self):
        self.assertRaises(OSError, hadron_collection_from_folder, "doesntexist")

    @unittest.skip("Slow")
    def testFitManyCorrelators(self):
        c = hadron_collection_from_folder(self.folder_name)
        params = {"fit_range": (3, 31), "guess": {"m": self.mass, "z": 1.0},
                  "covariant_fit": False, "fit_type": 'Individual'}
        fit_params = c.fit(**params)
        fit_errors = c.fit_errors
        tol = 1e-3
        self.failUnless(np.abs((fit_params['m'] - self.mass)) < tol)
        self.failUnless(fit_errors['m'] < tol)
        self.failIf(np.abs((fit_params['m'] - 123.45)) < tol)

    def testSortCorrelators(self):
        c = hadron_collection_from_folder(self.folder_name, sort=True)
        nums = c.get_config_numbers()
        self.failUnless(nums == list(range(1, self.N_CONFIG + 1)))
        d = hadron_collection_from_folder(self.folder_name, sort=False)
        nums = d.get_config_numbers()
        self.failIf(nums == list(range(1, self.N_CONFIG + 1)))

    def testFitRangeCorrelators(self):
        c = hadron_collection_from_folder(self.folder_name)
        params = {"fit_range": (0, -1), "guess": {"m": self.mass, "z": 0.1}, "covariant_fit": False,
                  'fit_type': 'Individual'}
        self.assertRaises(IndexError, c.fit, **params)

    def testFitOneSimCorrelator(self):
        c = hadron_from_pickle(os.path.join(self.folder_name_sim, self.file_names[0]))
        params = {"fit_range": ((0, 32), (0, 32), (0, 32)),
                  "guess": {"m": self.mass, "z": 1.0, "f": 1.0}, "covariant_fit": False,
                  'fit_type': 'Simultaneous'}
        fit_params = c.fit(**params)
        tol = 1e-3
        self.failUnless(np.abs((fit_params['m'] - self.mass)) < tol)
        self.failIf(np.abs((fit_params['m'] - 123.45)) < tol)

    @unittest.skip("Slow")
    def testFitManySimCorrelators(self):
        c = hadron_collection_from_folder(self.folder_name_sim)
        params = {"fit_range": ((3, 32), (1, 32), (1, 32)),
                  "guess": {"m": self.mass, "z": 1.0, "f": 1.0}, "covariant_fit": False,
                  'fit_type': 'Simultaneous'}
        fit_params = c.fit(**params)
        fit_errors = c.fit_errors
        tol = 1e-3
        self.failUnless(np.abs((fit_params['m'] - self.mass)) < tol)
        self.failUnless(fit_errors['m'] < tol)
        self.failIf(np.abs((fit_params['m'] - 123.45)) < tol)


class BaryonTests(unittest.TestCase):
    @staticmethod
    def makeBaryonCorrelator(m, z, T):
        corr = [PP(t, m, z, T) + nprnd.normal(0., 1e-5) for t in range(T)]
        return corr

    def setUp(self):
        self.N_CONFIG = 100
        self.folder_name = "baryonfiles"
        try:
            os.rmdir(self.folder_name)
        except OSError:
            pass
        if not os.path.exists(self.folder_name):
            os.mkdir(self.folder_name)
        self.data = []
        self.data_sim = []
        self.file_names = []
        myLattice = Lattice24c()
        self.mass = nprnd.uniform(0.01, 0.3)
        for i in range(self.N_CONFIG):
            # Individual correlators
            numbers = self.makeBaryonCorrelator(self.mass, 1.0, 64)
            params = {"masses": (0.005, 0.01), "config_number": self.N_CONFIG-i,
                      "hadron_type": "Baryon",
                      "lattice": myLattice}
            data = {"data": numbers}
            data.update(params)
            self.data.append(data)
            file_name = str(i) + '.pickle'
            self.file_names.append(file_name)
            write_pickle_file(data, os.path.join(self.folder_name, file_name))

    def tearDown(self):
        for i in range(self.N_CONFIG):
            file_name = str(i) + '.pickle'
            os.remove(os.path.join(self.folder_name, file_name))
        os.rmdir(self.folder_name)

    def testFitOneBaryon(self):
        c = hadron_from_pickle(os.path.join(self.folder_name, self.file_names[0]))
        params = {"fit_range": (3, 32), "guess": {"m": self.mass, "z": 1.0}, "covariant_fit": False,
                  'fit_type': 'Individual'}
        fit_params = c.fit(**params)
        tol = 1e-3
        self.failUnless(np.abs((fit_params['m'] - self.mass)) < tol)
        self.failIf(np.abs((fit_params['m'] - 123.45)) < tol)

    def testFitManyBaryons(self):
        c = hadron_collection_from_folder(self.folder_name)
        params = {"fit_range": (3, 31), "guess": {"m": self.mass, "z": 1.0}, "covariant_fit": False,
                  'fit_type': 'Individual'}
        fit_params = c.fit(**params)
        fit_errors = c.fit_errors
        tol = 1e-3
        self.failUnless(np.abs((fit_params['m'] - self.mass)) < tol)
        self.failUnless(fit_errors['m'] < tol)
        self.failIf(np.abs((fit_params['m'] - 123.45)) < tol)