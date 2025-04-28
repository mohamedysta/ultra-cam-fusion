import cv2, numpy as np, json, argparse
parser = argparse.ArgumentParser()
parser.add_argument('--rows',type=int,default=6)
parser.add_argument('--cols',type=int,default=9)
parser.add_argument('--square',type=float,default=22.0)
args = parser.parse_args()

objp = np.zeros((args.rows*args.cols,3),np.float32)
objp[:,:2] = np.mgrid[0:args.cols,0:args.rows].T.reshape(-1,2)*args.square
obj_pts, img_pts = [], []

cap = cv2.VideoCapture(0)
print('SPACE = capture, ESC = finish')
while True:
    ok, frame = cap.read()
    if not ok: break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray,(args.cols,args.rows),None)
    disp = frame.copy()
    if found: cv2.drawChessboardCorners(disp,(args.cols,args.rows),corners,found)
    cv2.imshow('calib', disp)
    k = cv2.waitKey(1) & 0xFF
    if k==27: break
    if k==32 and found:
        obj_pts.append(objp); img_pts.append(corners)
        print('Captured',len(obj_pts))
cap.release(); cv2.destroyAllWindows()

ret,K,dist,_,_ = cv2.calibrateCamera(obj_pts,img_pts,gray.shape[::-1],None,None)
np.savez('../data/camera_params.npz',K=K,dist=dist)
print('Saved data/camera_params.npz')