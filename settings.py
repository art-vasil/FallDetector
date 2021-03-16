import os

from utils.folder_file_manager import make_directory_if_not_exists

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(CUR_DIR, 'utils', 'model')
ALARM_DIR = make_directory_if_not_exists(os.path.join(CUR_DIR, 'alarm'))

JOINT_COLORS = [
    (0, 0, 255),
    (0, 0, 128), (255, 255, 255), (0, 255, 0), (0, 0, 255),
    (192, 192, 192), (128, 0, 255), (0, 128, 128), (255, 255, 255),
    (128, 128, 0), (128, 128, 128), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255), (0, 0, 128)
]

"""
Pose Data Points

Nose 0, Neck 1, Right Shoulder 2, Right Elbow 3, Right Wrist 4,
Left Shoulder 5, Left Elbow 6, Left Wrist 7, Right Hip 8,
Right Knee 9, Right Ankle 10, Left Hip 11, Left Knee 12,
LAnkle 13, Right Eye 14, Left Eye 15, Right Ear 16,
Left Ear 17, Background 18
"""
POSE_POINTS_NUMBER = 18
POSE_PAIRS = [
    [1, 0], [1, 2], [1, 5], [2, 3], [3, 4], [5, 6], [6, 7],
    [1, 8], [8, 9], [9, 10], [1, 11], [11, 12], [12, 13],
    [0, 14], [0, 15], [14, 16], [15, 17]
]

ALARM_TEXT = "Fall Detected!"

WEB_CAM = True
VIDEO_FILE_PATH = ""
