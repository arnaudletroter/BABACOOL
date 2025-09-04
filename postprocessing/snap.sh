#!/bin/bash

image=$1
index=$2
output=$3

STEP=1
NUMSTEPS=10
mkdir snap
 
#for T1w T2w
param="--cmap greyscale --negativeCmap greyscale --displayRange 10.0 110.0 --clippingRange 0.0 150 --modulateRange -20 110"

#for TPM
#param="--cmap brain_colours_x_rain_iso --displayRange 0.2 1.0 --clippingRange 0.2 1.1 --modulateRange 0.0 1.0"

for (( n = 0; n <= NUMSTEPS; n += STEP )); do
    n_int=$(printf "%04d" "$n")
    x=$((n + index))
    echo "$x"
    n_int_name=$(printf "%04d" "$x")
    n_int_1=$(printf "%d" "$n") 

    fsleyes render --outfile snap/${output}_${n_int_name}.png --worldLoc 6.1172777520673876 -15.288620620450743 0.48002745507764644 --displaySpace world --size 640 244  --displaySpace ${image} --xcentre -0.00832  0.04014 --ycentre  0.01091  0.01787 --zcentre  0.01607 -0.03058 --xzoom 1162.157455031331 --yzoom 1162.157455031331 --zzoom 1162.157455031331  --showLocation no --layout horizontal --cursorWidth 1.0 --hideLabels --showLocation no --hideCursor --bgColour 0.0 0.0 0.0 --fgColour 1.0 1.0 1.0 --cursorColour 0.0 1.0 0.0 $image  --interpolation linear  --gamma 0.0 --cmapResolution 256 ${param} --volume $n_int_1
echo $n_int

done