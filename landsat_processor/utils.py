#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utils used on landsat_processor module
"""
import os
import subprocess

try:
    from osgeo import gdal
except ImportError as error:
    import gdal


class Util:

    @staticmethod
    def _print(msg, quiet):
        """
        Used to print if quiet is False
        """
        if not quiet:
            print(msg)

    @staticmethod
    def _check_creation_folder(folder):
        """
        Check whether a folder exists, if not the folder is created.
        Always return folder_path.
        """
        if not os.path.exists(folder):
            os.makedirs(folder)

        return folder

    @staticmethod
    def _validate_image_bands(image, data):
        """
        Function used to check if image exists and
        if is a valid datasource with same bands num of data (nodata)
        """

        if not os.path.isfile(image):
            return False

        try:
            ds = gdal.Open(image)
        except Exception as exc:
            print(exc)
            return False

        return ds.RasterCount == len(data)

    @staticmethod
    def _subprocess(command):
        """
        Function to check_call subprocess
        """
        ok = True

        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError as exc:
            print(exc)
            ok = False
        except OSError as exc:
            print(exc)
            ok = False

        return ok
