__author__ = 'srd1g10'
import numpy as np


class DataHandlerIndividual:
    def pare_data(self, data, fit_range, **kwargs):
        x = np.array(range(fit_range[0], fit_range[1] + 1))  # create x range (i.e. t) that we fit
        data = data[x]  # Only uses certain fit range
        if len(data) == 0:  # Some fit ranges will make the data empty. Raise error if this is the case
            raise IndexError
        pared = {"data": data, "x": x}
        for k, v in kwargs.iteritems():  # Handle anything else we throw at it
            if v is None:
                pared[k] = None
            else:
                pared[k] = v[x]
        return pared


class DataHandlerSimultaneous:
    def pare_data(self, data, fit_range, **kwargs):
        rangelam = lambda x: np.arange(x[0], x[1] + 1)
        x = map(rangelam, fit_range)
        y = [d[xx] for d, xx in zip(data, x)]
        y_shape = [len(yy) for yy in y]
        if min(y_shape) == 0:  # Check none of the dimensions are zero
            raise IndexError
        pared = {"data": y, "x": x}
        for k, v in kwargs.iteritems():  # Handle anything else we throw at it
            if v is None:
                pared[k] = None
            else:
                pared[k] = [vv[xx] for vv, xx in zip(v, x)]
        return pared


class DataHandlerFactory(object):
    """
    Handles the data and fit ranges for individual and simultaneous fits.
    """
    types = {"Individual": DataHandlerIndividual, "Simultaneous": DataHandlerSimultaneous}

    def create_data_handler(self, t):
        return self.types[t]()