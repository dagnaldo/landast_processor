#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

os.environ["PATH"] += ":{}".format(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tilers-tools')
)


class Tiler:
    """ 
    Class for tiler data using tiler-tools 
    from https://github.com/vss-devel/tilers-tools

    method make_tiles creates a pyramid for image
    """

    def __get_image_info(self):
        pass

    def __convert_to_byte_scale(input_image, output_folder = ""):
        image_path = os.path.join(output_folder, "{}.TIF".format(input_image.image_name))
        output_image = Image(image_path)
        command = 'gdal_translate -ot Byte -scale {0} {1}'.format(
            input_image.image_path, output_image.image_path)

        call_gdal_transform(command, input_image, output_image)
        return output_image

    def _generate_tms(input_image, naming_image, output_folder="", nodata=[0,0,0], zoom=[2,15]):
        nodata = ",".join(map(str, nodata))
        command = "gdal_tiler.py -q -p tms --src-nodata {nodata} --zoom={min_z}:{max_z} -t {path} {image}".format(
            nodata=nodata,
            min_z=zoom[0],
            max_z=zoom[1],
            path=output_folder,
            image=input_image
        )

        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError as exc:
            print(exc)
            return False
        except OSError as exc:
            print(exc)
            return False

        return output_folder

    def _generate_xml(input_image, naming_image, link_base, output_folder=""):

        image_info = get_image_info(Image(input_image))

        try:
            upper_left = image_info['cornerCoordinates']['upperLeft']
            lower_right = image_info['cornerCoordinates']['lowerRight']
        except Exception as exc:
            print(exc)
            return False

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
        out_xml = os.path.join(output_folder, xml_name)

        with open(out_xml, 'w') as f:
            f.write(tms_xml)

        return xml_name


    def make_tiles(image_path, link_base, output_folder="", zoom=[2, 15], nodata=[0,0,0]):

        original_image = Image(image_path)
        converted_image = convert_to_8b(
            original_image, output_folder=output_folder)

        tms = generate_tms(
            converted_image.image_path,
            original_image,
            output_folder=output_folder,
            nodata=nodata,
            zoom=zoom)

        if not tms:
            return False

        link_base = os.path.join(link_base, "")
        xml = generate_xml(
            converted_image.image_path,
            original_image,
            link_base=link_base,
            output_folder=output_folder)

        if not xml:
            return False

        converted_image.remove_file()
        return (tms, xml)
