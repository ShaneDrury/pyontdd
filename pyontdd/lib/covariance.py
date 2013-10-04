import numpy as np


def get_cov(X, Y):
    #(1/(n - 1)) \sum_{i = 1}^{n} (x_i - \Hat x) (y_i - \Hat y)
    N = len(X)
    mean_x = np.average(X)
    mean_y = np.average(Y)
    total = np.sum([(x - mean_x)*(y - mean_y) for x, y in zip(X, Y)])
    cov = 1.0 / (N - 1.0) * total
    return cov


def get_inverse_cov_matrix(M, COR_FIT=False):
    Ndata = len(M)
    Nconf = len(M[0])
    cov_matrix = np.zeros((Ndata, Ndata))
    for i in range(Ndata):
        row_i = M[i, :]
        for j in range(Ndata):
            row_j = M[j, :]
            if i != j and not COR_FIT:
                continue
            temp = get_cov(row_i, row_j) / Nconf
            cov_matrix[i][j] = temp
    cov_matrix = np.matrix(cov_matrix)
    invcov = cov_matrix.I
    return invcov