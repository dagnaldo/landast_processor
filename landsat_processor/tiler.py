#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import subprocess

from osgeo import gdal

from .exceptions import TMSError, XMLError
from .image_info import Image

os.environ["PATH"] += ":{}".format(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tilers-tools')
)


class Tiler:
    """
    Class for tiler data using tiler-tools
    from https://github.com/vss-devel/tilers-tools

    method make_tiles creates a pyramid for image
    """

    @classmethod
    def __validate_image_bands(self, image, data):
        """
        Internal method to check if image exists and is a valid datasource
        """

        if not os.path.isfile(image):
            return False

        try:
            ds = gdal.Open(image)
        except Exception as exc:
            print(exc)
            return False

        return ds.RasterCount == len(data)

    @classmethod
    def __subprocess(self, command):
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

    @classmethod
    def __get_image_info(self, image_path):
        """
        Get info from raster using gdal
        requires gdal >= 2.1.3
        params:
            image_path: absolute path for image

        returns:
            json data from gdalinfo command
        """
        command = 'gdalinfo -json {0}'.format(image_path)

        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

        return json.loads(proc.communicate()[0].decode())

    @classmethod
    def __convert_to_byte_scale(self, input_image, output_folder="~/tms/"):
        """
        Translates raster using gdal
        requires gdal >= 2.1.3
        params:
            input_image: Image instance
            output_folder: output folder for image
        returns:
            Image instance of output_image
        """
        command = 'gdal_translate -ot Byte -scale {0} {1}'

        image_name = "{}.TIF".format(input_image.image_name)
        output_image_path = os.path.join(output_folder, image_name)
        output_image = Image(output_image_path)
        command = command.format(
            input_image.image_path, output_image.image_path
        )

        if not Tiler.__subprocess(command):
            return False

        return output_image

    @classmethod
    def _generate_tms(
        self, image_path, output_folder="~/tms/",
        nodata=[0, 0, 0], zoom=[2, 15]
    ):
        """
        Generate TMS Pyramid for input Image instance
        params:
            input_image: Image object
            naming_image: name of output path
            output_folder: folder for output pyramid
            nodata: nodata info, must be same number as source bands
            zoom: list of zoom levels ([start, end])
        """
        command = "gdal_tiler.py -q -p tms --src-nodata {nodata} \
            --zoom={min_z}:{max_z} -t {path} {image}"
        str_nodata = ",".join(map(str, nodata))

        if not Tiler.__validate_image_bands(image_path, nodata):
            raise TMSError('Input image is not a valid data, check if \
                            length must be same as datasource bands')

        command = command.format(
            nodata=str_nodata, path=output_folder, image=image_path,
            min_z=zoom[0], max_z=zoom[1],
        )

        if not Tiler.__subprocess(command):
            return False

        return True

    @classmethod
    def _generate_xml(
        self, image_path, naming_image,
        link_base, output_folder="~/tms/"
    ):
        """
        Generates XML for image on same path of image
        """

        try:
            image_info = Tiler.__get_image_info(image_path=image_path)
            upper_left = image_info['cornerCoordinates']['upperLeft']
            lower_right = image_info['cornerCoordinates']['lowerRight']
        except Exception as exc:
            raise ValueError(exc)

        target_window = "<TargetWindow>\n\
            <UpperLeftX>{0}</UpperLeftX>\n\
            <UpperLeftY>{1}</UpperLeftY>\n\
            <LowerRightX>{2}</LowerRightX>\n\
            <LowerRightY>{3}</LowerRightY>\n\
        </TargetWindow>".format(
            upper_left[0], upper_left[1], lower_right[0], lower_right[1])

        tms_xml = "<GDAL_WMS>\n\
            <Service name=\"TMS\">\n\
                <ServerUrl>{0}/{1}.tms/${{z}}/${{x}}/${{y}}.png</ServerUrl>\n\
                <SRS>EPSG:3857</SRS>\n\
                <ImageFormat>image/png</ImageFormat>\n\
            </Service>\n\
            <DataWindow>\n\
                <UpperLeftX>-20037508.34</UpperLeftX>\n\
                <UpperLeftY>20037508.34</UpperLeftY>\n\
                <LowerRightX>20037508.34</LowerRightX>\n\
                <LowerRightY>-20037508.34</LowerRightY>\n\
                <TileLevel>{2}</TileLevel>\n\
                <TileCountX>1</TileCountX>\n\
                <TileCountY>1</TileCountY>\n\
                <YOrigin>bottom</YOrigin>\n\
            </DataWindow>\n\
            {3}\n\
            <Projection>EPSG:3857</Projection>\n\
            <BlockSizeX>256</BlockSizeX>\n\
            <BlockSizeY>256</BlockSizeY>\n\
            <BandsCount>4</BandsCount>\n\
            <ZeroBlockHttpCodes>204,303,400,404,500,501</ZeroBlockHttpCodes>\n\
            <ZeroBlockOnServerException>true</ZeroBlockOnServerException>\n\
            <Cache>\n\
                <Path>/tmp/cache_{4}.tms</Path>\n\
            </Cache>\n\
        </GDAL_WMS>".format(
            link_base, naming_image.image_name,
            15, target_window, naming_image.image_name
        )

        xml_name = naming_image.image_name + ".xml"
        xml = os.path.join(output_folder, xml_name)

        with open(xml, 'w') as f:
            f.write(tms_xml)

        return xml_name

    @staticmethod
    def make_tiles(
        image_path, link_base, output_folder="~/tms/",
        zoom=[2, 15], nodata=[0, 0, 0]
    ):
        """
        Creates tiles for image using tilers-tools
        params:
            image_path: path for image
            link_base: http url for xml file. E.g.: http://localhost
            output_folder: folder for image and pyramid files
                default is '~/tms/'
            zoom: list of zoom levels ([start, end])
            nodata: nodata info, must be same number as source bands
        returns:
            pyramid data and xml data on output folder for zoom levels
        """

        input_image = Image(image_path)

        converted_image = Tiler.__convert_to_byte_scale(
            input_image=input_image,
            output_folder=output_folder
        )

        try:
            tms = Tiler._generate_tms(
                image_path=converted_image.image_path,
                output_folder=output_folder,
                nodata=nodata,
                zoom=zoom
            )
        except Exception as exc:
            raise TMSError(exc)

        try:
            xml = Tiler._generate_xml(
                image_path=converted_image.image_path,
                naming_image=input_image,
                link_base=os.path.join(link_base, ""),
                output_folder=output_folder
            )
        except Exception as exc:
            raise XMLError(exc)

        # Removing converted image file on output path
        converted_image.remove_file()

        return (tms, xml)
