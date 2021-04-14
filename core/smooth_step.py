import numpy as np
#from scipy.special import comb

def smoothstep(x, x_min=0, x_max=1):
    if x < x_min:
        return 0
    if x > x_max:
        return 1.

    x = np.clip((x - x_min) / (x_max - x_min), 0, 1)
    return x


    # result = 0
    # for n in range(0, N + 1):
    #      result += comb(N + n, n) * comb(2 * N + 1, N - n) * (-x) ** n
    #
    # result *= x ** (N + 1)
    #
    # return result
