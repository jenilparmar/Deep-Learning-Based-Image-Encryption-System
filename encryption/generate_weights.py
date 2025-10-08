from logistic_map import calculate_r_and_x
import numpy as np
x ,r = calculate_r_and_x("JenilIsVeryHandSomeGuy")


def create_weights(prev, num):
    x_weights = []
    for _ in range(num):
        x_temp = prev * (1 - prev) * r
        x_weights.append(x_temp)
        prev = x_temp
    return np.array(x_weights)

