import os

import cv2
import numpy as np
import face_recognition

class Detector():
    def __init__(self, face_dir='faces'):
        self._update_known(face_dir)

    # return the first authorized face in frame, or none
    def find_any(frame, auth_faces):
        small = self._downsize(frame)
        bbs = face_recognition.api.face_locations(small)
        encodings = face_recognition.api.face_encodings(small, bbs)

        for enc in encodings:
            for person in self.known_faces:
                if person not in auth_faces:
                    continue
                person_enc = self.known_faces[person]
                if face_recognition.api.compare_faces([person_enc], enc)[0]:
                    return person

        return None

    def _update_known(self, face_dir='faces'):
        fnames = os.listdir(face_dir)
        enc_dir = {}
        for fname in fnames:
            path = os.path.join(face_dir, fname)
            name = os.path.splitext(fname)[0]
            im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            encodings = face_recognition.api.face_encodings(im, num_jitters=3)
            if len(encodings) == 1:
                enc_dir[name] = encodings[0]
        self.known_faces = enc_dir

    def _downsize(self, frame, fx=0.5, fy=0.5):
        in_height, in_width = frame.shape[:2]
        out_size = (round(in_width * fx), round(in_height * fy))
        return cv2.resize(frame, out_size, 0, 0, cv2.INTER_AREA)
