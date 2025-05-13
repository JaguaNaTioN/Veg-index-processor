import numpy as np

def safe_divide(numerator, denominator):
    with np.errstate(divide='ignore', invalid='ignore'):
        result = numerator / denominator
        result[np.isnan(result)] = 0
        return result

def calculate_ndvi(nir, red):
    return safe_divide(nir - red, nir + red)

def calculate_savi(nir, red, L=0.5):
    return safe_divide((nir - red), (nir + red + L)) * (1 + L)

def calculate_evi(nir, red, blue, G=2.5, C1=6, C2=7.5, L=1):
    return G * safe_divide((nir - red), (nir + C1 * red - C2 * blue + L))

def calculate_arvi(nir, red, blue):
    red_corr = red - (2 * (red - blue))
    return safe_divide(nir - red_corr, nir + red_corr)

def calculate_nbr(nir, swir2):
    return safe_divide(nir - swir2, nir + swir2)

def calculate_nbwi(green, nir):
    return safe_divide(green - nir, green + nir)

def calculate_ndbi(swir1, nir):
    return safe_divide(swir1 - nir, swir1 + nir)

def calculate_gci(nir, green):
    return safe_divide(nir, green) - 1
