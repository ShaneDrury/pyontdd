import numpy as np
import logging
from pyontdd.lib.register import registerCorrelator
from pyontdd.lib.registered_types import RegisteredCorrelatorTypes
from pyontdd.lib.fit_types import IndividualPPFitType, SimultaneousMesonFitType


class CorrelatorFactory:
    @staticmethod
    def create_correlator(correlator_fit_type, data, **params):
        types = RegisteredCorrelatorTypes.types  # Get the list of hadrons we can use from here.
                                                 # Registered with @registerHadron decorator
        return types[correlator_fit_type](data, **params)


def registered_correlators():
    """
    Returns list of registered correlator types
    """
    return RegisteredCorrelatorTypes.types


class Correlator(object):
    """
    Class for Correlator. Embodies the way we fit the data.
    """
    def __init__(self, data, lattice=None):
        self.data = data
        self.lattice = lattice
        self.fit_params = None
        self.x = None
        self.error = None
        self.covariant_fit = None
        self.correlated_fit = None
        self.T = None
        self.inv_covar = None

    def fit_setup(self, fit_range=None, covariant_fit=False, correlated_fit=False, inv_covar=None,
                  error=None):
        self.x = fit_range
        if error is None:
            try:
                err_shape = [len(column) for column in self.x]
                error = [np.ones(sh) for sh in err_shape]
            except TypeError:
                error = [1.0 for _ in self.x]
        self.error = error
        if inv_covar is None:  # We cannot do covariant fit if we don't provide this. Warn user.
            if covariant_fit:
                logging.warn('No inverse covariance matrix provided, reverting to uncovariant fit')
            covariant_fit = False
        else:
            self.inv_covar = inv_covar
        self.covariant_fit = covariant_fit
        self.correlated_fit = correlated_fit
        self.T = self.lattice.lattice_size["t"]  # Set total time extent


class Meson(Correlator):
    pass


class PseudoscalarMeson(Meson):
    pass


class VectorMeson(Meson):
    pass


class VectorMesonSim(Meson):
    pass


@registerCorrelator
class VectorMesonIndividual(Meson):
    pass


@registerCorrelator
class PseudoscalarMesonIndividualPP(PseudoscalarMeson):
    """
    Class for Pseudoscalar Meson that is fit individually with gamma structure Psuedoscalar-Pseudoscalar.
    """
    def fit(self, guess=None, fit_range=None, covariant_fit=False, correlated_fit=False, inv_covar=None, error=None):
        self.fit_params = IndividualPPFitType.fit(self, guess, fit_range, covariant_fit, correlated_fit,
                                                  inv_covar, error)
        return self.fit_params


@registerCorrelator
class PseudoscalarMesonSimultaneous(PseudoscalarMeson):
    def fit(self, guess=None, fit_range=None, covariant_fit=False, correlated_fit=False, inv_covar=None, error=None):
        self.fit_params = SimultaneousMesonFitType.fit(self, guess, fit_range, covariant_fit, correlated_fit,
                                                       inv_covar, error)
        return self.fit_params


class Baryon(Correlator):
    pass


@registerCorrelator
class BaryonIndividual(Baryon):
    def fit(self, guess=None, fit_range=None, covariant_fit=False, correlated_fit=False, inv_covar=None, error=None):
        """
        Just do the PP fit - it's the same
        """
        self.fit_params = IndividualPPFitType.fit(self, guess, fit_range, covariant_fit, correlated_fit,
                                                  inv_covar, error)
        return self.fit_params


