import numpy as np


def add_z_col(dot_analysis, z):
    number_of_dots = dot_analysis[0].shape[0]

    z_column = np.full((number_of_dots, 1), z)

    dot_analysis[0] = np.append(dot_analysis[0], z_column, 1)

    return dot_analysis
