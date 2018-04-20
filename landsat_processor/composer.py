import os
import subprocess

from osgeo import gdal


class Composer:
    """
    Class with method that process and create
    composition from a Landsat list of files.
    """
    @classmethod
    def __set_full_output_filepath(self, filename, out_path, type_bands_name):
        """
        Returns complete filepath tif for rgb composition
        """
        if (filename.endswith(".TIF") or
            filename.endswith(".tif") or
            filename.endswith(".tiff") or
                filename.endswith(".TIFF")):
            file_path = os.path.join(out_path, filename)
        else:
            file_path = os.path.join(
                out_path,
                "{}_{}.TIF".format(filename, type_bands_name)
            )

        return file_path

    @classmethod
    def __validate_output_image_bands(self, image, ordered_filelist):
        """
        Internal method to check if image exists and is a valid datasource
        """

        if not os.path.isfile(image):
            return False

        try:
            ds = gdal.Open(image)
        except Exception as exc:
            return False

        return ds.RasterCount == len(ordered_filelist)

    @staticmethod
    def create_composition(
        filename, ordered_filelist,
        out_path, bands, quiet=True
    ):
        """
            Creates a composition using gdal_merge.py with ordered filelist

            Args:
                filename: output filename. (my_file, my_file.tif)
                ordered_filelist: list of images used on merge,
                    must be ordered by user for correct output
                out_path: output path for processed image
                bands: list bands number for composition. (6,5,4 -> r6g5b4)

            Returns:
                Merged image with on outpu_path, after bands validation
                raises exception if:
                    - return image dataset is not valid
                    - bands number is different of ordered filelist length
        """
        type_bands_name = "r{0}g{1}b{2}".format(*bands)

        file_path = Composer.__set_full_output_filepath(
            filename=filename,
            out_path=out_path,
            type_bands_name=type_bands_name
        )

        if not quiet:
            print("-- Creating file composition to {}".format(file_path))
            quiet = ""
        else:
            quiet = "-q"

        gdal_mergepy_command = "gdal_merge.py {} -separate \
            -co PHOTOMETRIC=RGB -o {}".format(quiet, file_path)

        for file in ordered_filelist:
            gdal_mergepy_command += " " + file

        subprocess.call(gdal_mergepy_command, shell=True)

        is_valid = Composer.__validate_output_image_bands(
            file_path, ordered_filelist)

        if is_valid:
            return {
                "name": file_path.split("/")[-1],
                "path": file_path,
                "type": type_bands_name
            }
        else:
            return None
