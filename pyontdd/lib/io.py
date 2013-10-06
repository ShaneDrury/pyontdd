import pickle as pck
import os

from pyontdd.lib.hadron import Hadron
from pyontdd.lib.hadron_collection import HadronCollection


def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))


def get_list_of_files(folder):
    """
    Returns list of files in folder with the folder prepended.
    """
    out = sorted_ls(folder)
    if out:
        list_of_files = [os.path.join(folder, f) for f in out]
        return list_of_files
    else:
        raise IOError("Error opening {0}, skipping.".format(folder))


def write_pickle_file(data, filename):
    with open(filename, 'wb') as f:
        pck.dump(data, f)


def read_pickle_file(filename):
    with open(filename, 'rb') as f:
        return pck.load(f)


def hadron_from_pickle(filename):
    out = read_pickle_file(filename)
    return Hadron(**out)


def hadron_collection_from_folder(foldername, sort=True):
    return HadronCollection([hadron_from_pickle(f) for f in get_list_of_files(foldername)], sort=sort)