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

path = '/Users/junichi/Dropbox/Experiments/BRP/BRPRobotCases/Scene'
dataFile = 'RobotCase-Log.csv'
pointInterval = 5.0 # distance between points in mm
prefix = 'Decimated-5-'

def main():

    # Open result file
    lt = time.localtime()
    
    caseIndex = -1
    targetIndex = -1
    imageIndex = -1
    robotTgtRIndex = -1
    robotTgtAIndex = -1
    robotTgtSIndex = -1
    bevelIndex = -1
    segmentLRIndex = -1    # Left - Right
    segmentZoneIndex = -1  # CG, TZ, or PZ
    segmentABIndex = -1    # Apex, Base, or Mid gland
    segmentAPIndex = -1    # Anterior - Posterior
    depthStartIndex = -1
    depthEndIndex = -1
    coreIndex = -1
    
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
                bevelIndex = row.index('Bevel')
                segmentLRIndex = row.index('LR')
                segmentZoneIndex = row.index('Zone')
                segmentABIndex = row.index('AB')
                segmentAPIndex = row.index('AP')
                depthStartIndex = row.index('DepthStart')
                depthEndIndex = row.index('DepthEnd')
                coreIndex = row.index('Core')
                
            else:
                case = int(row[caseIndex])
                target = int(row[targetIndex])
                image = int(row[imageIndex])
                robotTgtR = float(row[robotTgtRIndex])
                robotTgtA = float(row[robotTgtAIndex])
                robotTgtS = float(row[robotTgtSIndex])
                bevel = int(row[bevelIndex])
                segmentLR = row[segmentLRIndex]
                segmentZone = row[segmentZoneIndex]
                segmentAB = row[segmentABIndex]
                segmentAP = row[segmentAPIndex]
                depthStart = float(row[depthStartIndex])
                depthEnd = float(row[depthEndIndex])
                core = row[coreIndex]

                caseData.append((case, target, image, [robotTgtR, robotTgtA, robotTgtS], bevel, [segmentLR, segmentZone, segmentAB, segmentAP], [depthStart, depthEnd], core))

    for (case, target, image, robotTgt, bevel, segment, depth, core) in caseData:

        print 'Processing for case=%d, image=%d...' % (case, image)
        
        # Load trajectory
        trajectoryFilePath = '%s/Case%03d/Traj-%d.fcsv' % (path, case, image)
        trajectoryNode = None
        if os.path.isfile(trajectoryFilePath):
            (r, trajectoryNode) = slicer.util.loadMarkupsFiducialList(trajectoryFilePath, True)
        if not trajectoryNode:
            print 'Could not find trajectory file.'
            continue

        # Create output trajectory
        outputFiducialNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
        slicer.mrmlScene.AddNode(outputFiducialNode)
        outputFiducialNode.SetName('%sTraj-%d' % (prefix, image))

        nFid = trajectoryNode.GetNumberOfFiducials()
        dist = 0.0
        pos = [0.0, 0.0, 0.0]
        trajectoryNode.GetNthFiducialPosition(0,pos)
        prevPosArray = numpy.array(pos)
        outputFiducialNode.AddFiducialFromArray(pos, 'P-0')
        
        for i in range(1,nFid):
            trajectoryNode.GetNthFiducialPosition(i,pos)
            posArray = numpy.array(pos)
            dist = dist + numpy.linalg.norm(posArray-prevPosArray)
            if dist > pointInterval:
                outputFiducialNode.AddFiducialFromArray(pos, 'P-%d' % i)
                dist = 0.0
            prevPosArray = posArray

        # If the last fiducial has not been copied, the last one in the output is replaced with it.
        # (The last segment may be longer than the length defined by 'pointInterval'
        if dist > 0.0:
            trajectoryNode.GetNthFiducialPosition(nFid-1, pos)
            nOutput = outputFiducialNode.GetNumberOfFiducials()
            outputFiducialNode.SetNthFiducialPositionFromArray(nOutput-1, pos)

        slicer.util.saveNode(outputFiducialNode, '%s/Case%03d/%sTraj-%d.fcsv' % (path, case, prefix, image))
        slicer.mrmlScene.RemoveNode(trajectoryNode)
        slicer.mrmlScene.RemoveNode(outputFiducialNode)


if __name__ ==  "__main__":
    main();


