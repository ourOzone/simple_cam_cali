import numpy as np
import cv2 as cv

def select_imgs_from_vids(vid_file, f_interval = 10):
    vid = cv.VideoCapture(vid_file)
    selected_imgs = []

    if vid.isOpened():
        frame_cnt = 0
        while True:
            valid, img = vid.read()
            if not valid:
                break
            if not frame_cnt:
                selected_imgs.append(img)
            frame_cnt = (frame_cnt + 1) % f_interval

    return selected_imgs

def calib_cam(imgs, board_shape, cell_size):
    img_pts = []
    for img in imgs:
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        complete, pts = cv.findChessboardCorners(gray, board_shape)
        if complete:
            img_pts.append(pts)

    obj = [[x, y, 0] for y in range(board_shape[1]) for x in range(board_shape[0])]
    obj_pts = [np.array(obj, dtype = np.float32) * cell_size] * len(img_pts)

    return cv.calibrateCamera(obj_pts, img_pts, gray.shape[::-1], None, None)

def print_calib_result(cal_data):
    rms, K, dist_coeff, rvecs, tvecs = cal_data

    print("\n## Camera Calibration Results")
    print(f"  RMS error : {rms:.4f}")
    print(f"  fx, fy    : {K[0,0]:.2f}, {K[1,1]:.2f}")
    print(f"  cx, cy    : {K[0,2]:.2f}, {K[1,2]:.2f}")
    print(f"  dist_coeff: {dist_coeff[0].round(4)}")
    print(f"  num images: {len(rvecs)}")

def rmv_dist(vid_file, cal_data):
    vid = cv.VideoCapture(vid_file)
    rms, K, dist_coeff, rvecs, tvecs = cal_data
    if vid.isOpened():
        w, h = int(vid.get(cv.CAP_PROP_FRAME_WIDTH)), int(vid.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = vid.get(cv.CAP_PROP_FPS)
        map1, map2 = cv.initUndistortRectifyMap(K, dist_coeff, None, None, (w, h), cv.CV_32FC1)
        out = cv.VideoWriter("no_dist.mp4",  cv.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

        while True:
            vaild, frame = vid.read()
            if not vaild:
                break
            rectified = cv.remap(frame, map1, map2, interpolation = cv.INTER_LINEAR)
            out.write(rectified)
        vid.release()
        out.release()

vid_file = "./vid1.mp4"
imgs = select_imgs_from_vids(vid_file)
cal_data = calib_cam(imgs, (10, 7), 0.02)
print_calib_result(cal_data)
rmv_dist(vid_file, cal_data)
