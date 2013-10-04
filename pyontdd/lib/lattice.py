class Lattice:
    pass


class Lattice24c(Lattice):
    lattice_size = {"x": 24, "y": 24, "z": 24, "t": 64, "s": 16}
    a_inv = 1.78
    a_inv_err = 0.03
    Z = 0.71732


class Lattice32c(Lattice):
    lattice_size = {"x": 32, "y": 32, "z": 32, "t": 64, "s": 16}
    a_inv = 2.28
    a_inv_err = 0.03
    Z = 0.74522

