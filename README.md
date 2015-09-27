# TargetingEvaluation
Python scripts for targeting accuracy evaluation


## RunRegistration.py

Perform rigid registration between the planning and a series of needle confirmation images. The script performs the following steps:

1. Find the planning and first needle confirmation images with their mask data.
2. Perform rigid registration using mask data. Initialize by aligning the ROI centers.
3. Find the next needle confirmation image.
4. If the needle confirmation image does not have an initialization transform, estimate the initialization transform by registering the first confirmation image.
5. Generate mask data by resampling the mask for planning with the initialization transform.
6. Register the planning image to the needle confirmation image using the mask data using the initialization transform. 


To use the script:

1. The data folder should only contain images from the same clinical case.
2. File names should be 'planning-XX.nrrd' and 'planning-XX-label.nrrd' for the planning image/mask, and 'needle-t-XX.nrrd' and 'needle-t-XX-label.nrrd' for needle confirmation images. XX is a series number.
3. If you want to use a specific initialization transform, place the transform file named 'T-XX-init-adjusted.h5'.
4. Specify the path at line 12
5. Run from the python console in 3D Slicer using execfile() command.




