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


def ProcessCase(directory, caseIndex, reRegistration=False, outFileName=None):
    # Find base image (for anatomy segmentation)
    index = 0
    modelImageNode = None
    modelLabelNode = None

    path = "%s/Case%03d" % (directory, caseIndex)
    resultFile = None

    # Generate output file name, if not specified.
    if not outFileName:
        # Open result file
        lt = time.localtime()
        resultFileName = "TrajAnalysis-%04d-%02d-%02d-%02d-%02d-%02d.csv" % (lt.tm_year, lt.tm_mon, lt.tm_mday, lt.tm_hour, lt.tm_min, lt.tm_sec)
        resultFilePath = path + '/' + resultFileName

    resultFile = open(resultFilePath, 'a')
    #resultFile.write("Case, Series, Target, TgtErr, TgtErrR, TgtErrA, TgtErrS, TgtErrAngle, DeltaTgtErrAngle, BxErr, BxErrR, BxErrA, BxErrS, BxErrAngle, DeltaBxErrAngle, BevelAngle, EntryErrR, EntryErrA, EntryErrS, curveRadius, SegmentLR, SegmentZone, SegmentAB, SegmentAP, DepthStart, DepthEnd, Core, TgtDispR, TgtDispA, TgtDispS\n") ## CSV header
    resultFile.write("Case, Traj, ObjName, Length, EntAng1, EntAng2, Norm1X, Norm1Y, Norm1Z, Norm2X, Norm2Y, Norm2Z\n") ## CSV header

    # Load model image
    for index in range(1, 100):
        modelImageFileName ='%s/needle-v-%02d.nrrd' % (path, index)
        modelLabelFileName ='%s/needle-v-%02d-anatomy-label.nrrd' % (path, index)
        if os.path.isfile(modelImageFileName) and os.path.isfile(modelLabelFileName):
            (r, modelImageNode) = slicer.util.loadVolume(modelImageFileName, {}, True)
            (r, modelLabelNode) = slicer.util.loadLabelVolume(modelLabelFileName, {}, True)
            break

    if not modelImageNode:
        print "Could not find baseline image: %s." % modelImageFileName
        return

    if not modelLabelNode:
        print "Could not find baseline image: %s." % modelLabelFileName
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
    sindex = index-1

    for index in range(sindex, 100):

        print index

        # Load current needle image
        needleImageFileName = '%s/needle-v-%02d.nrrd' % (path, index)
        needleImageNode = None

        if os.path.isfile(needleImageFileName):
            (r, needleImageNode) = slicer.util.loadVolume(needleImageFileName, {}, True)

        if not needleImageNode:
            print 'Could not find needle confirmation image: %s' % needleImageFileName
            continue

        # Load the corresponding trajectory data
        trajectoryFilePath = '%s/Traj-%d.fcsv' % (path, index)
        trajectoryNode = None
        if os.path.isfile(trajectoryFilePath):
            (r, trajectoryNode) = slicer.util.loadMarkupsFiducialList(trajectoryFilePath, True)

        if not trajectoryNode:
            print 'Could not find trajectory file: %s' % trajectoryFilePath
            slicer.mrmlScene.RemoveNode(needleImageNode)
            continue

        print 'Processing series %d' % index

        # Any manual transform?
        manualTransformFileName = '%s/T-%02d-to-%02d-manual.h5' % (path, baseIndex, index)
        transformNode = None
        if os.path.isfile(manualTransformFileName):
            print 'Series %02d: Manual transform has been found.' % index
            (r, transformNode) = slicer.util.loadTransform(manualTransformFileName, True)

        transformName = 'T-%02d-to-%02d' % (baseIndex, index)
        transformFileName = '%s/%s.h5' % (path, transformName)

        # If 're-registration' option is ON, any existing transform?
        if (not reRegistration) and os.path.isfile(transformFileName):
            print 'Series %02d: Existing transform has been found.' % index
            (r, transformNode) = slicer.util.loadTransform(transformFileName, True)

        # No manual / existing transform
        if not transformNode:
            print 'Series %02d: Finding initial transform.' % index
            transformNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLLinearTransformNode")
            slicer.mrmlScene.AddNode(transformNode)
            transformNode.SetName(transformName)

            RigidRegistration(modelImageNode, needleImageNode, transformNode)

            # Create initialization transform
            #transform.ApplyTransformMatrix(firstTransformMatrix)
            slicer.util.saveNode(transformNode, path+'/'+transformName+'.h5')

        # Once the transform is obtained, apply it to the models
        TransformModelHierarchy(modelHierarchyNode, transformNode)

        # Path Collision Analysis module
        pcaLogic = PathCollisionAnalysis.PathCollisionAnalysisLogic()
        [objectIDs, objectNames, normalVectors, entryAngles, totalLengthInObject] = pcaLogic.CheckIntersections(modelHierarchyNode, trajectoryNode)

        # Asume that the trajectory data traces the path from the tip to the base.
        # The first entry point in the output represents the needle's entry point into the object.
        nObjects = len(objectIDs)
        for k in range(nObjects):
            angles = entryAngles[k]
            normals = normalVectors[k]
            length = totalLengthInObject[k]
            nEntry = 2
            lb = ''
            if len(angles) < 2:
                lb = "%f, --, %f, --, --, --, %f, %f, %f" % (length, angles[0], normals[0][0], normals[0][1], normals[0][2])
            else:
                lb = "%f, %f, %f, %f, %f, %f, %f, %f, %f" % (length, angles[1], angles[0], normals[1][0], normals[1][1], normals[1][2], normals[0][0], normals[0][1], normals[0][2])

            resultFile.write("%d, %d, %s, %s\n" % (caseIndex, index, objectNames[k], lb))

        # Transform the models back to the original location
        transformNode.Inverse()
        TransformModelHierarchy(modelHierarchyNode, transformNode)

        #### Load fiducial
        # pcaLogic = PathCollisionAnalysis.PathCollisionAnalysisLogic()
        # [objectIDs, objectNames, normalVectors, entryAngles, totalLengthInObject] = pcaLogic.CheckIntersections(modelHierarchyNode, FiducialSelector.currentNode())

        slicer.mrmlScene.RemoveNode(trajectoryNode)
        slicer.mrmlScene.RemoveNode(needleImageNode)
        slicer.mrmlScene.RemoveNode(transformNode)

    RemoveModels(modelHierarchyNode)
    slicer.mrmlScene.RemoveNode(modelHierarchyNode)
    slicer.mrmlScene.RemoveNode(modelImageNode)

if __name__ ==  "__main__":
    main()
