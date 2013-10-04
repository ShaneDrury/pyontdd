__author__ = 'srd1g10'
import copy
import minuit
import numpy as np
import logging

import fitfunc as ff


class FitType(object):
    pass


class IndividualPPFitType(FitType):
    @staticmethod
    def fit(cls, guess=None, fit_range=None, covariant_fit=False, correlated_fit=False, inv_covar=None, error=None):
        """
        Fit function for IndividualPP e.g. Pseudoscalar Meson Indidivual PP/AA or Individual Baryon
        """

        if guess is None:
            guess = {"m": 0.3, "z": 0.1}
        cls.fit_setup(fit_range=fit_range, covariant_fit=covariant_fit, correlated_fit=correlated_fit,
                      inv_covar=inv_covar, error=error)  # Set up the fit parameters internally

        if cls.covariant_fit:
            chi2 = lambda m, z: ff.chi2_covariant_individual(ff.PP, {"m": m, "z": z, "T": cls.T}, cls.x, cls.data,
                                                             cls.inv_covar)
        else:
            chi2 = lambda m, z: ff.chi2_uncovariant_individual(ff.PP, {"m": m, "z": z, "T": cls.T}, cls.x, cls.data, cls.error)
        m = minuit.Minuit(chi2)
        m.values = copy.deepcopy(guess)  # Have to deepcopy, otherwise 'guess' gets changed when 'm.values' does
        m.tol = 0.000001
        m.migrad()
        vals = m.values.values()
        fit_params = m.values
        cov_matrix = m.matrix()  # Check covariance matrix is positive definite
        eigs = np.linalg.eig(cov_matrix)[0]
        for e in eigs:
            if e < 1e-6:
                logging.warn("Eigenvalue < 1e-6: {0}".format(e))
        fit_params.update({"chi2": chi2(*vals) / (len(cls.data) - 2.)})
        return fit_params


class SimultaneousMesonFitType(FitType):
    @staticmethod
    def fit(self, guess=None, fit_range=None, covariant_fit=False, correlated_fit=False, inv_covar=None, error=None):
        if guess is None:
            guess = {"m": 0.3, "z": 0.1, "f": 1.0}
        self.fit_setup(fit_range=fit_range, covariant_fit=covariant_fit, correlated_fit=correlated_fit,
                       inv_covar=inv_covar, error=error)  # Set up the fit parameters internally
        if self.covariant_fit:
            chi2 = lambda m, z, f: ff.chi2_covariant_simultaneous({"m": m, "z": z, "f": f, "T": self.T,
                                                                   "Z": self.lattice.Z}, self.x, self.data,
                                                                  self.inv_covar)
        else:
            chi2 = lambda m, z, f: ff.chi2_uncovariant_simultaneous({"m": m, "z": z, "f": f, "T": self.T,
                                                                     "Z": self.lattice.Z}, self.x, self.data,
                                                                    self.error)
        m = minuit.Minuit(chi2)
        m.values = copy.deepcopy(guess)  # Have to deepcopy, otherwise 'guess' gets changed when 'm.values' does
        m.tol = 0.00001
        m.migrad()
        vals = m.values.values()
        fit_params = m.values
        cov_matrix = m.matrix()  # Check covariance matrix is positive definite
        eigs = np.linalg.eig(cov_matrix)[0]
        for e in eigs:
            if e < 1e-6:
                logging.warn("Eigenvalue < 1e-6: {0}".format(e))
        fit_params.update({"chi2": chi2(*vals) / (len(self.data) - 2.)})
        return fit_params