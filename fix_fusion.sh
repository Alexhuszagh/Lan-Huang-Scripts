#!/bin/bash

for f in *-3.mgf; do export g=${f//-3.mgf/_ITMSms3cid_c.txt}; python fixFusion.py -m "$f" -p "$g"; done

mkdir Corrected
for f in *_fixed.txt; do export g=${f//_fixed.txt/.txt}; mv "$f" Corrected/"$g"; done
