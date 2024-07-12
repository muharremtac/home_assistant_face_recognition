Bu proje https://github.com/ageitgey/face_recognition adresindeki yüz tanıma kütüphanesini kullanmaktadır.

ids dizininde kişi ismimlerine ait dizinlerden aldığı kişi isimlerini web kamerasından, mjpeg sunucusundan ve rtsp kameradan görüntü alabilmektedir.

https://HOME_ASSISTANT_URL/api/webhook/say_my_name adresi ile oluşturduğunuz webhook adresine kişi isimlerini göndermektedir.

Kendi Home Assistant sunucunuzda çalıştırmak için HOME_ASSISTANT_URL adresini kendi sunucunuzun adresi ile değiştirmeniz gerekmektedir.

## Yükleme

git clone https://github.com/muharremtac/home_assistant_face_recognition.git

cd home_assistant_face_recognition

Uygulamayı pip veya conda ile yükleyebilirsiniz.

### pip yüklemesi:

* `python3 -m venv face_recognize`
* `pip3 install -r requirements.txt`

#### Linux/Mac için
* `source face_recognize/bin/activate`

#### Windows için
* `face_recognize\Scripts\activate`

#### conda yüklemesi:
* `conda config --append channels conda-forge`
* `conda config --append channels bioconda`
* `conda create -n face_recognize python=3.11 ffmpeg-python cudatoolkit dlib face_recognition opencv numpy requests`
* `conda activate face_recognize`

## Çalıştırma:

USB kamera ile çalıştırmak için:
* `python3 face_recognize_usb_webcam.py`

MJPEG sunucusu ile çalıştırmak için:
* `python3 face_recognize_mjpeg.py`

RTSP / onvif kamera ile çalıştırmak için:
* `python3 face_recognize_rtsp.py`