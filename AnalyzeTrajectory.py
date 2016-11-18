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

path = '/Users/junichi/Dropbox/Experiments/BRP/BRPRobotCases/Scene/Case448'

def main():
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

        # Check if there is an adjusted initial transform
        adjustedInitTransformFileName = '%s/T-%02d-to-%02d-init-adjusted.h5' % (path, baseIndex, index)
        if os.path.isfile(adjustedInitTransformFileName):
            print 'Series %02d: Initial transform from File.' % index
            (r, initTransform) = slicer.util.loadTransform(adjustedInitTransformFileName, True)

        if not initTransform:
            print 'Series %02d: Finding initial transform.' % index
            initTransform = slicer.mrmlScene.CreateNodeByClass("vtkMRMLLinearTransformNode")            
            initTransformName = 'T-%02d-to-%02d-init' % (baseIndex, index)
            slicer.mrmlScene.AddNode(initTransform)
            initTransform.SetName(initTransformName)

            # Register first needle image to the current needle image
            registrationParameters['fixedVolume'] = needleImageNode.GetID()
            registrationParameters['movingVolume'] = modelImageNode.GetID()
            registrationParameters['linearTransform'] = initTransform.GetID()
            registrationParameters['initialTransform'] = ''
            registrationParameters['initializeTransformMode'] = 'Off'
            registrationParameters['maskProcessingMode'] = 'NOMASK'
            registrationParameters['fixedBinaryVolume'] = ''
            registrationParameters['movingBinaryVolume'] = ''
    
            slicer.cli.run(registrationCLI, None, registrationParameters, True)

            # Create initialization transform
            initTransform.ApplyTransformMatrix(firstTransformMatrix)
            slicer.util.saveNode(initTransform, path+'/'+initTransformName+'.h5')
            
        if initTransform:
            modelLabelNode.SetAndObserveTransformNodeID(initTransform.GetID())
            ###slicer.vtkSlicerTransformLogic.hardenTransform(modelLabelNode)
            
        # Resample mask
        needleLabelName = 'needle-t-%0d-label' % index
        needleLabelNode.SetName("needleLabelNode")
        resampleCLI = slicer.modules.brainsresample
        resampleParameters['inputVolume'] = modelLabelNode.GetID()
        resampleParameters['referenceVolume'] = needleImageNode.GetID()
        resampleParameters['outputVolume'] = needleLabelNode.GetID()
        resampleParameters['warpTransform'] = initTransform.GetID()
        slicer.cli.run(resampleCLI, None, resampleParameters, True)
        #slicer.util.saveNode(needleLabelNode, path+'/'+needleLabelName+'.nrrd')

        slicer.mrmlScene.RemoveNode(needleImageNode)
        slicer.mrmlScene.RemoveNode(needleLabelNode)
        slicer.mrmlScene.RemoveNode(initTransform)
        
    slicer.mrmlScene.RemoveNode(modelImageNode)
    slicer.mrmlScene.RemoveNode(modelLabelNode)



if __name__ ==  "__main__":
    main();
