# Tiler Tools

A few scripts for creating and handling a tile sets from digital raster maps. The scripts are based on GDAL tools.

## Installation

You need to clone and add the path to the tilers-tools on PATH:

```bash
git clone //git/tilers-tools.git
export PATH=$PATH: /path/to/tilers/tools
```

Then, test if lib is available:
```bash
gdal_tiler.py --version
$ gdal_tiler.py version 3.1.0

```

## Tools available:
 * `gdal_tiler.py` -- creates a tile set tree directory from a GDAL dataset (including BSB/KAP, GEO/NOS, OZI map, KML image overlays);
 > `gdal_tiler.py -q -p tms --src-nodata 0,0,0 -t <dst_path> <input_file.TIF>`

 * `tiles_merge.py` -- sequentially merges a few tile sets in a single one to cover the area required;
 * `tiles_convert.py` -- converts tile sets between a different tile structures: TMS, Google map-compatible (maemo mappero), SASPlanet cache, maemo-mapper sqlite3 and gmdb databases;

 * `ozf_decoder.py` -- converts .ozf2 or .ozfx3 file into .tiff (tiled format)
 * `hdr_pcx_merge.py` -- converts hdr-pcx chart image into .png

 * `tiles-opt.py` -- optimizes png tiles into a palleted form using pngnq tool;
 * `tiles-scale.py`

 * `bsb2gdal.py` -- creates geo-referenced GDAL .vrt file from BSB chart;
 * `ozi2gdal.py` -- creates geo-referenced GDAL .vrt file from Ozi map;

 * gdal2kmz.py
 * kml2gdal.py
 * kml2gpx.sh
 * mk-merge-order.sh
 * vrt-bsb-cut.sh


## Compatible with:
- Python 2.x (only)
- Gdal >= 1.7 (tested with 2.2.1)


## TODO:
- Python 3.x compatility;

