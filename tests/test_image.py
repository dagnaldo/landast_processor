#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `landsat_processor` package."""

import os
import pytest
import subprocess

from landsat_processor.image_info import Image

LOCAL_PATH = os.path.join(os.path.abspath(os.path.dirname('.')), 'test_media')
SCENE_NAME = "LC08_L1TP_221071_20170521_20170526_01_T1"


@pytest.fixture
def create_image():
    path_1 = os.path.join(LOCAL_PATH, SCENE_NAME + "_r6g5b4.TIF")
    path_2 = os.path.join(LOCAL_PATH, SCENE_NAME + "_r6g5b4")

    image_1 = Image(path_1)
    image_2 = Image(path_2)

    create_files(image_1.image_dir, SCENE_NAME + "_r6g5b4.TIF")
    create_files(image_2.image_dir, SCENE_NAME + "_r6g5b4")

    return image_1, image_2, path_1, path_2

def create_files(dir, file):
    subprocess.call('mkdir {} -p '.format(dir), shell=True)
    subprocess.call('touch {} '.format(os.path.join(dir, file)), shell=True)

def test_image_info(create_image):
    data = create_image

    assert(data[0].image_path == data[2])
    assert(data[1].image_path == data[3])
    assert(data[0].image_dir == LOCAL_PATH)
    assert(data[1].image_dir == LOCAL_PATH)
    assert(data[0].image_name == SCENE_NAME + "_r6g5b4")
    assert(data[1].image_name == SCENE_NAME + "_r6g5b4")

def test_image_rename(create_image):
    data = create_image
    image = data[0]
    image.rename_file("my_image")

    assert(image.image_path == os.path.join(LOCAL_PATH, 'my_image'))
    assert(image.image_name == 'my_image')
    assert(image.image_dir == LOCAL_PATH)
    assert(os.path.exists(image.image_path))
    image.remove_file()
    assert(not os.path.exists(image.image_path))

    

def test_remove_file(create_image):
    data = create_image

    assert(os.path.exists(data[0].image_path))
    assert(os.path.exists(data[1].image_path))
    
    data[0].remove_file()
    data[1].remove_file()

    assert(not os.path.exists(data[0].image_path))
    assert(not os.path.exists(data[1].image_path))
    