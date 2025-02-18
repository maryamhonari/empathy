from __future__ import print_function
import keras.backend as K
from keras.preprocessing.image import ImageDataGenerator # for data augmentation if needed
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, normalization
from keras.layers import Convolution2D, MaxPooling2D
from keras import regularizers
from keras.optimizers import SGD, adam, RMSprop
from keras.utils import np_utils
from keras.utils.np_utils import to_categorical
from keras.callbacks import ReduceLROnPlateau, ModelCheckpoint
# from log import save_model, save_config, save_result
from keras.models import model_from_json
import numpy as np
import time
import os
# from model0_6class import compile_model
from keras.preprocessing import image
from cv2 import cv
import cv2
import sys
from shared import *


# print(len(sys.argv))
# print(sys.argv[1])

from keras.backend.common import set_image_data_format
set_image_data_format('channels_first')


if len(sys.argv) != 3:
    print('Usage: python videoEmpathy.py <checkpoint> <model>')
    exit(0)

# # -------------------------------------------------
# Background config:
weights_path = sys.argv[1]
model_path = sys.argv[2]
#
cascade_classifier = cv2.CascadeClassifier(CASC_PATH)
#



def brighten(data, b):
    datab = data * b
    return datab

iter = 0
def format_image(myimage):
    if len(myimage.shape) > 2 and myimage.shape[2] == 3:
        myimage = cv2.cvtColor(myimage, cv2.COLOR_BGR2GRAY)
    else:
        myimage = cv2.imdecode(myimage, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    faces = cascade_classifier.detectMultiScale(
        myimage,
        scaleFactor=1.3,
        minNeighbors=5
    )
    # None is we don't found an image
    if not len(faces) > 0:
        return None
    max_area_face = faces[0]
    for face in faces:
        if face[2] * face[3] > max_area_face[2] * max_area_face[3]:
            max_area_face = face
    # Chop image to face
    face = max_area_face
    myimage = myimage[face[1]:(face[1] + face[2]), face[0]:(face[0] + face[3])]
    # Resize image to network size
    try:
        myimage = cv2.resize(myimage, (48, 48), interpolation=cv2.INTER_CUBIC)
    except Exception:
        print("[+] Problem during resize")
        return None

    # print(myimage)
    # cv2.imshow("Lol", myimage)
    # # if iter<10:
    # cv2.imwrite(str(iter) + '.png', myimage.astype('uint8'))
    #
    # cv2.waitKey(1)

    print(myimage.shape)
    # myimage.reshape(-1,1,image.shape[0], image.shape[1])
    # myimage = myimage-
    img_mean = myimage.mean()
    img_std = np.std(myimage)
    myimage = np.divide(np.subtract(myimage, img_mean), img_std)
    # myimage = myimage / 255.0
    myimage = np.expand_dims(myimage, axis=0)
    myimage = np.expand_dims(myimage, axis=0)
    print(myimage.shape)
    myimage = myimage.astype('float32')

    print('face:', face)

    return myimage, face


# Load Model
network = load_model(model_path, weights_path)

video_capture = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_SIMPLEX

feelings_faces = []
for index, emotion in enumerate(EMOTIONS):
    feelings_faces.append(cv2.imread('../emojis2/' + emotion + '.png', -1))

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Predict result with network
    # cv2.imshow(frame,)
    if frame is not None:
        tmp = format_image(frame)
        if tmp == None:
            continue
        iter += 1
        tmp , face = tmp
        # cv2.imwrite(str(time.clock()) + '.jpg', face.astype('uint8'))
        result = network.predict(tmp, batch_size=1)


        # Write results in frame
        h = frame.shape[0] - 180
        if result is not None:
            print(EMOTIONS[np.argmax(result)])
            # Draw face in frame

            # for (x,y,w,h) in faces:
            (x, y, w, h) = face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
            cv2.rectangle(frame, (x, y - 15), (x + w, y), (255, 0, 0), -1)
            cv2.putText(frame, EMOTIONS[np.argmax(result)], (x, y - 5), cv2.FONT_HERSHEY_PLAIN, 0.8, (255, 255, 255), 1)

            print(result)
            # cv2.rectangle(frame,(0,h -200), (200, h), (255, 255, 255), -1)


            face_image = feelings_faces[np.argmax(result)]



            # for i in face_:
            #     face_image[i] = cv2.resize(face_image[i],(20,20), interpolation=cv2.INTER_CUBIC)

            for index, emotion in enumerate(EMOTIONS):
                # index+=5
                cv2.putText(frame, emotion, (10, index * 20 + 20+h), cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 255, 0), 1)



                cv2.rectangle(frame, (80, index * 20 + 10+h), (80 + int(result[0][index] * 100), (index + 1) * 20 + 4+h),
                              (255, 0, 0), -1)


            # frame[200:320, 10:130]=face_image[:,:,:3]

            # Ugly transparent fix
            # for c in range(0, 3):
            #     frame[200:264, 10:74, c] = face_image[:, :, c] * (face_image[:, :, 3] / 255.0) + frame[200:264, 10:74,
            #                                                                                       c] * (
            #                                                                                       1.0 - face_image[:, :,
            #                                                                                             3] / 255.0)

        # Display the resulting frame
        cv2.imshow('Video', frame)

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #   break
    if cv2.waitKey(1) == 27:
        break  # esc to quit
# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
