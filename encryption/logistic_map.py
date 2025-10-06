import numpy as np 
from SHA_function import create_sha_key
import math




# take hash value in list and input and returns the r and x value as array
def calculate_r_and_x(h): 
    r = 0
    x  = 0
    
    r_star = 0
    for i in range(32):
        value = int(h[i], 16)  # convert hex to integer
        r_star += value * math.log(math.pow(256, 32 - i))
    x_star = 0
    x_star = 0
    for i in range(33, 65): # Corresponds to i from 33 to 64
        value = int(h[i-1], 16) # h is 0-indexed
        x_star += value * math.log(math.pow(256, 64 - i))
    x = x_star - int(x_star)
    r = 3.57 + (r_star - int(r_star) )*0.43   
    return [x , r]



h= list(create_sha_key("JenilParmarIsGreatCoder"))


print(calculate_r_and_x(h))