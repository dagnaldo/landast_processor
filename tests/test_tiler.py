#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `landsat_processor` package."""
import os
import shutil
import subprocess

from homura import download

from landsat_processor.tiler import Tiler

BANDS = []
SCENE = "LC08_L1TP_221071_20170521_20170526_01_T1"
URL = "https://landsat-pds.s3.amazonaws.com/c1/L8/221/071"
PATH = "test_media/"


def check_create_folder(folder_path):
    """
    Check whether a folder exists, if not the folder is created.
    Always return folder_path.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path


def remove_path(path=PATH):
    """
    Check if path exists, then remove tree of test_downloader path
    """
    if os.path.exists(path):
        shutil.rmtree(path)


def download_images(scene=SCENE, bands=BANDS, url=URL, path=PATH):
    """
    Download bands on defined PATH for test_process
    """

    downloaded_images = []

    _bands = ["_B{}.TIF".format(i) for i in bands]
    _bands.extend(["_BQA.TIF", "_MTL.txt"])

    scene_bands = [
        {
            "url": "{url}/{scene}/{scene}{band}".format(
                url=url, scene=scene, band=band),
            "band": band.split(".")[0]
        }
        for band in _bands]

    assert(len(scene_bands) == len(bands)+2)

    path = check_create_folder(path)

    for band in scene_bands:
        f = os.path.join(path, band["url"].split("/")[-1])
        d = download(url=band["url"], path=path)
        downloaded_images.append(f)

    return downloaded_images


def test_os_environ_gdal_tiler():
    assert('tilers-tools' in os.environ["PATH"])


def test_call_gdal_tiler():
    zoom = 7
    download_images(bands=[4])
    tiffile = os.path.join(PATH, SCENE + "_B4.TIF")
    out_path = os.path.join(PATH, 'tms')
    out_path_check = os.path.join(out_path, SCENE + "_B4.tms")

    subprocess.call('gdal_tiler.py -p tms --src-nodata 0 --zoom={} '
                    '-t {} {}'.format(zoom, out_path, tiffile), shell=True)

    assert(os.path.exists(out_path))
    assert(os.path.exists(out_path_check))
    assert(os.path.exists(os.path.join(out_path_check, '7')))
    assert(not os.path.exists(os.path.join(out_path_check, '8')))

    zoom = '7:8'
    subprocess.call('gdal_tiler.py -p tms --src-nodata 0 --zoom={} '
                    '-t {} {}'.format(zoom, out_path, tiffile), shell=True)

    assert(os.path.exists(os.path.join(out_path_check, '8')))

    shutil.rmtree(out_path_check)


def test_tiler_tools():
    pass
