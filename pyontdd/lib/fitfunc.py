import numpy as np
# TODO Implement chi2_covariant_simultaneous


def PP(t, m, z, T):
    return 0.5*z*z/m*(np.exp(-m*t) + np.exp(-m*(T-t)))


def AA(t, m, f, Z, T):
    return 0.5*f*f*m/(Z*Z)*(np.exp(-m*t) + np.exp(-m*(T-t)))


def AP(t, m, z, f, Z, T):
    return 0.5*z*f/Z*(np.exp(-m*t) - np.exp(-m*(T-t)))

PPlam = lambda t, m, z, f, Z, T: PP(t, m, z, T)
AAlam = lambda t, m, z, f, Z, T: AA(t, m, f, Z, T)
APlam = lambda t, m, z, f, Z, T: AP(t, m, z, f, Z, T)


def chi2_uncovariant_simultaneous(args, x, y, errs):
    c2 = 0.
    funcs = [PPlam, AAlam, APlam]
    for xx, yy, ee, f in zip(x, y, errs, funcs):
        for xxx, yyy, eee in zip(xx, yy, ee):
            c2 += (f(xxx, **args) - yyy / eee)**2
    return c2


def chi2_uncovariant_individual(func, args, x, y, errs):
    c2 = sum([((func(xx, **args) - yy) / err) ** 2 for xx, yy, err in zip(x, y, errs)])
    return c2


def chi2_covariant_individual(func, args, x, y, inv_covar):
    v = np.array(func(x, **args) - y)
    M = np.array(inv_covar)
    r = np.dot(M, v)
    c2 = np.dot(v, r)
    return c2
