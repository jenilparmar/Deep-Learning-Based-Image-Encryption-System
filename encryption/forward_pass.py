# %%
import numpy as np
import math

# %%
def update_df(R:float , c , d):
    f = np.int64(R) 
    z= c %32
    if z!=0:
        d = (c << (d%z))^d
    else:
        d= d^c
    d = d^ (d<<21)
    d = d ^ (d>>35)
    d  =d ^ (d<<4)
    
    return [f ,d]

# %%
update_df(2.345647768 , 157 , 524592858)

# %%
# ---- Main: Substitute function (forward + backward) ----
def Substitute(B):
    """
    Forward and backward substitution for one image block.
    B: list/array of pixel values [b1, b2, ..., bn]
    Returns: list of final substituted pixels (out)
    """
    n = len(B)
    out1 = []

    # --- Forward pass ---
    f = np.int64(1)  # initial f (non-zero)
    d = np.int64(1)  # initial d (non-zero)

    for bi in B:
        R = 17.32 * math.sqrt(abs(d) / (4 * abs(f) + 1e-9))

        k = int(R) % 256
        si = k ^ bi
        out1.append(si)
        f, d = update_df(R, bi, d)

    # --- Backward pass ---
    out = []
    f = np.int64(1)  # re-initialize f
    d = np.int64(1)  # re-initialize d

    for si in reversed(out1):  # process from right to left
        R = 17.32 * math.sqrt(abs(d) / (4 * abs(f) + 1e-9))

        k = int(R) % 256
        ci = k ^ si
        out.insert(0, ci)  # prepend to maintain original order
        f, d = update_df(R, si, d)

    return out
block = [120, 45, 200, 88]

output = Substitute(block)
print("Input Block: ", block)
print("Output Block:", output)

# %%
def Substitute_Inv(out):
    """
    Inverse substitution for decryption.
    out: encrypted block [c1, c2, ..., cn]
    Returns: original block B
    """
    n = len(out)
    out1 = []

    # --- Backward pass first ---
    f = np.int64(1)
    d = np.int64(1)

    for ci in reversed(out):  # i = n down to 1
        R = 17.32 * math.sqrt(d / (4 * f))
        k = int(R) % 256
        si = k ^ ci
        out1.insert(0, si)  # prepend to maintain order
        f, d = update_df(R, si, d)

    # --- Forward pass second ---
    B = []
    f = np.int64(1)  # re-initialize
    d = np.int64(1)

    for si in out1:  # i = 1 to n
        R = 17.32 * math.sqrt(d / (4 * f))
        k = int(R) % 256
        bi = k ^ si
        B.append(bi)
        f, d = update_df(R, bi, d)

    return B


# %%
# --- Global seeds (persist across calls) ---
Seed_r = np.int64(0)
Seed_c = np.int64(0)

# --- Randomize function ---
def Randomize(seed):
    seed = seed ^ (seed << 21)
    seed = seed ^ (seed >> 35)
    seed = seed ^ (seed << 4)
    seed = seed & 0xFFFFFFFFFFFFFFFF  # keep 64-bit
    return seed

# --- Update function for pixel perturbation ---
def Update(r, c, s, N):
    global Seed_r, Seed_c

    # Ensure Python int (not uint8)
    s = int(s)
    Seed_r = int(Seed_r)
    Seed_c = int(Seed_c)

    # Step 2: Update Seed_r
    Seed_r = Seed_r ^ (s // 256)

    # Step 3: Update Seed_c
    Seed_c = Seed_c ^ (s % 256)

    # Step 4: Update position (example chaotic function)
    r = (r + Seed_r) % N
    c = (c + Seed_c) % N

    return r, c



# %%

def Perturbation(Image):
    """
    Scramble the pixels of Image using chaotic Update function.
    Image: N x N numpy array
    Returns: Image_p (scrambled)
    """
    N = Image.shape[0]  # assuming square image

    # --- Initialize empty output image ---
    Image_p = np.full((N, N), -1, dtype=int)  # -1 means empty

    # --- Initialize positions from logistic map ---
    # For simplicity, we use random numbers here; replace with logistic map if available
    r = np.random.randint(0, N)
    c = np.random.randint(0, N)

    # --- Initialize global seeds ---
    global Seed_r, Seed_c
    Seed_r = np.int64(0)
    Seed_c = np.int64(0)

    # --- Main loop over pixels ---
    for i in range(N):
        for j in range(N):
            pixel = Image[i, j]

            # Try to place pixel at (r, c)
            placed = False
            if Image_p[r, c] == -1:
                Image_p[r, c] = pixel
                placed = True
            else:
                # Collision: search down the column first
                for rr in range(N):
                    if Image_p[rr, c] == -1:
                        Image_p[rr, c] = pixel
                        placed = True
                        r = rr  # update r to where we placed pixel
                        break

                # If still not placed, search next columns
                if not placed:
                    for cc in range(N):
                        for rr in range(N):
                            if Image_p[rr, cc] == -1:
                                Image_p[rr, cc] = pixel
                                r, c = rr, cc
                                placed = True
                                break
                        if placed:
                            break

            # --- Update position using Update function ---
            r, c = Update(r, c, pixel, N)

    return Image_p


# %%
def Perturbation_Inv(Image_p):
    """
    Restore the original image from a scrambled Image_p.
    Image_p: N x N scrambled image
    Returns: restored Image
    """
    N = Image_p.shape[0]
    Image = np.full((N, N), -1, dtype=int)  # initialize output

    # --- Initialize positions using same logistic map as forward ---
    r = np.random.randint(0, N)
    c = np.random.randint(0, N)

    # --- Reset global seeds ---
    global Seed_r, Seed_c
    Seed_r = np.int64(0)
    Seed_c = np.int64(0)

    # --- Main loop over pixels ---
    for i in range(N):
        for j in range(N):
            # Try to get pixel from (r, c)
            pixel = None
            if Image_p[r, c] != -1:
                pixel = Image_p[r, c]
                Image_p[r, c] = -1  # mark as taken
            else:
                # Search down the column first
                for rr in range(N):
                    if Image_p[rr, c] != -1:
                        pixel = Image_p[rr, c]
                        Image_p[rr, c] = -1
                        r = rr
                        break
                # If not found, search next columns
                if pixel is None:
                    found = False
                    for cc in range(N):
                        for rr in range(N):
                            if Image_p[rr, cc] != -1:
                                pixel = Image_p[rr, cc]
                                Image_p[rr, cc] = -1
                                r, c = rr, cc
                                found = True
                                break
                        if found:
                            break

            Image[i, j] = pixel

            # --- Update position using Update function ---
            r, c = Update(r, c, Image[i, j], N)

    return Image


