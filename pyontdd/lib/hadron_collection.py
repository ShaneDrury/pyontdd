from collections import defaultdict
from operator import attrgetter

import numpy as np
import pylab

from pyontdd.lib.hadron import Hadron
from pyontdd.lib.statistics import jk_reduce, jk_error


class HadronCollection(object):
    """
    Class for collections of hadron objects. Defines a natural way to have many estimations of the same hadron that we
    can fit and perform other analysis on.
    """
    def __init__(self, hadrons, sort=True):
        self.hadrons = hadrons
        self.fit_errors = {}
        if sort:
            self._sort_hadrons()
        self._get_central_hadron(self.hadrons)

    def _sort_hadrons(self):
        self.hadrons.sort(key=attrgetter('config_number'))

    def _get_jackknife_lists(self, hadrons):
        jk_data = jk_reduce([h.data for h in hadrons])
        params = hadrons[0].all_params
        li = [Hadron(dat, **params) for dat in jk_data]
        return li

    def _get_central_hadron(self, hadrons):
        """
        Slightly hacky way to get average value of all correlators. We extract the data, average that and then extract
        the parameters of the first hadron - assuming the rest are the same, then instantiate a new hadron of the
        same type as the first.
        """
        average_data = np.average([h.data for h in hadrons], axis=0)  # Seems to work for both ind and sim data
        params = hadrons[0].all_params
        self.central_hadron = Hadron(average_data, **params)

    def _sort_fit_params(self, fit_params):
        fp = defaultdict(list)
        for d in fit_params:
            for k, v in d.items():
                fp[k].append(v)
        return fp

    def _average_fit_params(self, fit_params):
        fp = {}
        for k, v in fit_params.iteritems():
            fp[k] = np.average(v)
        return fp

    def get_config_numbers(self):
        return [h.config_number for h in self.hadrons]

    def fit(self, **kwargs):
        jk_hadrons = self._get_jackknife_lists(self.hadrons)
        all_fit_params = [h.fit(**kwargs) for h in jk_hadrons]
        self.jk_params = self._sort_fit_params(all_fit_params)
        self.central_params = self.central_hadron.fit(**kwargs)
        for k, v in self.central_params.items():
            self.fit_errors[k] = jk_error(v, self.jk_params[k])
        return self.central_params

    def plot(self):
        pylab.plot(self.central_hadron.data)
        pylab.yscale('log')
        pylab.show()
