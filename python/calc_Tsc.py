import math
from pathlib import Path
import sys
import numpy as np, cv2
import json  # pylint: disable=unused-import
import os

PARAM_FILE = Path('data/camera_params.npz')

if PARAM_FILE.exists():
    print('Loading intrinsics from', PARAM_FILE)
    data = np.load(PARAM_FILE)
    K    = data['K']
    dist = data['dist']
else:
    # ---------- ONLY EDIT HERE IF .npz DOES NOT EXIST --------------
    # Example K (3×3)  and your distortion vector (1×5)
    # Replace the numbers with *your* calibrated values.
    K = np.array([[688.8606520684872, 0, 321.9162150015034], [0, 689.3555248266161, 272.1847524568002], [0, 0, 1]], dtype=np.float32)

    dist = np.array([[
        -0.24521122408380058,
         1.1418835708597352,
        -0.0009097603254697011,
         0.0022192360604281727,
        -1.9751280035692884
    ]], dtype=np.float32)

print('K =\n', K)
print('dist =', dist.ravel())


# -------------------------------------------------------------------
# HELPER: polar (θ,r)  →  Cartesian (x,y,0) in sensor frame
# -------------------------------------------------------------------
def polar_to_cart(theta_deg: float, r_m: float):
    th = math.radians(theta_deg)
    return (r_m * math.cos(th),
            r_m * math.sin(th),
            0.0)                       # z = 0 in sensor plane

# -------------------------------------------------------------------
# B)  MEASURED CORRESPONDENCE POINTS  -------------------------------
# -------------------------------------------------------------------
# Edit the list `pairs` so that each row is:
#     (theta_deg ,  range_m ,  u_px ,  v_px)
#
# You need at least 3, but 5–10 spread across the image is better.
# -------------------------------------------------------------------
pairs = [
    # θ ° ,   r m ,   u px , v px
    (  0.0 , 0.80 ,   320  , 240 ),
    (-25.0 , 0.90 ,   420  , 250 ),
    ( 30.0 , 0.75 ,   250  , 235 ),
    ( 55.0 , 1.10 ,   180  , 235 ),
    (-45.0 , 1.20 ,   500  , 265 ),
]

# Convert lists to numpy arrays
pts_sensor = np.float32([polar_to_cart(th, r) for th, r, _, _ in pairs])
pts_img    = np.float32([[u, v]               for _, _, u, v in pairs])
SCALE = 1000.0      # convert metres ➔ millimetres
pts_sensor = np.float32([
    [x*SCALE, y*SCALE, 0]  for (x,y,_) in pts_sensor
])
print(f'{len(pairs)} correspondences loaded')

print('pts_sensor =\n', pts_sensor)
if len(pairs) < 3:
    sys.exit('Need at least 3 point pairs!')

# -------------------------------------------------------------------
# SOLVE PnP  ---------------------------------------------------------
# -------------------------------------------------------------------
IMG_H = 480    # change if different
best = 1e9
best_pts = None
for swap in [False, True]:
    for flip in [False, True]:
        test = np.float32([
            [v if swap else u,
             (IMG_H-1-v) if flip else (u if swap else v)]
            for _,_,u,v in pairs])
        ok,rvec,tvec = cv2.solvePnP(pts_sensor, test, K, dist, flags=0)
        if ok:
            pr,_ = cv2.projectPoints(pts_sensor,rvec,tvec,K,dist)
            err = cv2.norm(test, pr.reshape(-1,2), cv2.NORM_L2)/math.sqrt(len(pairs))
            if err < best: best, best_pts = err, test
print('best RMS', best)
pts_img = best_pts       # keep the winner



ok, rvec, tvec = cv2.solvePnP(
        pts_sensor, pts_img,
        K, dist,
        flags=cv2.SOLVEPNP_ITERATIVE)

if not ok:
    sys.exit('solvePnP failed — check your points')

R, _ = cv2.Rodrigues(rvec)
T_sc = np.eye(4, dtype=np.float32)
T_sc[:3, :3] = R
T_sc[:3,  3] = tvec[:, 0]

# -------------------------------------------------------------------
# REPORT & SAVE  -----------------------------------------------------
# -------------------------------------------------------------------
proj, _ = cv2.projectPoints(pts_sensor, rvec, tvec, K, dist)
error = cv2.norm(pts_img, proj.reshape(-1,2), cv2.NORM_L2) / math.sqrt(len(pairs))
print(f'RMS reprojection error: {error:.2f} px')
# ----------  DEBUG each correspondence -----------------------------
for (th, r, u, v), (u2, v2) in zip(pairs, proj.reshape(-1, 2)):
    err = math.hypot(u - u2, v - v2)
    print(f'{th:+06.1f}°  {r:4.2f} m  |  ({u:4},{v:4})  ->  '
          f'({u2:6.1f},{v2:6.1f})  = {err:6.1f} px')
# Save the transformation matrix T_sc to a file
output_dir = Path(__file__).parent.parent / 'data'  # Use absolute path
output_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

np.save(output_dir / 'T_sc.npy', T_sc)
print(f'Saved {output_dir / "T_sc.npy"}')