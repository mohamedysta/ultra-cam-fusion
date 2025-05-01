

import numpy as np, cv2
K, dist = np.load('data/camera_params.npz').values()
print(K)
print(dist)        # should print your five numbers