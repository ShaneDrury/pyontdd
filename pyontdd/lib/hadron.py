__author__ = 'srd1g10'
import numpy as np

import pylab

from pyontdd.lib.correlator import CorrelatorFactory
from pyontdd.lib.data_handler import DataHandlerFactory


class Hadron(object):
    """
    Class for Hadrons.

    Parameters
    ----------

    data : array_like
        Numpy array of the data to be fit.

    masses : tuple
        The bare masses of the valence quarks comprising the hadron e.g.::

            masses=(0.005, 0.01)

    gamma_type : string
        The gamma structure of the propagators e.g.::

            gamma_type="AP"

        for Axial-Pseudoscalar.

    hadron_type : string
        The type of Hadron that the data represents e.g.::

            hadron_type="PseudoscalarMeson"

    fit_type : string
        The way we fit the data::

            fit_type="Individual" or "Simultaneous"

    lattice : Lattice
        Object that specifies the aspects of the details of the lattice::

            lattice.lattice_size = {"x": 24, "y": 24, "z": 24, "t": 64, "s": 16}

    config_number : int, optional
        The configuration number that this propagator corresponds to.

    kwargs : dict, optional
        Any other parameters of the hadron e.g. charge of the quarks

    """

    def __init__(self, data, masses=None, gamma_type=None, hadron_type=None, lattice=None,
                 config_number=None, **kwargs):

        #assert isinstance(data, np.ndarray)
        self.data = np.array(data)
        self.masses = masses
        self.config_number = config_number
        self.hadron_type = hadron_type
        self.lattice = lattice
        self.gamma_type = gamma_type
        #self.fit_type = fit_type
        self.other_params = kwargs
        self.all_params = {"masses": masses, "gamma_type": gamma_type, "hadron_type": hadron_type,
                           "lattice": lattice, "config_number": config_number}
        self.all_params.update(self.other_params)

    def fit(self, guess=None, fit_range=None, covariant_fit=False, correlated_fit=False, inv_covar=None,
            error=None, fit_type=None):
        """
        Fit the Hadron based on the parameters given.

        Parameters
        ----------
        guess : dict
        fit_range : tuple
        covariant_fit : bool
        correlated_fit : bool
        inv_covar : ndarray, optional
        error : ndarray
        correlator_fit_type : string
            Override the hadron_type, fit_type and gamma_type and just specify it here.

        """

        corr_fit_type = self.hadron_type + fit_type  # Build up the structure of the hadron
        try:
            corr_fit_type += self.gamma_type  # If it's defined, add on PP, AA or AP
        except TypeError:
            pass

        dhf = DataHandlerFactory()
        dh = dhf.create_data_handler(fit_type)
        pared = dh.pare_data(self.data, fit_range, error=error, inv_covar=inv_covar)
        x = pared['x']
        self.data = pared['data']
        error = pared['error']
        inv_covar = pared['inv_covar']
        q = CorrelatorFactory.create_correlator(corr_fit_type, self.data, lattice=self.lattice)
        self.fit_params = q.fit(guess=guess, fit_range=x, covariant_fit=covariant_fit,
                                correlated_fit=correlated_fit, inv_covar=inv_covar, error=error)
        return self.fit_params

    def plot(self):
        pylab.plot(self.data)
        pylab.yscale('log')
        pylab.show()