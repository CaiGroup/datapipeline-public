import numpy as np


def dist3d(p, q):
    "Return the Euclidean distance between points p and q."
    squared_dist = np.sum((p - q) ** 2, axis=0)
    dist = np.sqrt(squared_dist)
    return dist


def take_out_extra_dots(dot_analysis, r=2):
    """Return a maximal list of elements of points such that no pairs of
    points in the result have distance less than r.

    """
    points = dot_analysis[0]

    result_indices = []
    result = []
    for i in range(len(points)):
        if all(dist3d(points[i], q) >= r for q in result):
            result.append(points[i])
            result_indices.append(i)

    dot_analysis[0] = np.take(dot_analysis[0], result_indices, axis=0)
    dot_analysis[1] = np.take(dot_analysis[1], result_indices)

    return dot_analysis
