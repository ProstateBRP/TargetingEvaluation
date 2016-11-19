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

def main():
    path = '/Users/junichi/Dropbox/Experiments/BRP/BRPRobotCases/Scene/Case448'
    ProcessCase(path):

# Create surface models from a label map and return the node ID of model hierarhcy
def CreateModels(labelMapNode, modelHierarchyNode):

    modelMakerCLI = slicer.modules.modelmaker
    # tf = tempfile.NamedTemporaryFile(prefix='Slicer/Models-', suffix='.mrml')

    modelMakerParameters = {}
    modelMakerParameters['color'] = 'vtkMRMLColorTableNodeFileGenericAnatomyColors.txt'
    modelMakerParameters['modelSceneFile'] = modelHierarchy.GetID()
    modelMakerParameters['name'] = 'Model'
    modelMakerParameters['generateAll'] = True
    modelMakerParameters['start'] =-1
    modelMakerParameters['end'] =-1
    modelMakerParameters['skipUnNamed'] = True
    modelMakerParameters['jointsmooth'] = True
    modelMakerParameters['smooth'] = 15
    modelMakerParameters['filtertype'] = 'Sinc'
    modelMakerParameters['decimate'] = 0.25
    modelMakerParameters['splitnormals'] = True
    modelMakerParameters['pointnormals'] = True
    modelMakerParameters['pad'] = labelMapNode.GetID()

    slicer.cli.run(resampleCLI, None, resampleParameters, True)


def TrasformModelHierarchy(modelHierarchyNode, transformNode):
    if not transformNode:
        return False

    # modelLabelNode.SetAndObserveTransformNodeID(transformNode.GetID())
    # slicer.vtkSlicerTransformLogic.hardenTransform(modelLabelNode)
    collection = vtk.vtkCollection()
    modelHierarchyNode.GetAssociatedNode(collection)
    if collection:
        nModels = collection.GetNumberOfItems()
        for i in range(nModels):
            model = collection.GetItemAsObject(i)
            model.SetAndObserveTransformNodeID(transformNode.GetID())
            slicer.vtkSlicerTransformLogic.hardenTransform(model)
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
    registrationParameters['fixedVolume'] = needleImageNode.GetID()
    registrationParameters['movingVolume'] = modelImageNode.GetID()
    registrationParameters['linearTransform'] = transform.GetID()
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


def ProcessCase(path, reRegistration=False):
    # Find base image (for anatomy segmentation)
    index = 0
    modelImageNode = None
    modelLabelNode = None

    # Load model image
    for index in range(1, 100):
        modelImageFileName ='%s/needle-v-%02d.nrrd' % (path, index)
        modelLabelFileName ='%s/needle-v-%02d-anatomy-label.nrrd' % (path, index)
        if os.path.isfile(modelImageFileName) and os.path.isfile(modelLabelFileName):
            (r, modelImageNode) = slicer.util.loadVolume(modelImageFileName, {}, True)
            (r, modelLabelNode) = slicer.util.loadVolume(modelLabelFileName, {}, True)
            break

    if not (modelImageNode and modelLabelNode):
        return

    # Create 3D models
    print "Creating 3D surface models for %s " % modelLabelFileName
    modelHierarchyNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelHierarchyNode")
    CreateModels(modelLabelNode, modelHierarchyNode)

    baseIndex = index
    sindex = index-1

    for index in range(sindex, 100):

        print index

        # Load current needle image
        needleImageFileName ='%s/needle-v-%02d.nrrd' % (path, index)
        needleImageNode = None

        if os.path.isfile(needleImageFileName):
            (r, needleImageNode) = slicer.util.loadVolume(needleImageFileName, {}, True)

        if not needleImageNode:
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
        if (not reRegistration) && os.path.isfile(transformFileName):
            print 'Series %02d: Existing transform has been found.' % index
            (r, transformNode) = slicer.util.loadTransform(transformFileName, True)

        # No manual / existing transform
        if not transformNode:
            print 'Series %02d: Finding initial transform.' % index
            transform = slicer.mrmlScene.CreateNodeByClass("vtkMRMLLinearTransformNode")
            slicer.mrmlScene.AddNode(transform)
            transform.SetName(transformName)

            RigidRegistration(modelImageNode, needleImageNode, transformNode)

            # Create initialization transform
            #transform.ApplyTransformMatrix(firstTransformMatrix)
            slicer.util.saveNode(transform, path+'/'+transformName+'.h5')

        # Once the transform is obtained, apply it to the models
        TransformModelHierarchy(modelHierarchyNode, transformNode)

        #### Load fiducial
        # pcaLogic = PathCollisionAnalysis.PathCollisionAnalysisLogic()
        # [objectIDs, objectNames, normalVectors, entryAngles, totalLengthInObject] = pcaLogic.CheckIntersections(modelHierarchyNode, FiducialSelector.currentNode())

        slicer.mrmlScene.RemoveNode(needleImageNode)
        slicer.mrmlScene.RemoveNode(needleLabelNode)
        slicer.mrmlScene.RemoveNode(transform)

    slicer.mrmlScene.RemoveNode(modelImageNode)
    slicer.mrmlScene.RemoveNode(modelLabelNode)



if __name__ ==  "__main__":
    main()
