import numpy as np
import math
import sys

def rodrigues_vec_to_rotation_mat(rodrigues_vec):
    theta = np.linalg.norm(rodrigues_vec)
    if theta < sys.float_info.epsilon:
        rotation_mat = np.eye(3, dtype=float)
    else:
        r = rodrigues_vec / theta
        ident = np.eye(3, dtype=float)
        r_rT = np.array(
            [
                [r[0] * r[0], r[0] * r[1], r[0] * r[2]],
                [r[1] * r[0], r[1] * r[1], r[1] * r[2]],
                [r[2] * r[0], r[2] * r[1], r[2] * r[2]],
            ]
        )
        r_cross = np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]], dtype=float)
        rotation_mat = math.cos(theta) * ident + (1 - math.cos(theta)) * r_rT + math.sin(theta) * r_cross

    return rotation_mat

def get_K_in_pixel_coordinates(focal, width, height):
    f = focal * max(width, height)
    return np.array([[f, 0, 0.5 * (width - 1)],
                        [0, f, 0.5 * (height - 1)],
                        [0, 0, 1.0]])