# -*- coding: utf-8 -*-

import subprocess
import json
import os

from django.conf import settings

# os.environ["PATH"] += ":{}".format(settings.TILER_TOOLS_PATH)
# os.environ["PATH"] += ":{}".format(settings.GDAL_BIN_PATH)

class Image:

    def __init__(self, image_path):
        self.set_attributes(image_path)

    def remove_file(self):
        os.remove(self.image_path)

    def rename_file(self, new_filename):
        os.rename(self.image_path, os.path.join(self.image_folder, new_filename))
        self.set_attributes(os.path.join(self.image_folder, new_filename))

    def set_attributes(self, image_path):
        self.image_path = os.path.abspath(image_path)
        self.image_folder = os.path.dirname(self.image_path )
        self.image_name = os.path.basename(self.image_path).split(".")[0]

def convert_to_8b(input_image, output_folder = ""):
    image_path = os.path.join(output_folder, "{}.TIF".format(input_image.image_name))
    output_image = Image(image_path)
    command = 'gdal_translate -ot Byte -scale {0} {1}'.format(
        input_image.image_path, output_image.image_path)

    call_gdal_transform(command, input_image, output_image)
    return output_image

def equalize(input_image, output_folder = ""):
    image_path = os.path.join(output_folder, "{}_equalized.TIF".format(input_image.image_name))
    output_image = Image(image_path)
    command = "gdal_contrast_stretch -ndv '0 0 0' -outndv 0 \
              -percentile-range 0.02 0.98 {0} {1}".format(
        input_image.image_path, output_image.image_path)

    call_gdal_transform(command, input_image, output_image)
    return output_image

def get_image_info(input_image):
    command = 'gdalinfo -json {0}'.format(input_image.image_path)
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return json.loads(proc.communicate()[0].decode())

def convert_4326_to_3857(coordinates):
    command = 'echo {} {} | gdaltransform -output_xy -s_srs EPSG:4326 -t_srs EPSG:{}'.format(
        coordinates[0], coordinates[1], 3857)
    converted_coordinates = subprocess.check_output(command, shell=True)

    return converted_coordinates.decode().rstrip().split(' ')

def call_gdal_transform(command, input_image, output_image):
    #FNULL = open(os.devnull, 'w')
    subprocess.call(command, shell=True)

def generate_tms(input_image, naming_image, output_folder="", no_data=[0,0,0], zoom=[2,15]):
    # output = os.path.join(output_folder, naming_image.image_name + ".tms")
    no_data = ",".join(map(str, no_data))
    command = "gdal_tiler.py -q -p tms --src-nodata {no_data} --zoom={min_z}:{max_z} -t {path} {image}".format(
        no_data=no_data,
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

    return output_folder3

def generate_xml(input_image, naming_image, link_base, output_folder = ""):

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
    </TargetWindow>".format(upper_left[0],upper_left[1],lower_right[0],lower_right[1])

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
        15,target_window, naming_image.image_name
    )
    
    xml_name = naming_image.image_name + ".xml"
    out_xml = os.path.join(output_folder, xml_name)

    with open(out_xml, 'w') as f:
        f.write(tms_xml)

    return xml_name

def make_tiles(image_path, link_base, output_folder="", zoom=[2, 15]):

    original_image = Image(image_path)
    converted_image = convert_to_8b(original_image, output_folder=output_folder)

    tms = generate_tms(
        converted_image.image_path, 
        original_image, 
        output_folder=output_folder, 
        zoom=zoom)
    
    if not tms:
        return False

    link_base = os.path.join(link_base, "")
    xml = generate_xml(
        converted_image.image_path, 
        original_image, 
        link_base=link_base, 
        output_folder = output_folder)

    if not xml:
        return False

    converted_image.remove_file()
    return (tms, xml)