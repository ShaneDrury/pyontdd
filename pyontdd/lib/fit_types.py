__author__ = 'srd1g10'
import copy
import minuit
import logging

import numpy as np

import pyontdd.lib.fitfunc as ff


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
            chi2 = lambda m, z: ff.chi2_uncovariant_individual(ff.PP, {"m": m, "z": z, "T": cls.T}, cls.x, cls.data,
                                                               cls.error)
        fitter = minuit.Minuit(chi2)
        fitter.values = copy.deepcopy(guess)  # Have to deepcopy, otherwise 'guess' gets changed when 'm.values' does
        fitter.tol = 0.00001
        fitter.migrad()
        vals = fitter.values.values()
        fit_params = fitter.values
        cov_matrix = fitter.matrix()  # Check covariance matrix is positive definite
        eigs = np.linalg.eig(cov_matrix)[0]
        for e in eigs:
            if e < 1e-6:
                logging.warning("Eigenvalue < 1e-6: {0}".format(e))
        fit_params.update({"chi2": chi2(*vals) / (len(cls.data) - 2.)})
        return fit_params


class SimultaneousMesonFitType(FitType):
    @staticmethod
    def fit(cls, guess=None, fit_range=None, covariant_fit=False, correlated_fit=False, inv_covar=None, error=None):
        if guess is None:
            guess = {"m": 0.3, "z": 0.1, "f": 1.0}
        cls.fit_setup(fit_range=fit_range, covariant_fit=covariant_fit, correlated_fit=correlated_fit,
                      inv_covar=inv_covar, error=error)  # Set up the fit parameters internally
        if cls.covariant_fit:
            chi2 = lambda m, z, f: ff.chi2_covariant_simultaneous({"m": m, "z": z, "f": f, "T": cls.T,
                                                                   "Z": cls.lattice.Z}, cls.x, cls.data,
                                                                  cls.inv_covar)
        else:
            chi2 = lambda m, z, f: ff.chi2_uncovariant_simultaneous({"m": m, "z": z, "f": f, "T": cls.T,
                                                                     "Z": cls.lattice.Z}, cls.x, cls.data,
                                                                    cls.error)
        fitter = minuit.Minuit(chi2)
        fitter.values = copy.deepcopy(guess)  # Have to deepcopy, otherwise 'guess' gets changed when 'm.values' does
        fitter.tol = 0.0001
        fitter.migrad()
        vals = fitter.values.values()
        fit_params = fitter.values
        cov_matrix = fitter.matrix()  # Check covariance matrix is positive definite
        eigs = np.linalg.eig(cov_matrix)[0]
        for e in eigs:
            if e < 1e-6:
                logging.warning("Eigenvalue < 1e-6: {0}".format(e))
        fit_params.update({"chi2": chi2(*vals) / (len(cls.data) - 2.)})
        return fit_params