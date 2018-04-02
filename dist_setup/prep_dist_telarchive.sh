#!/bin/sh
# shell script to prep fetchsdss distribution, by copying and renaming
# relevant files to /Beleriand/dev/dist_fetchsdss/
# 
# We assume the following:
#    1. /Beleriand/dev/dist_telarchive/ exists
#    2. it has within it a symbolic link to telarchive_py3

cp telarchive_setup.py /Beleriand/dev/dist_telarchive/setup.py
cp telarchive_MANIFEST.in /Beleriand/dev/dist_telarchive/MANIFEST.in
cp README.txt /Beleriand/dev/dist_telarchive/README.txt
cp README_fetchsdss.txt /Beleriand/dev/dist_telarchive/README_fetchsdss.txt
cp COPYING.txt /Beleriand/dev/dist_telarchive/COPYING.txt
cp INSTALLATION.txt /Beleriand/dev/dist_telarchive/INSTALLATION.txt
cp dosearch.py /Beleriand/dev/dist_telarchive/dosearch.py
cp do_fetchsdss.py /Beleriand/dev/dist_telarchive/do_fetchsdss.py
cp do_fetchsdss_spectra.py /Beleriand/dev/dist_telarchive/do_fetchsdss_spectra.py
cp public_changelog.txt /Beleriand/dev/dist_telarchive/changelog.txt
