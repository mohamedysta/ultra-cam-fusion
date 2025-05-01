import cv2, serial, numpy as np, math, argparse, sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--port', default='COM4'); args = parser.parse_args()

# Use absolute paths for data files
base_dir = Path(__file__).parent.parent / 'data'
data = np.load(base_dir / 'camera_params.npz')
K, dist = data['K'], data['dist']
T_sc = np.load(base_dir / 'T_sc.npy')

try:
    ser = serial.Serial(args.port, 115200, timeout=0.1)
except serial.SerialException as e:
    print(f"Error: Could not open serial port {args.port}. {e}")
    sys.exit(1)

cap = cv2.VideoCapture(0)

def sens2cart(th,r):
    th = math.radians(th)
    return np.array([r*math.cos(th), r*math.sin(th), 0, 1])

while True:
    ok, frame = cap.read()
    if ser.in_waiting:
        line = ser.readline().decode().strip()
        if line.count(',')==1:
            th,r = map(float,line.split(','))
            Xs = sens2cart(th,r)
            Xc = T_sc @ Xs
            if Xc[2]>0.05:
                uv = K @ Xc[:3]
                u,v = int(uv[0]/uv[2]), int(uv[1]/uv[2])
                cv2.circle(frame,(u,v),6,(0,0,255),-1)
    cv2.imshow('Projection',frame)
    if cv2.waitKey(1)&0xFF==27: break
cap.release(); cv2.destroyAllWindows(); ser.close()