# -*- coding: utf-8 -*-

import os


class Image:
    """ Class for image """

    def __init__(self, image_path):
        self.set_attributes(image_path)

    def remove_file(self):
        os.remove(self.image_path)

    def rename_file(self, new_filename):
        new_path = os.path.join(self.image_dir, new_filename)
        os.rename(self.image_path, new_path)
        self.set_attributes(os.path.join(self.image_dir, new_filename))

    def set_attributes(self, image_path):
        self.image_path = os.path.abspath(image_path)
        self.image_dir = os.path.dirname(self.image_path)
        self.image_name = os.path.basename(self.image_path).split(".")[0]
