python image_mosaic.py
python parse_names.py
copy names.js ..\tiles\names.js

python gentiles.py -t jpg -w 512 output.png 1-5 ../tiles
python gentiles.py -t png -w 512 output.png 6 ../tiles

