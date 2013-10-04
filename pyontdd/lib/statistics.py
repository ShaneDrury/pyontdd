import numpy as np
import math


def jk_error(c, lists):
    s = 0.0
    for l in lists:
        d = c-l
        if math.isnan(d):  # Ignore infinities
            d = 0.0
        s += d*d
    s *= (1.0 - 1.0 / len(lists))
    return np.sqrt(s)


def jackknife(sample, n=1):
    length = len(sample)
    lists = []
    selectevery = int(length/n)
    for j in range(selectevery):
        this_list=[]
        for i in range(length):
            if i % selectevery != j:
                this_list.append(sample[i])
        lists.append(this_list)  # Copy to eventual output
    return lists


def jk_reduce(data, n=1):
    """Returns averaged jackknife lists"""
    lists = [np.average(l, axis=0) for l in jackknife(data, n)]
    return lists