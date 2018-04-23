=================
landsat_processor
=================


.. image:: https://img.shields.io/pypi/v/landsat_processor.svg
        :target: https://pypi.python.org/pypi/landsat_processor

.. image:: https://img.shields.io/travis/dagnaldo/landsat_processor.svg
        :target: https://travis-ci.org/dagnaldo/landsat_processor

.. image:: https://readthedocs.org/projects/landsat-processor/badge/?version=latest
        :target: https://landsat-processor.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


A landsat collection of processes


* Free software: MIT license
* Documentation: https://landsat-processor.readthedocs.io.


Features
--------

* Composition:

Creates a composition using gdal_merge.py

.. code-block:: python
    
    from landsat_process.composer import Composer

    composition = Composer.create_composition(
        filename=<output-filename>,
        ordered_filelist=<ordered-images-list>,
        out_path=<outputh=path>,
        bands=<Bands: [6,5,4]>,
        quiet=<True or False>
    )


* Tilers

.. code-block:: python
    
    from landsat_process.composer import Tiler

    tms_path, xml_path = Tiler.make_tiles(
        image_path=<path-to-image>,
        link_base=<link-base-used-on-xml>,
        output_folder=<output-folder>,
        zoom=<zoom-levels-list: [2,15]>,
        quiet=<True or False,
        nodata=<Nodata-value>, # Must be same as datasource bands count
        convert=<True or False>, # Convert to byte scale?
    )

* TODO:

    * NDVI;
    * NDWI;
    * Change Detection;


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

