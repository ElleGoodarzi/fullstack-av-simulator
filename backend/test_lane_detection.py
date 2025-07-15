import pytest
from lane_detection import detect_lane

def test_detect_lane_image():
    position, output = detect_lane(image_path='test_road.jpg')
    assert isinstance(position, float)
    assert -1 <= position <= 1
    assert output == 'output.jpg'

# Add if testing video
# def test_detect_lane_video():
#     position, output = detect_lane(video_path='test_road.mp4')
#     assert isinstance(position, float)
#     assert -1 <= position <= 1
#     assert output == 'output.mp4'