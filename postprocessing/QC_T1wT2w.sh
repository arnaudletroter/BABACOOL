#!/bin/bash

sub=(sub-Noe sub-Olivier sub-Ota1 sub-Palme sub-Pesto sub-Prune sub-Oasis sub-Omelette sub-Oz sub-Papou sub-Phyllis sub-Puma sub-Odin sub-Omer sub-Pau sub-Picsou sub-Odor sub-Omerta sub-Ozy sub-Pepita sub-Prouesse)

ses=(ses-0 ses-1 ses-2 ses-3)

mkdir snap snap/ses-0 snap/ses-1 snap/ses-2 snap/ses-3 

#21 subjects

for i in {0..20}
do
  echo ${sub[i]}
  for j in {0..3}
    do

    #location=`fslstats $1/$2/segmentation/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_space-orig_label-GM_mask.nii.gz -c`
    location=`fslstats $1/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_T2w.nii.gz -c`

    p95_T2w=`fslstats $1/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_T2w.nii.gz -p 95`
    p95_T1w=`fslstats $1/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_T1w.nii.gz -p 95`

    fsleyes render --outfile snap/${ses[j]}/${sub[i]}_${ses[j]}_T1w_T2w.png --size 640 240  --scene ortho --worldLoc $location --displaySpace $1/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_T2w.nii.gz  --xcentre 0 0 --ycentre 0 0 --zcentre 0 0 --xzoom 100 --yzoom 100 --zzoom 100  --showLocation no --layout horizontal --cursorWidth 1.0 --hideLabels --showLocation no --hideCursor --bgColour 0.0 0.0 0.0 --fgColour 1.0 1.0 1.0 --cursorColour 0.0 1.0 0.0 $1/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_T1w.nii.gz --overlayType volume --alpha 100.0 --name "${sub[i]}_${ses[j]}_T1w.nii.gz "  --displayRange 0.0 $p95_T1w --interpolation linear --brightness 60.00 --contrast 60.00 --cmap greyscale --displayRange 50.0 $p95_T1w --clippingRange 50.0 2000 --modulateRange 0.0 $p95_T1w --gamma 0.0 --cmapResolution 256 --interpolation none --numSteps 150 --blendFactor 0.1 --smoothing 0 --resolution 100 --numInnerSteps 10 --clipMode intersection --volume 0 $1/${sub[i]}/${ses[j]}/anat/${sub[i]}_${ses[j]}_T2w.nii.gz  --name "${sub[i]}_${ses[j]}_T2w.nii.gz " --overlayType volume --alpha 30.0 --displayRange 0.0 $p95_T2w --interpolation linear --brightness 60.00 --contrast 60.00  --cmap brain_colours_x_rain_iso  --displayRange 10.0 $p95_T2w --clippingRange 10.0 2000 --modulateRange 0.0 $p95_T2w --gamma 0.0 --cmapResolution 256 --interpolation none --numSteps 150 --blendFactor 0.1 --smoothing 0 --resolution 100 --numInnerSteps 10 --clipMode intersection --volume 0 

    done

done

