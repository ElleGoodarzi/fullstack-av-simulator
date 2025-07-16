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
        out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (640, 480))
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
    # Resize and enhance
    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 40, 120)  # Tuned for more edges on curves
    
    # Wider ROI for curved roads
    height, width = edges.shape
    mask = np.zeros_like(edges)
    polygon = np.array([[(0, height), (width, height), (width, height * 0.55), (0, height * 0.55)]], np.int32)
    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    
    # Hough with tuned params
    lines = cv2.HoughLinesP(cropped_edges, 1, np.pi/180, 20, minLineLength=10, maxLineGap=200)
    
    lane_position = 0.0
    line_img = np.zeros_like(frame)
    if lines is not None:
        left_x, left_y, right_x, right_y = [], [], [], []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 == x1:
                continue
            slope = (y2 - y1) / (x2 - x1)
            if abs(slope) < 0.3:  # Stricter to skip horizontal noise
                continue
            intercept = y1 - slope * x1
            if slope < -0.3:
                left_x.extend([x1, x2])
                left_y.extend([y1, y2])
            elif slope > 0.3:
                right_x.extend([x1, x2])
                right_y.extend([y1, y2])
        
        def fit_line(x, y):
            if len(x) < 2:
                return None
            return np.polyfit(y, x, 2)
        
        left_fit = fit_line(left_x, left_y)
        right_fit = fit_line(right_x, right_y)
        
        def make_points(fit, height):
            if fit is None:
                return None
            y = np.linspace(int(height * 0.5), height, 30, dtype=int)  # More points for smoother curve
            x = fit[0] * y**2 + fit[1] * y + fit[2]
            x = np.clip(x, 0, width)
            points = np.array([x, y]).T.astype(np.int32)
            return points
        
        left_points = make_points(left_fit, height)
        right_points = make_points(right_fit, height)
        
        if left_points is not None:
            cv2.polylines(line_img, [left_points], False, (0, 255, 0), 10)
        if right_points is not None:
            cv2.polylines(line_img, [right_points], False, (0, 255, 0), 10)
        
        # Average position at multiple heights for stability
        positions = []
        for h in [height, int(height * 0.8), int(height * 0.6)]:
            left_x_h = left_fit[0] * h**2 + left_fit[1] * h + left_fit[2] if left_fit is not None else 200
            right_x_h = right_fit[0] * h**2 + right_fit[1] * h + right_fit[2] if right_fit is not None else width - 200
            lane_center_h = (left_x_h + right_x_h) / 2
            positions.append((lane_center_h - width / 2) / (width / 2))
        lane_position = np.mean(positions) if positions else 0.0

    return cv2.addWeighted(frame, 0.8, line_img, 1, 0), lane_position

if __name__ == "__main__":
    start = time.time()
    position, output = detect_lane(image_path='test_road.jpg')
    fps = 1 / (time.time() - start)
    print(f"Lane position: {position}")
    print(f"Processing FPS: {fps}")