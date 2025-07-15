import cv2
import numpy as np
import time

def detect_lane(image_path=None, video_path=None):
    if video_path:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return 0.0, None
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
        total_position = 0.0
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            processed_frame, lane_position = process_frame(frame)
            out.write(processed_frame)
            total_position += lane_position
            frame_count += 1
        cap.release()
        out.release()
        avg_position = total_position / frame_count if frame_count > 0 else 0.0
        return avg_position, 'output.mp4'
    
    img = cv2.imread(image_path) if image_path else None
    if img is None:
        return 0.0, None
    
    processed_img, lane_position = process_frame(img)
    output_path = 'output.jpg'
    cv2.imwrite(output_path, processed_img)
    return lane_position, output_path

def process_frame(frame):
    # Resize for efficiency on M2
    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)  # Low-light optimization
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    
    # Region of interest (bottom half for lanes)
    height, width = edges.shape
    mask = np.zeros_like(edges)
    polygon = np.array([[(0, height), (width, height), (width//2, height//2)]], np.int32)
    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    
    # Hough transform for line detection
    lines = cv2.HoughLinesP(cropped_edges, 2, np.pi/180, 100, minLineLength=40, maxLineGap=5)
    
    lane_position = 0.0
    line_img = np.zeros_like(frame)
    if lines is not None:
        left_fit = []
        right_fit = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 == x1:
                continue  # Avoid division by zero
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            if slope < 0:
                left_fit.append((slope, intercept))
            else:
                right_fit.append((slope, intercept))
        
        def avg_fit(fit):
            if not fit:
                return None
            return np.average(fit, axis=0)
        
        left_avg = avg_fit(left_fit)
        right_avg = avg_fit(right_fit)
        
        def make_line(fit, height):
            if fit is None:
                return None
            slope, intercept = fit
            y1 = height
            y2 = int(height * 0.6)
            x1 = max(0, min(width, int((y1 - intercept) / slope)))
            x2 = max(0, min(width, int((y2 - intercept) / slope)))
            return ((x1, y1), (x2, y2))
        
        left_line = make_line(left_avg, height)
        right_line = make_line(right_avg, height)
        
        if left_line:
            cv2.line(line_img, left_line[0], left_line[1], (0, 255, 0), 10)
        if right_line:
            cv2.line(line_img, right_line[0], right_line[1], (0, 255, 0), 10)
        
        # Calculate lane position (normalized deviation from center: -1 left to 1 right)
        center = width // 2
        left_x = left_line[0][0] if left_line else center - 100
        right_x = right_line[0][0] if right_line else center + 100
        lane_center = (left_x + right_x) // 2
        lane_position = (lane_center - center) / (width / 2)

    # Overlay lines on frame
    return cv2.addWeighted(frame, 1, line_img, 0.8, 0), lane_position

if __name__ == "__main__":
    start = time.time()
    position, output = detect_lane(image_path='test_road.jpg')
    fps = 1 / (time.time() - start)
    print(f"Lane position: {position}")
    print(f"Processing FPS: {fps}")