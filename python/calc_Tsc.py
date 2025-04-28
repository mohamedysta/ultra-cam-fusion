import numpy as np, cv2
import json  # pylint: disable=unused-import

K,dist = np.load('../data/camera_params.npz').values()
# --- Fill these arrays with your measured points -------------
pts_sensor = np.float32([[0.10,0.00,0],
                         [0.15,0.05,0],
                         [0.20,-0.04,0]])
pts_img    = np.float32([[320,200],
                         [300,180],
                         [340,220]])
# -------------------------------------------------------------
ok,rvec,tvec = cv2.solvePnP(pts_sensor,pts_img,K,dist,flags=cv2.SOLVEPNP_ITERATIVE)
R,_ = cv2.Rodrigues(rvec)
T = np.eye(4); T[:3,:3]=R; T[:3,3]=tvec.T
np.save('../data/T_sc.npy',T)
print('Saved data/T_sc.npy')