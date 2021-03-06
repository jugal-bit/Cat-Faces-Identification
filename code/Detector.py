#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" This module provides functions to detect, crop and align cat faces.

Authors:
    Pg96, dsforza96
"""

from argparse import ArgumentParser
import cv2.cv2 as cv
import utils
import math
import numpy as np
from os import path
from PIL import Image

cascade_models_dir = '../models/detection/'
cat_cascades = ['haarcascade_frontalcatface.xml', 'haarcascade_frontalcatface_extended.xml',
                'lbpcascade_frontalcatface.xml']
eye_cascade_model = path.join(cascade_models_dir, 'haarcascade_eye.xml')


def detect_cat_face(image_file, classifier, show=False, scaleFactor=1.05, minNeighbors=2,
                    eyes_ScaleFactor=1.08, eyes_minNeighbors=3, eyes_minSize=(40, 40)):
    """
    Cat face detection utility.

    :param image_file : str
        The name of the image file to detect the face from.
    :param classifier : int
        Integer used to select the type of detector model to be used:
        0 = haarcascade_frontalcatface.xml
        1 = haarcascade_frontalcatface_extended.xml
        2 = lbpcascade_frontalcatface.xml
    :param show: bool
        set to True to see an output image
    :param scaleFactor: float
        Scale factor value the detector should use
    :param minNeighbors : int
        Min neighbors value the detector should use
    :param eyes_ScaleFactor: float
        scaleFactor value the eyes detector should use
    :param eyes_minNeighbors:
        minNeighbors value the eyes detector should use
    :param eyes_minSize:
        minSize value the eyes detector should use
    :return the cropped face and the location of the eyes, if detected, else None.
    """

    face_detector = cat_cascades[classifier]
    print("Chosen classifier: " + face_detector)
    print("SF={0}, minN={1}".format(scaleFactor, minNeighbors))

    cat_cascade = cv.CascadeClassifier(path.join(cascade_models_dir, face_detector))
    eye_cascade = cv.CascadeClassifier(eye_cascade_model)

    if cat_cascade.empty():
        raise RuntimeError('The face classifier was not loaded correctly!')

    if eye_cascade.empty():
        raise RuntimeError('The eye classifier was not loaded correctly!')

    img = cv.imread(image_file)

    img_orig = cv.imread(image_file)

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    faces = cat_cascade.detectMultiScale(gray, scaleFactor=scaleFactor, minNeighbors=minNeighbors)

    if classifier == 0:
        col = (255, 0, 0)
    elif classifier == 1:
        col = (0, 255, 0)
    else:
        col = (0, 0, 255)

    cropped = None

    for (x, y, w, h) in faces:  # blue
        img = cv.rectangle(img, (x, y), (x + w, y + h), col, 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray,
                                            scaleFactor=eyes_ScaleFactor,
                                            minNeighbors=eyes_minNeighbors,
                                            minSize=eyes_minSize)

        for (ex, ey, ew, eh) in eyes:
            cv.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (255, 255, 0), 2)

        if len(eyes) == 0:
            print("No eyes detected")
        elif len(eyes) == 1:
            print("Only 1 eye (possibly) detected")
            cropped = img_orig[y:y + h, x: x + w]

        elif len(eyes) == 2:
            print("2 eyes detected!")
            cropped = img_orig[y:y + h, x: x + w]

            cropped = [cropped, eyes]
        else:
            print("More than 2 eyes (?) detected")
            cropped = img_orig[y:y + h, x: x + w]

    if show:
        utils.show_image(img)

    return cropped


def ScaleRotateTranslate(img, angle, center=None, new_center=None, scale=None, resample=Image.BICUBIC):
    # Copyright (c) 2012, Philipp Wagner
    # All rights reserved.
    #
    # Redistribution and use in source and binary forms, with or without
    # modification, are permitted provided that the following conditions
    # are met:
    #
    #  * Redistributions of source code must retain the above copyright
    #    notice, this list of conditions and the following disclaimer.
    #  * Redistributions in binary form must reproduce the above
    #    copyright notice, this list of conditions and the following
    #    disclaimer in the documentation and/or other materials provided
    #    with the distribution.
    #  * Neither the name of the author nor the names of its
    #    contributors may be used to endorse or promote products derived
    #    from this software without specific prior written permission.
    #
    # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
    # FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
    # COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
    # INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
    # BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    # LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    # CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
    # LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
    # ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    # POSSIBILITY OF SUCH DAMAGE.

    if (scale is None) and (center is None):
        return img.rotate(angle=angle, resample=resample)
    nx, ny = x, y = center
    sx = sy = 1.0
    if new_center:
        (nx, ny) = new_center
    if scale:
        (sx, sy) = (scale, scale)
    cosine = math.cos(angle)
    sine = math.sin(angle)
    a = cosine / sx
    b = sine / sx
    c = x - nx * a - ny * b
    d = -sine / sy
    e = cosine / sy
    f = y - nx * d - ny * e
    return img.transform(img.size, Image.AFFINE, (a, b, c, d, e, f), resample=resample)


def Distance(p1, p2):
    # Copyright (c) 2012, Philipp Wagner
    # All rights reserved.
    #
    # Redistribution and use in source and binary forms, with or without
    # modification, are permitted provided that the following conditions
    # are met:
    #
    #  * Redistributions of source code must retain the above copyright
    #    notice, this list of conditions and the following disclaimer.
    #  * Redistributions in binary form must reproduce the above
    #    copyright notice, this list of conditions and the following
    #    disclaimer in the documentation and/or other materials provided
    #    with the distribution.
    #  * Neither the name of the author nor the names of its
    #    contributors may be used to endorse or promote products derived
    #    from this software without specific prior written permission.
    #
    # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
    # FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
    # COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
    # INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
    # BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    # LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    # CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
    # LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
    # ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    # POSSIBILITY OF SUCH DAMAGE.

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)


def AlignFace(img, eye_left=(0, 0), eye_right=(0, 0), offset_pct=(0.3, 0.3), dest_sz=(200, 200)):
    # Copyright (c) 2012, Philipp Wagner
    # All rights reserved.
    #
    # Redistribution and use in source and binary forms, with or without
    # modification, are permitted provided that the following conditions
    # are met:
    #
    #  * Redistributions of source code must retain the above copyright
    #    notice, this list of conditions and the following disclaimer.
    #  * Redistributions in binary form must reproduce the above
    #    copyright notice, this list of conditions and the following
    #    disclaimer in the documentation and/or other materials provided
    #    with the distribution.
    #  * Neither the name of the author nor the names of its
    #    contributors may be used to endorse or promote products derived
    #    from this software without specific prior written permission.
    #
    # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
    # FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
    # COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
    # INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
    # BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    # LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    # CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
    # LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
    # ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    # POSSIBILITY OF SUCH DAMAGE.

    # calculate offsets in original image
    offset_h = math.floor(float(offset_pct[0]) * dest_sz[0])
    offset_v = math.floor(float(offset_pct[1]) * dest_sz[1])
    # get the direction
    eye_direction = (eye_right[0] - eye_left[0], eye_right[1] - eye_left[1])
    # calc rotation angle in radians
    rotation = -math.atan2(float(eye_direction[1]), float(eye_direction[0]))
    # distance between them
    dist = Distance(eye_left, eye_right)
    # calculate the reference eye-width
    reference = dest_sz[0] - 2.0 * offset_h
    # scale factor
    scale = float(dist) / float(reference)
    # rotate original around the left eye
    img = ScaleRotateTranslate(img, center=eye_left, angle=rotation)
    # crop the rotated image
    # crop_xy = (eye_left[0] - scale * offset_h, eye_left[1] - scale * offset_v)
    # crop_size = (dest_sz[0] * scale, dest_sz[1] * scale)
    # img = img.crop(
    #     (int(crop_xy[0]), int(crop_xy[1]), int(crop_xy[0] + crop_size[0]), int(crop_xy[1] + crop_size[1])))
    # resize it
    img = img.resize(dest_sz, Image.ANTIALIAS)
    return img


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('input_image', help='The path of the input image')
    parser.add_argument('-o', '--output', help='The path of the output directory', default='../images/dataset/cropped/')
    parser.add_argument('-d', '--detector', default=0, type=int)
    parser.add_argument('-s', '--scalefactor', default=1.05, type=float)
    parser.add_argument('-n', '--minneighbors', default=2, type=int)
    parser.add_argument('-es', '--eyes-scalefactor', default=1.08, type=float)
    parser.add_argument('-en', '--eyes-minneighbors', default=3, type=int)
    parser.add_argument('-em', '--eyes-minsize', default=40, type=int)

    return parser.parse_args()


if __name__ == '__main__':
    """Main for image cropping & testing purposes"""
    args = parse_args()

    out_dir = args.output
    image = args.input_image

    directory, file = path.split(image)
    dir_name = path.basename(directory)
    file_name, file_extension = path.splitext(file)

    save_dir = path.join(out_dir, dir_name)

    detector = args.detector
    sf = args.scalefactor
    n = args.minneighbors
    eyes_sf = args.eyes_scalefactor
    eyes_n = args.eyes_minneighbors
    eyes_ms = (args.eyes_minsize, args.eyes_minsize)

    out = detect_cat_face(image, classifier=detector, show=True, scaleFactor=sf, minNeighbors=n,
                          eyes_ScaleFactor=eyes_sf, eyes_minNeighbors=eyes_n, eyes_minSize=eyes_ms)
    if len(out) == 2:
        face = out[0]
        # show_image(img)

        # transform image into a PIL Image (for face Alignment)
        trans = cv.cvtColor(face, cv.COLOR_BGR2RGB)
        im_pil = Image.fromarray(trans)

        eye1 = out[1][0]
        eye2 = out[1][1]
        # print("eye1 = {0} -- eye2 = {1}".format(eye1, eye2))
        left_eye = np.minimum(eye1, eye2)
        right_eye = eye2 if np.array_equal(left_eye, eye1) else eye1
        # print(left_eye)
        # print(right_eye)

        im = AlignFace(im_pil,
                       eye_left=(int(left_eye[0]), int(left_eye[1])),
                       eye_right=(int(right_eye[0]), int(right_eye[1])))

        # im.show()
        # show_image(face)

        im_np = np.asarray(im_pil)

        cv.imwrite(path.join(save_dir, file_name + "_cropped" + file_extension), face)
        im.save(path.join(save_dir, file_name + "_cropped_aligned" + file_extension))
