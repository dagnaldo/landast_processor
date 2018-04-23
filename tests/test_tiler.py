#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `landsat_processor` package."""
import os
import pytest
import shutil
import subprocess

from homura import download

from landsat_processor.tiler import Tiler
from landsat_processor.exceptions import TMSError, XMLError

BANDS = []
SCENE = "LC08_L1TP_221071_20170521_20170526_01_T1"
URL = "https://landsat-pds.s3.amazonaws.com/c1/L8/221/071"
PATH = "test_media/"


@pytest.fixture
def create_data():
    """ Fixture data (SetUp) """
    download_images(bands=[4])
    tiffile = os.path.join(PATH, SCENE + "_B4.TIF")
    out_path = os.path.join(PATH, 'tms')
    out_path_check = os.path.join(out_path, SCENE + "_B4.tms")

    return {
        "zoom": 7,
        "tiffile": tiffile,
        "out_path": out_path,
        "out_path_check": out_path_check
    }


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


def test_call_gdal_tiler(create_data):
    """ Tests if gdal_tiler.py is valid and test data creation using it"""

    zoom = 7
    subprocess.call('gdal_tiler.py -p tms --src-nodata 0 --zoom={} '
                    '-t {} {}'.format(zoom,
                                      create_data['out_path'],
                                      create_data['tiffile']),
                    shell=True)

    assert(os.path.exists(create_data['out_path']))
    assert(os.path.exists(create_data['out_path_check']))
    assert(os.path.exists(os.path.join(create_data['out_path_check'], '7')))
    assert(not os.path.exists(os.path.join(
        create_data['out_path_check'], '8')))

    zoom = '7:8'
    subprocess.call('gdal_tiler.py -p tms --src-nodata 0 --zoom={} '
                    '-t {} {}'.format(zoom,
                                      create_data['out_path'],
                                      create_data['tiffile']),
                    shell=True)

    assert(os.path.exists(os.path.join(create_data['out_path_check'], '8')))

    shutil.rmtree(create_data['out_path_check'])


def test_tiler_make_tiles(create_data):
    """ Tests if Tiler.make_tiles creates a pyramid data """

    data = Tiler.make_tiles(
        image_path=create_data['tiffile'],
        link_base=create_data['out_path'],
        output_folder=create_data['out_path'],
        zoom=[7, 8],
        quiet=False,
        nodata=[0],
        # convert=True
    )

    assert(os.path.isfile(create_data['tiffile']))
    assert(len(data) == 2)
    assert(data[0] == create_data['out_path_check'])
    assert(os.path.exists(data[0]))
    assert(os.path.isfile(data[1]))

    zoom_7 = os.path.join(data[0], '7')
    zoom_8 = os.path.join(data[0], '8')
    zoom_9 = os.path.join(data[0], '9')

    assert(os.path.exists(zoom_7))
    assert(os.path.exists(zoom_8))
    assert(not os.path.exists(zoom_9))


def test_tiler_make_tiles_exception(create_data):

    """ When nodata is different of datasource bands count"""
    with pytest.raises(TMSError):
        Tiler.make_tiles(
            image_path=create_data['tiffile'],
            link_base=create_data['out_path'],
            output_folder=create_data['out_path'],
            zoom=[7, 8],
            quiet=False,
            nodata=[0,0],
        )

        """ When image path is a invalid datasource"""
    with pytest.raises(Exception):
        Tiler.make_tiles(
            image_path=None,
            link_base=create_data['out_path'],
            output_folder=create_data['out_path'],
            zoom=[7, 8],
            quiet=False,
            nodata=[0,0],
        )


    """ When Linkbase is None"""
    with pytest.raises(Exception):
        Tiler.make_tiles(
            image_path=create_data['tiffile'],
            link_base=None,
            output_folder=create_data['out_path'],
            zoom=[7, 8],
            quiet=False,
            nodata=[0],
        )

    """ When exists only image_path """
    with pytest.raises(Exception):
        Tiler.make_tiles(
            image_path=create_data['tiffile'],
        )

def test_tiler_tools():
    pass
