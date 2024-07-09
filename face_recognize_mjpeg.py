import face_recognition
import cv2
import os
import numpy as np
import json
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


def get_jpeg(stream):
    bytes_array = bytes()
    for chunk in stream.iter_content(chunk_size=1024):
        bytes_array += chunk
        a = bytes_array.find(b'\xff\xd8')
        b = bytes_array.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes_array[a:b + 2]
            bytes_array = bytes_array[b + 2:]
            return jpg
    return None


known_face_encodings, known_face_names = load_known_faces()

stream_url = "http://MJPEG_URL:8081/webcam/?action=stream"
stream = requests.get(stream_url, stream=True)

last_detected_name = None
last_send_time = 0
send_interval = 60

while True:
    try:
        jpg = get_jpeg(stream)
        if jpg is None:
            print("Failed to receive frame, trying again...")
            continue

        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            print("Frame could not be decoded, trying again...")
            continue

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
    except Exception as e:
        print(f"Something went wrong: {e}")
        print("The program is restarting...")
        stream = requests.get(stream_url, stream=True)

cv2.destroyAllWindows()