#!/bin/bash

sub=(sub-Noe sub-Olivier sub-Ota1 sub-Palme sub-Pesto sub-Prune sub-Oasis sub-Omelette sub-Oz sub-Papou sub-Phyllis sub-Puma sub-Odin sub-Omer sub-Pau sub-Picsou sub-Odor sub-Omerta sub-Ozy sub-Pepita sub-Prouesse)

ses=(ses-0)

#ses=(ses-0 ses-1 ses-2 ses-3)

mkdir snap snap/ses-0 snap/ses-1 snap/ses-2 snap/ses-3 

#21 subjects

for i in {0..20}
do
  echo ${sub[i]}
  for j in {0..0}
    do

    location=`fslstats $1/$2/segmentation/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_space-orig_label-GM_mask.nii.gz -c`
    p95=`fslstats $1/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_T2w.nii.gz -p 95`
    
    fsleyes render --outfile snap/${ses[j]}/${sub[i]}_${ses[j]}_T2w_seg_$2.png --size 640 240  --scene ortho --worldLoc $location --displaySpace $1/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_T2w.nii.gz  --xcentre 0 0 --ycentre 0 0 --zcentre 0 0 --xzoom 100 --yzoom 100 --zzoom 100  --showLocation no --layout horizontal --cursorWidth 1.0 --hideLabels --showLocation no --hideCursor --bgColour 0.0 0.0 0.0 --fgColour 1.0 1.0 1.0 --cursorColour 0.0 1.0 0.0 $1/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_T2w.nii.gz  --name "${sub[i]}_${ses[j]}_T2w.nii.gz "  --displayRange 0.0 $p95  --interpolation linear --volume 0 --volume 0 $1/$2/segmentation/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_space-orig_label-CSF_mask.nii.gz --name "CSF" --overlayType volume --alpha 100.0 --brightness 49.75000000000001 --contrast 49.90029860765409 --cmap green --negativeCmap greyscale --displayRange 0.0 33094.67 --clippingRange 0.0 33094.67 --modulateRange 0.0 32767.0 --gamma 0.0 --cmapResolution 256 --interpolation none --numSteps 150 --blendFactor 0.1 --smoothing 0 --resolution 100 --numInnerSteps 10 --clipMode intersection --volume 0 $1/$2/segmentation/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_space-orig_label-GM_mask.nii.gz --name "GM" --overlayType volume --alpha 100.0 --brightness 49.75000000000001 --contrast 49.90029860765409 --cmap red --negativeCmap greyscale --displayRange 0.0 33094.67 --clippingRange 0.0 33094.67 --modulateRange 0.0 32767.0 --gamma 0.0 --cmapResolution 256 --interpolation none --numSteps 150 --blendFactor 0.1 --smoothing 0 --resolution 100 --numInnerSteps 10 --clipMode intersection --volume 0 $1/$2/segmentation/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_space-orig_label-WM_mask.nii.gz --name "WM" --overlayType volume --alpha 100.0 --brightness 49.75000000000001 --contrast 49.90029860765409 --cmap blue --negativeCmap greyscale --displayRange 0.0 33094.67 --clippingRange 0.0 33094.67 --modulateRange 0.0 32767.0 --gamma 0.0 --cmapResolution 256 --interpolation none --numSteps 150 --blendFactor 0.1 --smoothing 0 --resolution 100 --numInnerSteps 10 --clipMode intersection  --volume 0 $1/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_T2w.nii.gz --name "T2w" --disabled --overlayType volume --alpha 100.0 --brightness 49.74999999999999 --contrast 49.90029860765409 --cmap greyscale --negativeCmap greyscale --displayRange 0.0 $p95 --clippingRange 0.0 3000 --modulateRange 0.0 $p95 --gamma 0.0 --cmapResolution 256 --interpolation none --numSteps 150 --blendFactor 0.1 --smoothing 0 --resolution 100 --numInnerSteps 10 --clipMode intersection --volume 0
    done

done
