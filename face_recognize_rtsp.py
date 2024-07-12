import json
import os
import cv2
import face_recognition
import requests
import time
import numpy as np
import ffmpeg


def load_known_faces(base_dir='ids'):
    known_face_encodings = []
    known_face_names = []

    for person_name in os.listdir(base_dir):
        person_dir = os.path.join(base_dir, person_name)
        if os.path.isdir(person_dir):
            for filename in os.listdir(person_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(person_dir, filename)
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)

                    if face_encodings:
                        encoding = face_encodings[0]
                        known_face_encodings.append(encoding)
                        known_face_names.append(person_name)

    return known_face_encodings, known_face_names


def send_api_request(name):
    url = "https://HOME_ASSISTANT_URL/api/webhook/say_my_name"
    payload = json.dumps({"name": name})
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        print(f"Success API call: {name}")
    except requests.exceptions.RequestException as e:
        print(f"Unsuccessfull API call: {e}")

known_face_encodings, known_face_names = load_known_faces()

rtsp_url = "rtsp://user:password@IP:port/onvif1"

process = (
    ffmpeg
    .input(rtsp_url, rtsp_transport="udp", buffer_size="20M")
    .output('pipe:', format='rawvideo', pix_fmt='rgb24', vsync='drop', preset='ultrafast', tune='zerolatency')
    .overwrite_output()
    .run_async(pipe_stdout=True)
)

width, height = 1280, 720


last_detected_name = None
last_send_time = time.time()
send_interval = 60

frame_count = 0
process_this_frame = True

process_this_frame = True
frame_skip = 30  # Her 30 karede bir işlem yap

while True:
    try:

        in_bytes = process.stdout.read(width * height * 3)
        if not in_bytes:
            break
        frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if process_this_frame:
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

        process_this_frame = not process_this_frame
        frame_skip -= 1
        if frame_skip == 0:
            process_this_frame = True
            frame_skip = 30

        current_time = time.time()
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

                if name != last_detected_name or (current_time - last_send_time) >= send_interval:
                    send_api_request(name)
                    last_detected_name = name
                    last_send_time = current_time
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        print(f"Something went wrong: {e}")
        print("The program is restarting...")

video_capture.release()
cv2.destroyAllWindows()