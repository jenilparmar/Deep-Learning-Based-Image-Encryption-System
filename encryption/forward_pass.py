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
# --- Global seeds (will be set inside perturbation) ---
Seed_r = np.int64(0)
Seed_c = np.int64(0)

def Randomize(seed):
    """64-bit safe randomizer using xorshift pattern — avoids OverflowError."""
    # use unsigned 64-bit (np.uint64) for masking and bitwise operations
    mask = np.uint64(0xFFFFFFFFFFFFFFFF)
    seed = np.uint64(seed) & mask

    seed ^= (seed << np.uint64(21)) & mask
    seed ^= (seed >> np.uint64(35)) & mask
    seed ^= (seed << np.uint64(4)) & mask

    # convert back to signed 64-bit for compatibility with np.int64 operations
    return np.int64(seed & mask)

def Update(r: int, c: int, s: int, N: int, M: int):
    """
    Update row and column positions based on pixel value s (0..255).
    Keeps everything in 64-bit range to avoid overflow.
    """
    global Seed_r, Seed_c

    # Mix pixel into seeds
    Seed_r = np.int64(Seed_r ^ np.int64(s))
    Seed_c = np.int64(Seed_c ^ np.int64((s << 3) | (s >> 5)))

    # Randomize both seeds safely (64-bit masked)
    Seed_r = Randomize(Seed_r)
    Seed_c = Randomize(Seed_c)

    # Map to valid positions
    r_new = int((int(Seed_r) % N) ^ int(r))
    c_new = int((int(Seed_c) % M) ^ int(c))

    # Ensure indices in bounds
    r_new = r_new % N
    c_new = c_new % M

    return r_new, c_new


# %%
def Perturbation(Image: np.ndarray, r_init, c_init):
    global Seed_r, Seed_c
    N, M = Image.shape  # works even if rectangular

    img = np.array(Image, copy=False)

    # ✅ Fix: use (N, M)
    Image_p = np.full((N, M), -1, dtype=int)

    Seed_r = np.int64(0)
    Seed_c = np.int64(0)

    def _map_to_index(v, length):
        if isinstance(v, (float, np.floating)):
            frac = v - math.floor(v)
            return int((frac * length)) % length
        else:
            return int(v) % length

    r = _map_to_index(r_init, N)
    c = _map_to_index(c_init, M)

    for i in range(N):
        for j in range(M):
            pixel = int(img[i, j])

            placed = False
            if Image_p[r, c] == -1:
                Image_p[r, c] = pixel
                placed = True
            else:
                for rr in range(N):
                    if Image_p[rr, c] == -1:
                        Image_p[rr, c] = pixel
                        placed = True
                        r = rr
                        break
                if not placed:
                    outer_break = False
                    for cc in range(M):
                        for rr in range(N):
                            if Image_p[rr, cc] == -1:
                                Image_p[rr, cc] = pixel
                                r, c = rr, cc
                                placed = True
                                outer_break = True
                                break
                        if outer_break:
                            break

            r, c = Update(r, c, pixel, N, M)

    Image_p[Image_p == -1] = 0
    return Image_p.astype(img.dtype)

# %%
def Perturbation_Inv(Image_p , r, c):
    """
    Restore the original image from a scrambled Image_p.
    Image_p: N x N scrambled image
    Returns: restored Image
    """
    N = Image_p.shape[0]
    M = Image_p.shape[1]
    Image = np.full((N, M), -1, dtype=int)  # initialize output

    # --- Initialize positions using same logistic map as forward ---
  

    # --- Reset global seeds ---
    global Seed_r, Seed_c
    Seed_r = np.int64(0)
    Seed_c = np.int64(0)

    # --- Main loop over pixels ---
    for i in range(N):
        for j in range(M):
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
                    for cc in range(M):
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
            r, c = Update(r, c, Image[i, j], N , M)

    return Image


