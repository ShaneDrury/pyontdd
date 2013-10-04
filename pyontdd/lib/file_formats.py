import os
import re
from pyontdd.lib.register import registerFileFormat
from pyontdd.lib.registered_types import RegisteredFileFormats
__author__ = 'srd1g10'

re_scientific = "[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?"  # Matches scientific notation e.g. 1.2345e+06


class FileFactory(object):
    """
    Benefit of doing this is that we can set the file format at run time.
    """
    @staticmethod
    def open(f, format_):
        types = RegisteredFileFormats.types
        return types[format_](f)


class BaseFileClass(object):
    """
    Class for BaseFileClass. Handles various file formats.

    Parameters
    ----------

    f : string
        Path to the file that we read
    """
    def __init__(self, f):
        with open(f, 'r') as g:
            self.data = g.read()
            self.file_path = g.name
            self.filename = os.path.basename(g.name)


@registerFileFormat
class Iwasaki32cMesonFile(BaseFileClass):
    filename_format = ("\w+\.src\d+\."
                       "ch1(?P<charge1>" + re_scientific + ")\."
                       "ch2(?P<charge2>" + re_scientific + ")\."
                       "m1(?P<mass1>" + re_scientific + ")\."
                       "m2(?P<mass2>" + re_scientific + ")\."
                       "dat\.(?P<config_number>\d+)")
    re_one_correl = "^\d+\s\s{res}\s\s{res}".format(res=re_scientific)  # Matches correlator data
    data_format = ("^STARTPROP\n"
                   "^MASSES:\s\s{m1}\s{{3}}{m2}\n"  # Note double {{...}} to ensure {...} survives .format()
                   "^SOURCE:\s{source}\n"
                   "^SINKS:\s{sink}\n"
                   "(?P<data>(" + re_one_correl + "\n)+)"
                   "^ENDPROP")

    def extract(self, source=None, sink=None, lattice=None):
        if not (source and sink and lattice):  # Need to pass all to function, but it's nice for them to be named
            raise TypeError("{0} needs {1} as arguments.".format(self.__class__.__name__, locals().keys()))
        m = re.match(self.filename_format, self.filename)
        if m:
            charge1 = float(m.group('charge1'))
            charge2 = float(m.group('charge2'))
            mass_1 = float(m.group('mass1'))
            mass_2 = float(m.group('mass2'))
            config_number = int(m.group('config_number'))
        else:
            raise re.error("Cannot match filename")
        m1 = "%.6e" % mass_1
        m2 = "%.6e" % mass_2
        m1.replace('.', '\.')  # Ensures the dots are properly escaped
        m2.replace('.', '\.')
        data_re = re.search(self.data_format.format(m1=m1, m2=m2, source=source, sink=sink),
                            self.data, re.MULTILINE)
        if data_re:
            dat = data_re.group('data')  # Extract the numbers
            re_one_correl_group = "\d+\s\s(?P<real>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)"
            m = re.findall(re_one_correl_group, dat, re.MULTILINE)
            if m:
                data = [float(mm[0]) for mm in m]
            else:
                raise re.error("Cannot find data")
        else:
            raise re.error("Cannot find data")
        masses = (mass_1, mass_2)
        charges = (charge1, charge2)
        hadron_type = 'PseudoscalarMeson'
        #lattice = Lattice32c()  # Cannot be determined fully from data, must add manually
        gamma_type = convert_gam_to_pp(source, sink)
        return {'data': data, 'masses': masses, 'charges': charges, 'gamma_type': gamma_type,
                'hadron_type': hadron_type, 'config_number': config_number, 'lattice': lattice}

    @staticmethod
    def folder_name(**kwargs):
        format_dict = {'m1': kwargs['masses'][0], 'm2': kwargs['masses'][1], 'q1': kwargs['charges'][0],
                       'q2': kwargs['charges'][1], 'gam': kwargs['gamma_type']}
        return 'm{m1}.m{m2}.q{q1}.q{q2}.{gam}'.format(**format_dict)


def convert_gam_to_pp(source, sink):
    trans = {'GAM_5': 'P'}
    return ''.join((trans[source], trans[sink]))


def convert_wme_to_pp(source_sink):
    trans = {'bPS_pPS': 'PP'}
    return trans[source_sink]


@registerFileFormat
class Wme32cMesonFile(BaseFileClass):
    filename_format = "wme\.dat\.(?P<config_number>\d+)"  # e.g. wme.dat.508
    re_one_correl = "^{{source_sink}}\s{{t_src}}\s\d+\s\s{res}\s{res}".format(res=re_scientific)
    all_data_format = "MASS=\s{m1}\s{m2}\n^((?!MASS=).*$\n)+"  # Matches between the mass we want and the next mass
    data_format = "(?P<data>(" + re_one_correl + "\n)+)"

    def extract(self, source_sink=None, mass_1=None, mass_2=None, t_src=None, lattice=None):
        if not (source_sink and mass_1 and mass_2 and (t_src == 0) and lattice):
            raise TypeError("{0} needs {1} as arguments.".format(self.__class__.__name__, locals().keys()))
        m = re.match(self.filename_format, self.filename)
        if m:
            config_number = int(m.group('config_number'))
        else:
            raise re.error("Cannot match filename")
        m1 = "%.6e" % mass_1
        m2 = "%.6e" % mass_2
        m1.replace('.', '\.')  # Ensures the dots are properly escaped
        m2.replace('.', '\.')
        all_data_re = re.search(self.all_data_format.format(m1=m1, m2=m2), self.data, re.MULTILINE)
        if all_data_re:
            data_re = re.search(self.data_format.format(source_sink=source_sink, t_src=t_src),
                                all_data_re.group(), re.MULTILINE | re.DOTALL)
        else:
            raise re.error("Cannot find data")
        if data_re:
            dat = data_re.group('data')  # Extract the numbers
            re_one_correl_group = '^\w+\s\d+\s\d+\s\s(?P<real>{res})\s{res}\n'.format(res=re_scientific)
            m = re.findall(re_one_correl_group, dat, re.MULTILINE)
            if m:
                data = [float(mm[0]) for mm in m]
            else:
                raise re.error("Cannot find data")
        else:
            raise re.error("Cannot find data")
        masses = (mass_1, mass_2)
        hadron_type = 'PseudoscalarMeson'
        #lattice = Lattice32c()  # Cannot be determined fully from data, must add manually
        gamma_type = convert_wme_to_pp(source_sink)
        return {'data': data, 'masses': masses, 'gamma_type': gamma_type,
                'hadron_type': hadron_type, 'config_number': config_number, 'lattice': lattice}

    @staticmethod
    def folder_name(**kwargs):
        format_dict = {'m1': kwargs['masses'][0], 'm2': kwargs['masses'][1], 'gam': kwargs['gamma_type']}
        return 'm{m1}.m{m2}.{gam}'.format(**format_dict)
