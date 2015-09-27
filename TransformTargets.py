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

# NOTE: The script assumes that there is a -1 offset between the image and transform indices,
# because transforms are calculated from the previous images. (We used TSE for registration,
# and VIBE for transform).

# This script requires CurveMaker module to measure the minimum distance between points and curves.

path = '/Users/junichi/Dropbox/Experiments/BRP/BRPRobotCases/Scene'
dataFile = 'RobotCase-Log.csv'

def main():

    # Initialize CurveMaker module
    slicer.util.selectModule('CurveMaker')
    cmlogic = slicer.modules.CurveMakerWidget.logic
    cmlogic.setInterpolationMethod(1)
    cmlogic.setRing(0)
    cmlogic.setTubeRadius(1.0)

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
                robotTgtRIndex = row.index('TgtR')
                robotTgtAIndex = row.index('TgtA')
                robotTgtSIndex = row.index('TgtS')

            else:
                case = int(row[caseIndex])
                target = int(row[targetIndex])
                image = int(row[imageIndex])
                robotTgtR = float(row[robotTgtRIndex])
                robotTgtA = float(row[robotTgtAIndex])
                robotTgtS = float(row[robotTgtSIndex])
                caseData.append((case, target, image, [robotTgtR, robotTgtA, robotTgtS]))

    for (case, target, image, robotTgt) in caseData:

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

        # Get actual biopsy target
        nTargets = targetsNode.GetNumberOfFiducials()
        if target > nTargets:
            print 'The target index exceeds the largest index (%d / %d).' % (target, nTargets)
            slicer.mrmlScene.RemoveNode(transformNode)
            slicer.mrmlScene.RemoveNode(targetsNode)
            continue

        biopsyTgt = [0.0, 0.0, 0.0]
        targetsNode.GetNthFiducialPosition(target-1, biopsyTgt)
        
        # Load trajectory
        trajectoryFilePath = '%s/Case%03d/Traj-%d.fcsv' % (path, case, image)
        trajectoryNode = None
        if os.path.isfile(trajectoryFilePath):
            (r, trajectoryNode) = slicer.util.loadMarkupsFiducialList(trajectoryFilePath, True)
        if not trajectoryNode:
            print 'Could not find trajectory file.'
            slicer.mrmlScene.RemoveNode(transformNode)
            slicer.mrmlScene.RemoveNode(targetsNode)
            continue

        # Set data to Curve Maker module
        destNode = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelNode')
        slicer.mrmlScene.AddNode(destNode)
        cmlogic.SourceNode = trajectoryNode
        cmlogic.DestinationNode = destNode
        cmlogic.enableAutomaticUpdate(True)
        cmlogic.updateCurve()

        # Calculate targeting error
        (robotTgtDist, robotTgtOffset) = cmlogic.distanceToPoint(robotTgt, True)
        print 'TARGETING ERROR: %.3f, (%.3f, %.3f, %.3f)' % (robotTgtDist, robotTgtOffset[0], robotTgtOffset[1], robotTgtOffset[2])

        # Calculate biopsy error
        (biopsyTgtDist, biopsyTgtOffset) = cmlogic.distanceToPoint(biopsyTgt, True)
        print 'BIOPSY ERROR: %.3f, (%.3f, %.3f, %.3f)' % (biopsyTgtDist, biopsyTgtOffset[0], biopsyTgtOffset[1], biopsyTgtOffset[2])

        cmlogic.SourceNode = None
        cmlogic.DestinationNode = None
        slicer.mrmlScene.RemoveNode(transformNode)
        slicer.mrmlScene.RemoveNode(targetsNode)
        slicer.mrmlScene.RemoveNode(destNode)
        slicer.mrmlScene.RemoveNode(trajectoryNode)


if __name__ ==  "__main__":
    main();


