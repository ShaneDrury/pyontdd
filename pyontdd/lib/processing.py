__author__ = 'srd1g10'
import os
import pickle as pck
from pyontdd.lib.io import get_list_of_files
from pyontdd.lib.file_formats import FileFactory


def convert_folder_to_pickle(folder, file_format, output_folder=None, parameters=None):
    if not parameters:
        raise TypeError
    list_of_files = get_list_of_files(folder)
    for f in list_of_files:
        my_file = FileFactory.open(f, file_format)
        d = my_file.extract(**parameters)
        folder_name = my_file.folder_name(**d)
        if not os.path.exists(os.path.join(output_folder, folder_name)):
            os.makedirs(os.path.join(output_folder, folder_name))
        with open(os.path.join(output_folder, folder_name, str(d['config_number']) + '.pickle'), 'wb') as g:
            pck.dump(d, g)
