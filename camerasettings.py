def grasshopper_gain_datasheet():
    G_TRUNC8 = 2**-8
    quantum_efficiency = 0.38
    G_ADU = 0.37
    G_TOT = (G_TRUNC8 / G_ADU) * quantum_efficiency
    return G_TOT
