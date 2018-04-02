#!/bin/sh
# shell script to prep fetchsdss distribution, by copying and renaming
# relevant files to /Beleriand/dev/dist_fetchsdss/
# 
# We assume the following:
#    1. /Beleriand/dev/dist_fetchsdss/ exists
#    2. it has within it a symbolic link to telarchive_py3

cp fetchsdss_setup.py /Beleriand/dev/dist_fetchsdss/setup.py
cp fetchsdss_MANIFEST.in /Beleriand/dev/dist_fetchsdss/MANIFEST.in
cp README_fetchsdss.txt /Beleriand/dev/dist_fetchsdss/README_fetchsdss.txt
cp COPYING.txt /Beleriand/dev/dist_fetchsdss/COPYING.txt
cp INSTALLATION_fetchsdss.txt /Beleriand/dev/dist_fetchsdss/INSTALLATION_fetchsdss.txt
cp do_fetchsdss.py /Beleriand/dev/dist_fetchsdss/do_fetchsdss.py
cp do_fetchsdss_spectra.py /Beleriand/dev/dist_fetchsdss/do_fetchsdss_spectra.py
