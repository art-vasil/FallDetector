import logging as log
import os
import sys
import threading
import cv2

import simpleaudio as sa
from openvino.inference_engine import IENetwork, IEPlugin
from src.alarm.player import AlarmPlayer
from settings import JOINT_COLORS, POSE_POINTS_NUMBER, POSE_PAIRS, MODEL_DIR, WEB_CAM, VIDEO_FILE_PATH


class FallDetector:
    def __init__(self):
        self.alarm_file_path = AlarmPlayer().play()
        self.sound_ret = True
        log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)
        log.info("Start Fall Detection")

        # Plugin initialization for specified device
        log.info("Initializing plugin for CPU device...")
        self.plugin = IEPlugin(device="CPU", plugin_dirs=None)

        # Load model
        model_xml = os.path.join(MODEL_DIR, "human-pose-estimation-0001.xml")
        model_bin = os.path.join(MODEL_DIR, "human-pose-estimation-0001.bin")
        log.info("Reading IR...")
        self.net = IENetwork(model=model_xml, weights=model_bin)

    def play_sound(self):
        wave_obj = sa.WaveObject.from_wave_file(self.alarm_file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()

        return

    def run(self, video_file_path=VIDEO_FILE_PATH):
        """Accept arguments and perform the inference on entry"""

        supported_layers = self.plugin.get_supported_layers(self.net)
        not_supported_layers = [layer for layer in self.net.layers.keys() if layer not in supported_layers]
        if len(not_supported_layers) != 0:
            log.error(
                f"""Following layers are not supported by the plugin
                for specified device {self.plugin.device}:\n {not_supported_layers}""")
            log.error(
                """Please try to specify cpu extensions library
                    path in demo's command line parameters using -l
                    or --cpu_extension command line argument
                """
            )
            sys.exit(1)
        input_blob = next(iter(self.net.inputs))

        log.info("Loading IR to the plugin...")
        exec_net = self.plugin.load(network=self.net, num_requests=2)

        # Read and pre-process input image
        n, c, h, w = self.net.inputs[input_blob].shape
        del self.net
        if WEB_CAM:
            cap = cv2.VideoCapture(0)
        else:
            cap = cv2.VideoCapture(video_file_path)
            assert os.path.isfile(video_file_path), "Specified input file doesn't exist"

        # Grab the shape of the input
        height = int(cap.get(4))
        fps = cap.get(cv2.CAP_PROP_FPS)
        font_scale = round(height / 360)
        font_thickness = round(3 * font_scale)

        cur_request_id = 0
        next_request_id = 1
        alarm_thread = None

        # Fall Detection variables
        previous_head_avg_position = 0
        previous_head_detection_frame = 0
        last_fall_detected_frame = 0
        # Fall Detection threshold speed is depedent of the frame height
        fall_threshold = 0.04 * height
        framerate_threshold = round(fps / 5.0)
        fall_detected_text_position = (20, round(0.15 * height))

        ret, frame = cap.read()
        frame_number = 0
        cnt = 0

        while cap.isOpened():
            ret, next_frame = cap.read()
            if not ret:
                break
            # Pre-process inputs
            in_frame = cv2.resize(next_frame, (w, h))
            in_frame = in_frame.transpose((2, 0, 1))
            in_frame = in_frame.reshape((n, c, h, w))

            # Inference
            exec_net.start_async(request_id=next_request_id, inputs={input_blob: in_frame})
            if exec_net.requests[cur_request_id].wait(-1) == 0:
                # Parse detection results of the current request
                res = exec_net.requests[cur_request_id].outputs
                kp_heatmaps = res['Mconv7_stage2_L2']

                threshold = 0.5
                points = []
                head_elements_y_pos = []

                for i in range(POSE_POINTS_NUMBER):
                    # confidence map of corresponding body's part.
                    prob_map = kp_heatmaps[0, i, :, :]

                    # Find global maxima of the probMap.
                    min_val, prob, min_loc, point = cv2.minMaxLoc(prob_map)

                    # Scale the point to fit on the original image
                    x = frame.shape[1] / prob_map.shape[1] * point[0]
                    y = frame.shape[0] / prob_map.shape[0] * point[1]

                    # Add point if the probability is greater than the threshold
                    if prob > threshold:
                        point = (int(x), int(y))

                        # If point is a component of the head (including neck and shoulders) append to the header
                        # elements
                        if i == 0 or i == 1 or i == 2 or i == 5 or i == 14 or i == 15 or i == 16 or i == 17:
                            head_elements_y_pos.append(point[1])
                        points.append(point)
                    else:
                        points.append(None)

                # Draw Skeleton
                for num, pair in enumerate(POSE_PAIRS):
                    part_a = pair[0]
                    part_b = pair[1]
                    if points[part_a] and points[part_b]:
                        cv2.line(frame, points[part_a], points[part_b], JOINT_COLORS[num], 3)

                # Calculate head average position from its components
                if len(head_elements_y_pos) > 0:
                    head_avg_position = sum(head_elements_y_pos)
                    head_avg_position /= len(head_elements_y_pos)
                    # log.info(head_avg_position)

                    # Compare previous head position
                    # to detect if falling
                    if previous_head_detection_frame and \
                            head_avg_position - previous_head_avg_position > fall_threshold and \
                            frame_number - previous_head_detection_frame < framerate_threshold:
                        # print("Fall detected.")
                        last_fall_detected_frame = frame_number

                    previous_head_avg_position = head_avg_position
                    previous_head_detection_frame = frame_number

                # Draw Fall Detection Text if last fall event occurred max 2 seconds ago
                if last_fall_detected_frame and (frame_number - last_fall_detected_frame) <= 2 * fps:
                    if self.sound_ret:
                        alarm_thread = threading.Thread(target=self.play_sound)
                        alarm_thread.start()
                    cv2.putText(frame, "FALL DETECTED!", fall_detected_text_position, cv2.FONT_HERSHEY_COMPLEX,
                                font_scale, (0, 0, 255), font_thickness, cv2.LINE_AA)
                    self.sound_ret = False
            if cnt > 10000:
                cnt = 0
            cnt += 1
            if cnt % 50 == 0:
                self.sound_ret = True

            cv2.imshow("Fall Detection", frame)
            cur_request_id, next_request_id = next_request_id, cur_request_id
            frame = next_frame

            # Increment frame number
            frame_number += 1
            if cv2.waitKey(1) & 0xff == ord('q'):
                break
        if alarm_thread is not None:
            alarm_thread.join()
        cv2.destroyAllWindows()
        cap.release()

        return


if __name__ == '__main__':
    FallDetector().run()
