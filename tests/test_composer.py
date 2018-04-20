#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `landsat_processor` package."""
import os
import shutil

from homura import download
from landsat_processor.composer import Composer


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


def test_download_images_exists():
    # Composer params:
    # filename, ordered_filelist, out_path, bands, quiet=True
    download = download_images(bands=[6,5,4])
    assert(len(download) == 5)

    composition = Composer.create_composition(
        filename=SCENE,
        ordered_filelist=download[:3],
        out_path=check_create_folder(PATH),
        bands=[6,5,4],
        quiet=False
    )

    assert(composition["type"] == 'r6g5b4')
    assert(composition["name"] == "{}_r6g5b4.TIF".format(SCENE))

    # remove_path()
