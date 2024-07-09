import json
import os
import cv2
import face_recognition
import requests
import time


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

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
video_capture = cv2.VideoCapture("rtsp://username:password@ONVIF_URL:554/onvif1",cv2.CAP_FFMPEG)

last_detected_name = None

while True:
    ret, frame = video_capture.read()

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

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

video_capture.release()
cv2.destroyAllWindows()
