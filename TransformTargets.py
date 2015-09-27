import os
import os.path
import unittest
import random
import math
import tempfile
import time
import numpy
import csv
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

path = '/Users/junichi/Dropbox/Experiments/BRP/BRPRobotCases/Scene'
dataFile = 'RobotCase-Log.csv'


# NOTE: The script assumes that there is a -1 offset between the image and transform indices,
# because transforms are calculated from the previous images. (We used TSE for registration,
# and VIBE for transform).

def main():

    caseIndex = -1
    targetIndex = -1
    imageIndex = -1
    caseData = []
    
    with open(path+'/'+dataFile, 'rU') as f:
        reader = csv.reader(f)

        for row in reader:
            if caseIndex < 0: # First row
                caseIndex = row.index('Case')
                targetIndex = row.index('Tgt')
                imageIndex = row.index('MRI')
            else:
                case = int(row[caseIndex])
                target = int(row[targetIndex])
                image = int(row[imageIndex])
                caseData.append((case, target, image))

    for (case, target, image) in caseData:

        print 'Processing for case=%d, image=%d...' % (case, image)
        
        # Load targets
        targetsFilePath = '%s/Case%03d/Targets.fcsv' % (path, case)
        targetsNode = None
        if os.path.isfile(targetsFilePath):
            (r, targetsNode) = slicer.util.loadMarkupsFiducialList(targetsFilePath, True)

        if not targetsNode:
            print 'Could not find target file.'
            continue

        # Load transform
        transformFilePath = '%s/Case%03d/T-%02d.h5' % (path, case, image)
        transformNode = None
        if os.path.isfile(transformFilePath):
            (r, transformNode) = slicer.util.loadTransform(transformFilePath, True)
        else:
            # Offset for image index. See the comment above.
            transformFilePath = '%s/Case%03d/T-%02d.h5' % (path, case, image-1)
            (r, transformNode) = slicer.util.loadTransform(transformFilePath, True)
            
        if not transformNode:
            print 'Could not find transform file.'
            slicer.mrmlScene.RemoveNode(targetsNode)
            continue

        # Transform targets
        matrix = vtk.vtkMatrix4x4()
        transformNode.GetMatrixTransformToParent(matrix)
        targetsNode.ApplyTransformMatrix(matrix)

        transformedTargetFilePath = '%s/Case%03d/Targets-transformed-%02d.fcsv' % (path, case, image)
        slicer.util.saveNode(targetsNode, transformedTargetFilePath)
        
        slicer.mrmlScene.RemoveNode(transformNode)
        slicer.mrmlScene.RemoveNode(targetsNode)


if __name__ ==  "__main__":
    main();


