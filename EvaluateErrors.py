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

# This script requires CurveMaker module to measure the minimum distance between points and curves.

#path = '/Users/junichi/Dropbox/Experiments/BRP/BRPRobotCases/Scene'
#path = '/home/develop/Projects/Dropbox/Experiments/BRP/BRPRobotCases/Scene'
#dataFile = 'RobotCase-Log.csv'


def main():
    # This script is called from Slicer Python Console.
    pass

# Fit a circle and return the intersection and radius
#   (intersect, radius) = FitCircle(p1, p2, p3)
#
#   p1, p2, p3: 3-element vectors in numpy.array() format
#
def FitCircle(p1, p2, p3):

    posErr = 0.00001;

    # Compute the bisecting points between p1 and p2 (m1), and p2 and p3 (m2)
    m1 = (p1+p2)/2.0
    m2 = (p2+p3)/2.0

    # Compute the normal vectors along the perpendicular bisectors
    v12 = (p2-p1)
    v23 = (p3-p2)

    norm12 = numpy.linalg.norm(v12)
    norm23 = numpy.linalg.norm(v23)

    if norm12 < posErr or norm23 < posErr:
        return 0

    v12 = v12 / norm12
    v23 = v23 / norm23

    # Vector perpendicular to the circle
    n = numpy.cross(v12, v23)
    norm_n = numpy.linalg.norm(n)

    if norm_n < posErr:
        return 0
    n = n / norm_n

    n1 = numpy.cross(v12, n)
    n2 = numpy.cross(v23, n)

    norm_n1 = numpy.linalg.norm(n1)
    norm_n2 = numpy.linalg.norm(n2)
    if norm_n1 < posErr or norm_n2 < posErr:
        return 0

    n1 = n1 / norm_n1
    n2 = n2 / norm_n2

    # Compute the projection of m2 onto the perpendicular bisector of p1p2
    h = m1 + numpy.inner((m2-m1),n1)*n1

    # The intersecting point of the two perpendicular bisectors (= estimated
    # center of fitted circle) is 'c' can be written as:
    #
    #    <c> = <m2> + a * <n2>
    #
    # where 'a' is a scalar value. Projection of 'c' on the m2h is 'h'
    #
    #    a * <n2> * (<h> - <m2>)/(|<h> - <m2>|) = |<h> - <m2>|
    #    a = |<h> - <m2>|^2 / {<n2> * (<h> - <m2>)}
    #

    m2h = h-m2
    nm2h = numpy.linalg.norm(m2h)

    a = nm2h*nm2h / numpy.inner(n2, m2h)


    intersect = m2 + a * n2

    print intersect
    radius = (numpy.linalg.norm(p1-intersect)+numpy.linalg.norm(p2-intersect)+numpy.linalg.norm(p3-intersect)) / 3.0

    #return (intersect, radius)
    return radius

def EvaluateErrors(path, dataFile='RobotCase-Log.csv', calibFile='RobotCalibration.csv'):

    # Open result file
    lt = time.localtime()
    resultFileName = "result-%04d-%02d-%02d-%02d-%02d-%02d.csv" % (lt.tm_year, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec)
    resultFilePath = path + '/' + resultFileName
    resultFile = open(resultFilePath, 'a')
    #resultFile.write("Case, Series, Target, TgtErr, TgtErrR, TgtErrA, TgtErrS, TgtErrAngle, DeltaTgtErrAngle, BxErr, BxErrR, BxErrA, BxErrS, BxErrAngle, DeltaBxErrAngle, BevelAngle, EntryErrR, EntryErrA, EntryErrS, curveRadius, SegmentLR, SegmentZone, SegmentAB, SegmentAP, DepthStart, DepthEnd, Core, TgtDispR, TgtDispA, TgtDispS\n") ## CSV header
    resultFile.write("Case, Series, Target, TgtErr, TgtErrR, TgtErrA, TgtErrS, TgtErrAngle, DeltaTgtErrAngle, BxErr, BxErrR, BxErrA, BxErrS, BxErrAngle, DeltaBxErrAngle, BevelAngle, EntryErrR, EntryErrA, EntryErrS, curveRadius, SegmentLR, SegmentZone, SegmentAB, SegmentAP, Core, TgtDispR, TgtDispA, TgtDispS, Finger, VIBE, InsertionLength\n") ## CSV header

    # Initialize CurveMaker module
    slicer.util.selectModule('CurveMaker')
    cmlogic = slicer.modules.CurveMakerWidget.logic
    cmlogic.setInterpolationMethod(1)
    cmlogic.setRing(0)
    cmlogic.setTubeRadius(1.0)

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
    #depthStartIndex = -1
    #depthEndIndex = -1
    coreIndex = -1

    caseData = []

    with open(path+'/'+dataFile, 'rU') as f:
        reader = csv.reader(f)

        for row in reader:
            if caseIndex < 0: # First row
                caseIndex = row.index('Case')
                targetIndex = row.index('Tgt')
                imageIndex = row.index('MRI')
                tseIndex = row.index('TSE')
                robotTgtRIndex = row.index('TgtR')
                robotTgtAIndex = row.index('TgtA')
                robotTgtSIndex = row.index('TgtS')
                bevelIndex = row.index('Bevel')
                segmentLRIndex = row.index('LR')
                segmentZoneIndex = row.index('Zone')
                segmentABIndex = row.index('AB')
                segmentAPIndex = row.index('AP')
                #depthStartIndex = row.index('DepthStart')
                #depthEndIndex = row.index('DepthEnd')
                coreIndex = row.index('Core')
                fingerIndex = row.index('Finger')

            else:
                case = int(row[caseIndex])
                target = int(row[targetIndex])
                image = int(row[imageIndex])
                imageTSE = int(row[tseIndex])
                robotTgtR = float(row[robotTgtRIndex])
                robotTgtA = float(row[robotTgtAIndex])
                robotTgtS = float(row[robotTgtSIndex])
                bevel = int(row[bevelIndex])
                segmentLR = row[segmentLRIndex]
                segmentZone = row[segmentZoneIndex]
                segmentAB = row[segmentABIndex]
                segmentAP = row[segmentAPIndex]
                #depthStart = float(row[depthStartIndex])
                #depthEnd = float(row[depthEndIndex])
                core = row[coreIndex]
                finger = row[fingerIndex]

                #caseData.append((case, target, image, [robotTgtR, robotTgtA, robotTgtS], bevel, [segmentLR, segmentZone, segmentAB, segmentAP], [depthStart, depthEnd], core))
                caseData.append((case, target, image, imageTSE, [robotTgtR, robotTgtA, robotTgtS], bevel, [segmentLR, segmentZone, segmentAB, segmentAP], core, finger))

    # Read robot calibration
    zframeCenter = {}
    
    with open(path+'/'+calibFile, 'rU') as f:
        reader = csv.reader(f)
        caseIndex = -1
        
        for row in reader:
            print 'caseIndex = %d' % caseIndex
            if caseIndex < 0: # First row
                caseIndex = row.index('Case')
                calibR11Index = row.index('R11')
                calibR12Index = row.index('R12')
                calibR13Index = row.index('R13')
                calibXIndex = row.index('X')
                calibR21Index = row.index('R21')
                calibR22Index = row.index('R22')
                calibR23Index = row.index('R23')
                calibYIndex = row.index('Y')
                calibR31Index = row.index('R31')
                calibR32Index = row.index('R32')
                calibR33Index = row.index('R33')
                calibZIndex = row.index('Z')
                caseIndex = 0
            else:
                case = int(row[caseIndex])
                zframeCenter[case] = [float(row[calibXIndex]), float(row[calibYIndex]), float(row[calibZIndex])]
                
    prevCase = -1
    prevTarget = -1
    prevRobotTgtOffset = numpy.array([0.0, 0.0, 0.0])
    prevBiopsyTgtOffset = numpy.array([0.0, 0.0, 0.0])
    prevTransformIndex = None

    #for (case, target, image, robotTgt, bevel, segment, depth, core) in caseData:
    for (case, target, image, imageTSE, robotTgt, bevel, segment, core, finger) in caseData:

        newTarget = False
        if (case != prevCase) or (target != prevTarget):
            newTarget = True

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
        transformIndexUsed = image
        isVIBE = (image != imageTSE)  ## VIBE image is used, when image != imageTSE

        if os.path.isfile(transformFilePath):
            (r, transformNode) = slicer.util.loadTransform(transformFilePath, True)
        else:
            if imageTSE > 0:
                transformFilePath = '%s/Case%03d/T-%02d.h5' % (path, case, imageTSE)
                (r, transformNode) = slicer.util.loadTransform(transformFilePath, True)
                transformIndexUsed = imageTSE

        if not transformNode:
            print 'Could not find transform file -- Previous one is used.'
            slicer.mrmlScene.RemoveNode(targetsNode)
            if prevTransformIndex:
                transformFilePath = '%s/Case%03d/T-%02d.h5' % (path, case, prevTransformIndex)
                (r, transformNode) = slicer.util.loadTransform(transformFilePath, True)
                transformIndexUsed = prevTransformIndex
            else:
                continue

        prevTransformIndex = transformIndexUsed

        # Validate the target index
        nTargets = targetsNode.GetNumberOfFiducials()
        if target > nTargets:
            print 'The target index exceeds the largest index (%d / %d).' % (target, nTargets)
            slicer.mrmlScene.RemoveNode(transformNode)
            slicer.mrmlScene.RemoveNode(targetsNode)
            continue

        # Get original target location
        origTgt = [0.0, 0.0, 0.0]
        targetsNode.GetNthFiducialPosition(target-1, origTgt)

        # Transform targets
        matrix = vtk.vtkMatrix4x4()
        transformNode.GetMatrixTransformToParent(matrix)
        targetsNode.ApplyTransformMatrix(matrix)

        transformedTargetFilePath = '%s/Case%03d/Targets-transformed-%02d.fcsv' % (path, case, image)
        slicer.util.saveNode(targetsNode, transformedTargetFilePath)

        # Get actual biopsy target
        biopsyTgt = [0.0, 0.0, 0.0]
        targetsNode.GetNthFiducialPosition(target-1, biopsyTgt)

        # Calculate the displacement of the target
        tgtDisplacement = numpy.array(biopsyTgt)-numpy.array(origTgt)

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
        ## Note that the returned offest is a vector from the line to the target. Error vector is the inverse.
        robotTgtOffset = -robotTgtOffset
        print 'TARGETING ERROR: %.3f, (%.3f, %.3f, %.3f)' % (robotTgtDist, robotTgtOffset[0], robotTgtOffset[1], -robotTgtOffset[2])

        # Calculate biopsy error
        (biopsyTgtDist, biopsyTgtOffset) = cmlogic.distanceToPoint(biopsyTgt, True)
        ## Note that the returned offest is a vector from the line to the target. Error vector is the inverse.
        biopsyTgtOffset = -biopsyTgtOffset
        print 'BIOPSY ERROR: %.3f, (%.3f, %.3f, %.3f)' % (biopsyTgtDist, biopsyTgtOffset[0], biopsyTgtOffset[1], biopsyTgtOffset[2])

        # Insertion length
        insertionLength = cmlogic.CurveLength
        print 'Insertion Length: %.3f' % (insertionLength)

        entryPointOffset = numpy.array([0.0, 0.0, 0.0])
        nFid = trajectoryNode.GetNumberOfFiducials()
        if  nFid > 0:
            posStart = [0.0, 0.0, 0.0]
            posMid   = [0.0, 0.0, 0.0]
            posEnd   = [0.0, 0.0, 0.0]
            trajectoryNode.GetNthFiducialPosition(nFid-1,posStart)
            trajectoryNode.GetNthFiducialPosition(nFid/2,posMid)
            trajectoryNode.GetNthFiducialPosition(0,posEnd)

            # Error at the skin entry point, assuming the robot adjusts the trajectory to the main field. (If not, needle orientation
            # has to be obtained from the RobotCase-Log.csv)
            # Offest in z-direction is calculated based on the robot calibration data. The offset between the center of the z-frame and
            # the needle guide is assumed to be 27 mm.
            entryPointOffset = numpy.array([posStart[0], posStart[1], posStart[2]]) - numpy.array([robotTgt[0], robotTgt[1], zframeCenter[case][2]])
            entryPointOffset[2] = entryPointOffset[2] - 27.0
                                
            #trajectoryNode.GetNthFiducialPosition(nOfControlPoints-1,posEnd)
            #posEnd = [0.0, 0.0, 0.0]

        
            # Compute curveture
            radius = FitCircle(numpy.array(posStart), numpy.array(posMid), numpy.array(posEnd))

        # Convert bevel direction to angle
        bevelAngle = bevel*30.0

        # Error angle -- 12 O'clock is zero
        robotErrorAngle = 90.0-(numpy.arctan2(robotTgtOffset[1], -robotTgtOffset[0]) *  180.0 / numpy.pi)
        biopsyErrorAngle = 90.0-(numpy.arctan2(biopsyTgtOffset[1], -biopsyTgtOffset[0]) *  180.0 / numpy.pi)
        if robotErrorAngle < 0.0:
            robotErrorAngle = robotErrorAngle + 360.0
        if biopsyErrorAngle < 0.0:
            biopsyErrorAngle = biopsyErrorAngle + 360.0

        # Delta error angle -- 12 O'clock is zero
        ## Delta error angle is an angle of the offest from the first attempt
        deltaRobotErrorAngle = 0.0
        deltaBiopsyErrorAngle = 0.0
        if newTarget:
            prevRobotTgtOffset = robotTgtOffset
            prevBiopsyTgtOffset = biopsyTgtOffset
        else:
            deltaRobotTgtOffset = robotTgtOffset - prevRobotTgtOffset
            deltaBiopsyTgtOffset = biopsyTgtOffset - prevBiopsyTgtOffset
            deltaRobotErrorAngle = 90.0-(numpy.arctan2(deltaRobotTgtOffset[1], -deltaRobotTgtOffset[0]) *  180.0 / numpy.pi)
            deltaBiopsyErrorAngle = 90.0-(numpy.arctan2(deltaBiopsyTgtOffset[1], -deltaBiopsyTgtOffset[0]) *  180.0 / numpy.pi)
            if deltaRobotErrorAngle < 0.0:
                deltaRobotErrorAngle = deltaRobotErrorAngle + 360.0
            if deltaBiopsyErrorAngle < 0.0:
                deltaBiopsyErrorAngle = deltaBiopsyErrorAngle + 360.0

            prevRobotTgtOffset = robotTgtOffset
            prevBiopsyTgtOffset = biopsyTgtOffset


        # Output results
        resultFile.write("%d,%d,%d," % (case, image, target))
        resultFile.write("%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (robotTgtDist, robotTgtOffset[0], robotTgtOffset[1], robotTgtOffset[2], robotErrorAngle, deltaRobotErrorAngle))
        resultFile.write("%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," % (biopsyTgtDist, biopsyTgtOffset[0], biopsyTgtOffset[1], biopsyTgtOffset[2], biopsyErrorAngle, deltaBiopsyErrorAngle))
        resultFile.write("%.3f," % bevelAngle)
        resultFile.write("%.3f,%.3f,%.3f," % (entryPointOffset[0], entryPointOffset[1], entryPointOffset[2]))
        resultFile.write("%.3f," % radius)
        resultFile.write("%s,%s,%s,%s," % (segment[0], segment[1], segment[2], segment[3]))
        #resultFile.write("%.3f,%.3f," % (depth[0], depth[1]))
        resultFile.write("%s," % core)
        resultFile.write("%.3f,%.3f,%.3f," % (tgtDisplacement[0], tgtDisplacement[1], tgtDisplacement[2]))
        resultFile.write("%s," % finger)
        resultFile.write("%d," % isVIBE)
        resultFile.write("%.3f\n" % insertionLength)

        
        cmlogic.SourceNode = None
        cmlogic.DestinationNode = None
        slicer.mrmlScene.RemoveNode(transformNode)
        slicer.mrmlScene.RemoveNode(targetsNode)
        slicer.mrmlScene.RemoveNode(destNode)
        slicer.mrmlScene.RemoveNode(trajectoryNode)

        prevCase = case
        prevTarget = target


    if resultFile:
        resultFile.close()


if __name__ ==  "__main__":
    main();
