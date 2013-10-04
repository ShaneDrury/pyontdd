import unittest
import os
import numpy.random as nprnd
import numpy as np
from pyontdd.lib.file_formats import FileFactory

from pyontdd.lib.io import hadron_from_pickle, write_pickle_file
from pyontdd.lib.lattice import Lattice24c, Lattice32c


class IOTests(unittest.TestCase):

    def setUp(self):
        self.folder_name = "files"
        os.mkdir(self.folder_name)
        self.data = []
        self.file_names = []
        myLattice = Lattice24c()
        for i in range(50):
            numbers = nprnd.random(100)
            params = {"masses": (0.005, 0.01), "config_number": i, "hadron_type": "PseudoscalarMeson",
                      "fit_type": "Individual", "lattice_size": myLattice}
            data = {"data": numbers}
            data.update(params)
            self.data.append(data)
            file_name = str(i) + '.pickle'
            self.file_names.append(file_name)
            write_pickle_file(data, os.path.join(self.folder_name, file_name))

    def tearDown(self):
        for i in range(50):
            file_name = str(i) + '.pickle'
            os.remove(os.path.join(self.folder_name, file_name))
        os.rmdir(self.folder_name)

    def testReadCorrelator(self):
        c = hadron_from_pickle(os.path.join(self.folder_name, self.file_names[0]))
        self.failUnless(np.array_equal(c.data, self.data[0]['data'])
                        and c.masses == self.data[0]['masses']
                        and c.config_number == self.data[0]['config_number']
                        and c.hadron_type == self.data[0]['hadron_type'])

    def testFailReadCorrelator(self):
        c = hadron_from_pickle(os.path.join(self.folder_name, self.file_names[0]))
        self.failIf(np.array_equal(c.data, self.data[1]['data'])
                    or c.masses == (0.02, 0.4, 123)
                    or c.config_number == 12432
                    or c.hadron_type == "ASD")

    def testFailReadFolder(self):
        self.assertRaises(IOError, hadron_from_pickle, "doesntexist")


class IOExtractionTests(unittest.TestCase):

    def setUp(self):
        self.iwasaki_lattice = Lattice32c()
        baseIWASAKI32cfilename = 'meson_BOX_RELOADED.src0.ch1-0.3333333333.ch2-0.3333333333.m10.03.m20.03.dat'
        baseIWASAKI32cfilename2 = 'meson_BOX_RELOADED.src0.ch10.3333333333.ch2-0.3333333333.m10.03.m20.03.dat'
        self.IWASAKI32cfile = os.path.join('testfiles', baseIWASAKI32cfilename + '.510')
        self.IWASAKI32cfile2 = os.path.join('testfiles', baseIWASAKI32cfilename2 + '.530')
        self.wme32cfile = os.path.join('testfiles', 'wme.dat.500')
        self.wme32cfile2 = os.path.join('testfiles', 'wme.dat.508')

    def tearDown(self):
        pass

    def testExtractIWASAKI32c(self):
        my_file = FileFactory.open(self.IWASAKI32cfile, 'Iwasaki32cMesonFile')
        my_file2 = FileFactory.open(self.IWASAKI32cfile2, 'Iwasaki32cMesonFile')
        my_data = my_file.extract('GAM_5', 'GAM_5', self.iwasaki_lattice)
        my_data2 = my_file2.extract('GAM_5', 'GAM_5', self.iwasaki_lattice)
        self.failUnless(my_data['data'][0] == 4.984743e+06)
        self.failUnless(my_data['config_number'] == 510)
        self.failUnless(my_data['charges'] == (-0.3333333333, -0.3333333333))
        self.failUnless(my_data['masses'] == (0.03, 0.03))
        self.failIf(my_data2['data'][0] == 4.984743e+06)
        self.failIf(my_data2['config_number'] == 510)
        self.failIf(my_data2['charges'] == (-0.3333333333, -0.3333333333))

    def testExtractWme32c(self):
        my_file = FileFactory.open(self.wme32cfile, 'Wme32cMesonFile')
        my_file2 = FileFactory.open(self.wme32cfile2, 'Wme32cMesonFile')
        my_data = my_file.extract('bPS_pPS', 0.055, 0.055, 0, self.iwasaki_lattice)
        my_data2 = my_file2.extract('bPS_pPS', 0.055, 0.055, 0, self.iwasaki_lattice)
        self.failUnless(my_data['data'][0] == 4.9167179302929398e+06)
        self.failIf(my_data2['data'][0] == 4.9167179302929398e+06)

