import sys
import os
import os.path
import unittest
import random
import math
import tempfile
import time
import numpy
import shutil
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import PathCollisionAnalysis

def main():
    path = '/Users/junichi/Dropbox/Experiments/BRP/BRPRobotCases/Scene/Case448'
    #ProcessCase(path):

# Create surface models from a label map and return the node ID of model hierarhcy
def CreateModels(labelMapNode, modelHierarchyNode):

    modelMakerCLI = slicer.modules.modelmaker
    # tf = tempfile.NamedTemporaryFile(prefix='Slicer/Models-', suffix='.mrml')

    modelMakerParameters = {}
    #modelMakerParameters['ColorTable'] = 'vtkMRMLColorTableNodeFileGenericAnatomyColors.txt'
    modelMakerParameters['ModelSceneFile'] = modelHierarchyNode.GetID()
    modelMakerParameters['Name'] = 'Model'
    modelMakerParameters['GenerateAll'] = True
    modelMakerParameters['StartLabel'] = -1
    modelMakerParameters['EndLabel'] = -1
    modelMakerParameters['KkipUnNamed'] = True
    modelMakerParameters['JointSmooth'] = True
    modelMakerParameters['Smooth'] = 15
    modelMakerParameters['FilterType'] = 'Sinc'
    modelMakerParameters['Decimate'] = 0.25
    modelMakerParameters['SplitNormals'] = True
    modelMakerParameters['PointNormals'] = True
    modelMakerParameters['InputVolume'] = labelMapNode.GetID()

    slicer.cli.run(modelMakerCLI, None, modelMakerParameters, True)


def TransformModelHierarchy(modelHierarchyNode, transformNode):
    if not transformNode:
        return False

    # modelLabelNode.SetAndObserveTransformNodeID(transformNode.GetID())
    # slicer.vtkSlicerTransformLogic.hardenTransform(modelLabelNode)
    collection = vtk.vtkCollection()
    modelHierarchyNode.GetAssociatedChildrenNodes(collection)
    if collection:
        nModels = collection.GetNumberOfItems()
        for i in range(nModels):
            model = collection.GetItemAsObject(i)
            model.SetAndObserveTransformNodeID(transformNode.GetID())
            slicer.vtkSlicerTransformLogic.hardenTransform(model)
    return True

def RemoveModels(modelHierarchyNode):
    collection = vtk.vtkCollection()
    modelHierarchyNode.GetAssociatedChildrenNodes(collection)
    if collection:
        nModels = collection.GetNumberOfItems()
        for i in range(nModels):
            model = collection.GetItemAsObject(i)
            slicer.mrmlScene.RemoveNode(model)
    return True

def RigidRegistration(fromImageNode, toImageNode, transformNode):
    registrationParameters = {}
    registrationParameters['samplingPercentage'] = 0.002
    registrationParameters['splineGridSize'] = [14,10,12]
    registrationParameters['initializeTransformMode'] = 'Off'
    registrationParameters['useRigid'] = True
    registrationParameters['maskProcessingMode'] = 'NOMASK'
    registrationParameters['medianFilterSize'] = [0,0,0]
    registrationParameters['removeIntensityOutliers'] = 0
    registrationParameters['outputVolumePixelType'] = 'float'
    registrationParameters['backgroundFillValue'] = 0
    registrationParameters['interpolationMode'] = 'Linear'
    registrationParameters['numberOfIterations'] = 1500
    registrationParameters['maximumStepLength'] = 0.05
    registrationParameters['minimumStepLength'] = 0.001
    registrationParameters['relaxationFactor'] = 0.5
    registrationParameters['translationScale'] = 1000
    registrationParameters['reproportionScale'] = 1
    registrationParameters['skewScale'] = 1
    registrationParameters['maxBSplineDisplacement'] = 0
    registrationParameters['fixedVolumeTimeIndex'] = 0
    registrationParameters['movingVolumeTimeIndex'] = 0
    registrationParameters['numberOfHistogramBins'] = 50
    registrationParameters['numberOfMatchPoints'] = 10
    registrationParameters['costMetric'] = 'MMI'
    registrationParameters['maskInferiorCutOffFromCenter'] = 1000
    registrationParameters['ROIAutoDilateSize'] = 0
    registrationParameters['ROIAutoClosingSize'] = 9
    registrationParameters['numberOfSamples'] = 0
    registrationParameters['failureExitCode'] = -1
    registrationParameters['numberOfThreads'] = -1
    registrationParameters['debugLevel'] = 0
    registrationParameters['costFunctionConvergenceFactor'] = 2e+13
    registrationParameters['projectedGradientTolerance'] = 1e-05
    registrationParameters['maximumNumberOfEvaluations'] = 900
    registrationParameters['maximumNumberOfCorrections'] = 25
    registrationParameters['metricSamplingStrategy'] = 'Random'

    resampleParameters = {}
    resampleParameters['pixelType'] = 'uchar'
    resampleParameters['interpolationMode'] = 'NearestNeighbor'
    resampleParameters['defaultValue'] = 0
    resampleParameters['numberOfThreads'] = -1

    registrationCLI = slicer.modules.brainsfit

    # Register first needle image to the current needle image
    registrationParameters['fixedVolume'] = toImageNode.GetID()
    registrationParameters['movingVolume'] = fromImageNode.GetID()
    registrationParameters['linearTransform'] = transformNode.GetID()
    registrationParameters['initialTransform'] = ''
    registrationParameters['initializeTransformMode'] = 'Off'
    registrationParameters['maskProcessingMode'] = 'NOMASK'
    registrationParameters['fixedBinaryVolume'] = ''
    registrationParameters['movingBinaryVolume'] = ''

    slicer.cli.run(registrationCLI, None, registrationParameters, True)

    # # Resample mask
    # needleLabelName = 'needle-t-%0d-label' % index
    # needleLabelNode.SetName("needleLabelNode")
    # resampleCLI = slicer.modules.brainsresample
    # resampleParameters['inputVolume'] = modelLabelNode.GetID()
    # resampleParameters['referenceVolume'] = needleImageNode.GetID()
    # resampleParameters['outputVolume'] = needleLabelNode.GetID()
    # resampleParameters['warpTransform'] = transform.GetID()
    # slicer.cli.run(resampleCLI, None, resampleParameters, True)
    # #slicer.util.saveNode(needleLabelNode, path+'/'+needleLabelName+'.nrrd')

def GenerateFileName(prefix, postfix):

    lt = time.localtime()
    fileName = "%s-%04d-%02d-%02d-%02d-%02d-%02d%s" % (prefix, lt.tm_year, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec, postfix)
    return fileName

def FindNextIndex(startIndex, endIndex, path, prefix, postfix):

    for index in range(startIndex, endIndex+1):
        modelImageFileName ='%s/%s%02d%s' % (path, prefix, index, postfix)
        if os.path.isfile(modelImageFileName):
            return index

    # Could not find the file in the index range
    return -1


def ProcessSeries(path, caseIndex, modelImageNode, modelHierarchyNode, baseSeriesIndex, seriesIndex, reRegistration=False):

    # Object name dictionary:
    objectNameDict = {
    'Model_x_x'  : 0, # Not defined -- Reserved
    'Model_2_2'  : 1,  # Prostate, 2
    'Model_3_3'  : 2, # Pelvic Diaphragm, 3
    'Model_4_4'  : 3, # Blubospongiosus m., 4
    'Model_16_16': 4, # Bulb of the Penus / Corpus Spongiosum, 16
    'Model_5_5'  : 5, # Ischiocavernosus m., 5
    'Model_6_6'  : 6, # Crus of the Penis / Corpus Cavernosum, 6
    'Model_13_13': 7, # Transverse Perineal m., 13
    'Model_10_10': 8, # Obturator internus m., 10
    'Model_8_8'  : 9, # Rectum, 8
    'Model_11_11': 10, # Pubic Arc
    }

    print 'Processing series %d' % seriesIndex

    # File name for needle confirmation image
    needleImageFileName = '%s/needle-v-%02d.nrrd' % (path, seriesIndex)
    needleImageNode = None

    # File names for transforms
    transformNode = None
    transformName = 'T-%02d-to-%02d' % (baseSeriesIndex, seriesIndex)
    transformFileName = '%s/%s.h5' % (path, transformName)
    manualTransformFileName = '%s/%s-manual.h5' % (path, transformName)

    # File name for trajectory
    trajectoryFilePath = '%s/Traj-%d.fcsv' % (path, seriesIndex)
    trajectoryNode = None

    # Any manual transform?
    print "Checking manual transform %s" % manualTransformFileName
    if os.path.isfile(manualTransformFileName):
        print 'Series %02d: Manual transform has been found.' % seriesIndex
        (r, transformNode) = slicer.util.loadTransform(manualTransformFileName, True)

    if not transformNode:
        # Load current needle image
        (r, needleImageNode) = slicer.util.loadVolume(needleImageFileName, {}, True)
        if not needleImageNode:
            print 'Could not load needle confirmation image: %s' % needleImageFileName
            return None

        # If 're-registration' option is ON, any existing transform?
        if (not reRegistration) and os.path.isfile(transformFileName):
            print 'Series %02d: Existing transform has been found.' % seriesIndex
            (r, transformNode) = slicer.util.loadTransform(transformFileName, True)

        # No manual / existing transform -- run registration
        if not transformNode:
            print 'Series %02d: Finding initial transform.' % seriesIndex
            transformNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLLinearTransformNode")
            slicer.mrmlScene.AddNode(transformNode)
            transformNode.SetName(transformName)

            RigidRegistration(modelImageNode, needleImageNode, transformNode)

            # Create initialization transform
            #transform.ApplyTransformMatrix(firstTransformMatrix)
            slicer.util.saveNode(transformNode, path+'/'+transformName+'.h5')

    if not transformNode:
        print 'Unable to generate transform.'
        return None

    # Load the corresponding trajectory data
    if os.path.isfile(trajectoryFilePath):
        (r, trajectoryNode) = slicer.util.loadMarkupsFiducialList(trajectoryFilePath, True)

    if not trajectoryNode:
        print 'Could not find trajectory file: %s' % trajectoryFilePath
        slicer.mrmlScene.RemoveNode(transformNode)
        slicer.mrmlScene.RemoveNode(needleImageNode)
        return None

    # Once the transform is obtained, apply it to the models
    TransformModelHierarchy(modelHierarchyNode, transformNode)

    # Path Collision Analysis module
    pcaLogic = PathCollisionAnalysis.PathCollisionAnalysisLogic()
    [objectIDs, objectNames, normalVectors, entryAngles, totalLengthInObject, curvatures, radiusNormals] = pcaLogic.CheckIntersections(modelHierarchyNode, trajectoryNode)

    # Asume that the trajectory data traces the path from the tip to the base.
    # The last entry point in the output represents the needle's entry point into the object.
    nObjects = len(objectIDs)
    resultString = ""

    nObjectsInDic = len(objectNameDict)
    lenTable = [0.0] * nObjectsInDic
    entAngTable = [0.0] * nObjectsInDic
    entDirTable = [0.0] * nObjectsInDic
    curvatureTable = [0.0] * nObjectsInDic
    centerDirTable = [0.0] * nObjectsInDic

    for k in range(nObjects):
        i = len(entryAngles[k]) - 1
        angle = entryAngles[k][i]
        normal = normalVectors[k][i]
        length = totalLengthInObject[k]
        curvature = curvatures[k][i]
        centerDir = radiusNormals[k][i]

        # Look up table index
        l = objectNameDict[objectNames[k]]
        lenTable[l] = length
        entAngTable[l] = angle
        # NOTE: It's not atan(y, x) because the angle is 0 when (x, y) = (0, 1).
        # Also note that the sign for x is negative, because it goes negative, when rotated clockwise from 0 degree.
        entDirTable[l] = math.atan2(-normal[0], normal[1]) * 180.0 / math.pi
        if entDirTable[l] < 0.0:
            entDirTable[l] = entDirTable[l] + 360.0
        curvatureTable[l] = curvature
        centerDirTable[l] = math.atan2(-centerDir[0], centerDir[1]) * 180.0 / math.pi
        if centerDirTable[l] < 0.0:
            centerDirTable[l] = centerDirTable[l] + 360.0

    # Transform the models back to the original location
    transformNode.Inverse()
    TransformModelHierarchy(modelHierarchyNode, transformNode)

    #### Load fiducial
    # pcaLogic = PathCollisionAnalysis.PathCollisionAnalysisLogic()
    # [objectIDs, objectNames, normalVectors, entryAngles, totalLengthInObject] = pcaLogic.CheckIntersections(modelHierarchyNode, FiducialSelector.currentNode())

    slicer.mrmlScene.RemoveNode(trajectoryNode)
    slicer.mrmlScene.RemoveNode(needleImageNode)
    slicer.mrmlScene.RemoveNode(transformNode)

    resultString = "%d, %d" % (caseIndex, seriesIndex)
    for i in range(0, nObjectsInDic):
        # Len,  EntAng,  EntDir,  Curv,  CentDir
        resultString = resultString + ", %f, %f, %f, %f, %f" % (lenTable[i], entAngTable[i], entDirTable[i], curvatureTable[i], centerDirTable[i])

    resultString = resultString + "\n"

    return resultString


def ProcessCase(path, caseIndex, reRegistration=False, outFileName=None):
    # This function will check the intersections between the given needle trajectory and anatomical structures.
    # The needle trajectory is given as a fiducial markers, whereas the antomical structures are given as a label map.
    # The fuction finds intersecting objects, and compute
    #   - Trajectory length within the objects
    #   - Entry angle defined by the angle between the normal of the object's surface at the entry point
    #   - Entry direction defined as the angle from the 12 o'clock direction and the projectino of normal vector on the axial plane.
    # The entry direction represents

    # Find base image (for anatomy segmentation)
    index = 0
    modelImageNode = None
    modelLabelNode = None

    path = "%s/Case%03d" % (path, caseIndex)
    resultFile = None

    # Generate output file name, if not specified.
    if not outFileName:
        # Open result file
        # lt = time.localtime()
        # resultFileName = "TrajAnalysis-%04d-%02d-%02d-%02d-%02d-%02d.csv" % (lt.tm_year, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec)
        resultFileName = GenerateFileName('TrajAnalysis', '.csv')
        resultFilePath = path + '/' + resultFileName

    resultFile = open(resultFilePath, 'a')

    # Print header
    # resultFile.write("Case, Series, Target, TgtErr, TgtErrR, TgtErrA, TgtErrS, TgtErrAngle, DeltaTgtErrAngle, BxErr, BxErrR, BxErrA, BxErrS, BxErrAngle, DeltaBxErrAngle, BevelAngle, EntryErrR, EntryErrA, EntryErrS, curveRadius, SegmentLR, SegmentZone, SegmentAB, SegmentAP, DepthStart, DepthEnd, Core, TgtDispR, TgtDispA, TgtDispS\n") ## CSV header
    resultFile.write("Case, Traj, ")
    resultFile.write("Len_0,  EntAng_0,  EntDir_0,  Curv_0,  CentDir_0, ")
    resultFile.write("Len_1,  EntAng_1,  EntDir_1,  Curv_1,  CentDir_1, ")
    resultFile.write("Len_2,  EntAng_2,  EntDir_2,  Curv_2,  CentDir_2, ")
    resultFile.write("Len_3,  EntAng_3,  EntDir_3,  Curv_3,  CentDir_3, ")
    resultFile.write("Len_4,  EntAng_4,  EntDir_4,  Curv_4,  CentDir_4, ")
    resultFile.write("Len_5,  EntAng_5,  EntDir_5,  Curv_5,  CentDir_5, ")
    resultFile.write("Len_6,  EntAng_6,  EntDir_6,  Curv_6,  CentDir_6, ")
    resultFile.write("Len_7,  EntAng_7,  EntDir_7,  Curv_7,  CentDir_7, ")
    resultFile.write("Len_8,  EntAng_8,  EntDir_8,  Curv_8,  CentDir_8, ")
    resultFile.write("Len_9,  EntAng_9,  EntDir_9,  Curv_9,  CentDir_9, ")
    resultFile.write("Len_10, EntAng_10, EntDir_10, Curv_10, CentDir_10\n")

    MAX_INDEX = 100

    # Load model image
    # for index in range(1, MAX_INDEX+1):
    #     modelImageFileName ='%s/needle-v-%02d.nrrd' % (path, index)
    #     modelLabelFileName ='%s/needle-v-%02d-anatomy-label.nrrd' % (path, index)
    #     if os.path.isfile(modelImageFileName) and os.path.isfile(modelLabelFileName):
    #         (r, modelImageNode) = slicer.util.loadVolume(modelImageFileName, {}, True)
    #         (r, modelLabelNode) = slicer.util.loadLabelVolume(modelLabelFileName, {}, True)
    #         break

    index = FindNextIndex(1, MAX_INDEX, path, 'needle-v-', '-anatomy-label.nrrd')

    if index < 0:
        print "Could not find baseline image in the index range."
        return

    modelImageFileName ='%s/needle-v-%02d.nrrd' % (path, index)
    modelLabelFileName ='%s/needle-v-%02d-anatomy-label.nrrd' % (path, index)
    (r, modelImageNode) = slicer.util.loadVolume(modelImageFileName, {}, True)
    (r, modelLabelNode) = slicer.util.loadLabelVolume(modelLabelFileName, {}, True)

    if not modelImageNode:
        print "Could not load baseline image: %s." % modelImageFileName
        return

    if not modelLabelNode:
        print "Could not load baseline label: %s." % modelLabelFileName
        slicer.mrmlScene.RemoveNode(modelImageNode)
        return

    # Create 3D models
    print "Creating 3D surface models for %s " % modelLabelFileName
    modelHierarchyNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelHierarchyNode")

    #modelHierarchyNode.SetName("ModelHierarchy")
    slicer.mrmlScene.AddNode(modelHierarchyNode)
    CreateModels(modelLabelNode, modelHierarchyNode)

    slicer.mrmlScene.RemoveNode(modelLabelNode)

    baseIndex = index

    #for index in range(sindex, 100):
    while index <= MAX_INDEX:

        indexImage = FindNextIndex(index, MAX_INDEX, path, 'needle-v-', '.nrrd')

        if indexImage < 0:
            indexManualTrans = FindNextIndex(index, MAX_INDEX, path, 'T-%02d-to-' % baseIndex, '-manual.h5')
            if indexManualTrans < 0:
                print "Could not find needle confirmation image in the range anymore."
                break
            index = indexManualTrans
        else:
            index = indexImage

        resultString = ProcessSeries(path, caseIndex, modelImageNode, modelHierarchyNode, baseIndex, index, reRegistration)

        if resultString:
            resultFile.write(resultString)

        index = index + 1

    RemoveModels(modelHierarchyNode)
    slicer.mrmlScene.RemoveNode(modelHierarchyNode)
    slicer.mrmlScene.RemoveNode(modelImageNode)

def ProcessCaseBatch():

    path = '/Users/junichi/Projects/BRP/BRPRobotCases/Scene'
    cases = [246, 248, 249, 250, 251, 256, 257, 260, 263, 264, 266, 267, 375, 397, 401, 403, 405, 411, 416, 418, 423, 426, 433, 436, 442, 445, 448]
    #cases = [246, 248, 249, 250, 251, 256, 257, 260, 263, 264, 266, 267, 375, 397, 401, 403, 405, 411, 416, 418, 423, 426, 433, 436, 442, 445, 448]
    #cases = [405, 411, 442, 445, 448]
    for c in cases:
        ProcessCase(path, c, True)

if __name__ ==  "__main__":
    main()
