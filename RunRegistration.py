import os
import os.path
import unittest
import random
import math
import tempfile
import time
import numpy
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

path = '/Users/junichi/Dropbox/Experiments/BRP/BRPRobotCases/Scene/Case267'

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
    
    
    # Find plannig image
    index = 0
    planningImageNode = None
    planningLabelNode = None
    
    # Load planning image
    for index in range(1, 50):
        planningImageFileName ='%s/planning-%02d.nrrd' % (path, index)
        planningLabelFileName ='%s/planning-%02d-label.nrrd' % (path, index)
        if os.path.isfile(planningImageFileName) and os.path.isfile(planningLabelFileName):
            (r, planningImageNode) = slicer.util.loadVolume(planningImageFileName, {}, True)
            (r, planningLabelNode) = slicer.util.loadVolume(planningLabelFileName, {}, True)
            break
    
    if not (planningImageNode and planningLabelNode):
        return
    
    sindex = index
    
    firstNeedleImageNode = None
    firstNeedleLabelNode = None
    
    # Load first needle image
    for index in range(sindex, 50):
    
        firstNeedleImageFileName ='%s/needle-t-%02d.nrrd' % (path, index)
        firstNeedleLabelFileName ='%s/needle-t-%02d-label.nrrd' % (path, index)
    
        if os.path.isfile(firstNeedleImageFileName):
            (r, firstNeedleImageNode) = slicer.util.loadVolume(firstNeedleImageFileName, {}, True)
    
        if os.path.isfile(firstNeedleLabelFileName):
            (r, firstNeedleLabelNode) = slicer.util.loadVolume(firstNeedleLabelFileName, {}, True)
    
        if firstNeedleImageNode and firstNeedleLabelNode:
            break
    
    if not firstNeedleLabelNode:
        return
    
    # Register the planning image to the first needle image
    firstNeedleImageTransform = slicer.mrmlScene.CreateNodeByClass("vtkMRMLLinearTransformNode")
    firstNeedleImageTransformName = 'T-%02d' % index
    slicer.mrmlScene.AddNode(firstNeedleImageTransform)
    firstNeedleImageTransform.SetName(firstNeedleImageTransformName)
    
    registrationCLI = slicer.modules.brainsfit
    registrationParameters['fixedVolume'] = firstNeedleImageNode.GetID()
    registrationParameters['movingVolume'] = planningImageNode.GetID()
    registrationParameters['linearTransform'] = firstNeedleImageTransform.GetID()
    registrationParameters['initialTransform'] = ''
    registrationParameters['initializeTransformMode'] = 'useCenterOfROIAlign'
    registrationParameters['maskProcessingMode'] = 'ROI'
    registrationParameters['fixedBinaryVolume'] = firstNeedleLabelNode.GetID()
    registrationParameters['movingBinaryVolume'] = planningLabelNode.GetID()
    slicer.cli.run(registrationCLI, None, registrationParameters, True)     
    
    slicer.util.saveNode(firstNeedleImageTransform, path+'/'+firstNeedleImageTransformName+'.h5')
    firstTransformMatrix = vtk.vtkMatrix4x4()
    firstNeedleImageTransform.GetMatrixTransformToParent(firstTransformMatrix)

    sindex = index+1
    for index in range(sindex, 50):

        # Load current needle image
        needleImageFileName ='%s/needle-t-%02d.nrrd' % (path, index)
        needleLabelFileName ='%s/needle-t-%02d-label.nrrd' % (path, index)
    
        needleImageNode = None
        needleLabelNode = None
        
        if os.path.isfile(needleImageFileName):
            (r, needleImageNode) = slicer.util.loadVolume(needleImageFileName, {}, True)
    
        if not needleImageNode:
            continue
        
        print 'Processing series %d' % index

        # Check if there is a label data
        if os.path.isfile(needleLabelFileName):
            (r, needleLabelNode) = slicer.util.loadVolume(needleLabelFileName, {}, True)

        initTransform = None

        if not needleLabelNode:
            # Check if there is an adjusted initial transform
            adjustedInitTransformFileName = '%s/T-%02d-init-adjusted.h5' % (path, index)
            if os.path.isfile(adjustedInitTransformFileName):
                print 'Series %02d: Initial transform from File.' % index
                (r, initTransform) = slicer.util.loadTransform(adjustedInitTransformFileName, True)

            if not initTransform:
                print 'Series %02d: Finding intiial transform.' % index
                initTransform = slicer.mrmlScene.CreateNodeByClass("vtkMRMLLinearTransformNode")            
                initTransformName = 'T-%02d-init' % index
                slicer.mrmlScene.AddNode(initTransform)
                initTransform.SetName(initTransformName)

                # Register first needle image to the current needle image
                registrationParameters['fixedVolume'] = needleImageNode.GetID()
                registrationParameters['movingVolume'] = firstNeedleImageNode.GetID()
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
                # Resample mask
                needleLabelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLScalarVolumeNode")
                slicer.mrmlScene.AddNode(needleLabelNode)
                needleLabelName = 'needle-t-%0d-label' % index
                needleLabelNode.SetName("needleLabelNode")
                resampleCLI = slicer.modules.brainsresample
                resampleParameters['inputVolume'] = planningLabelNode.GetID()
                resampleParameters['referenceVolume'] = needleImageNode.GetID()
                resampleParameters['outputVolume'] = needleLabelNode.GetID()
                resampleParameters['warpTransform'] = initTransform.GetID()
                slicer.cli.run(resampleCLI, None, resampleParameters, True)
                #slicer.util.saveNode(needleLabelNode, path+'/'+needleLabelName+'.nrrd')

        # Registration
        needleImageTransform = slicer.mrmlScene.CreateNodeByClass("vtkMRMLLinearTransformNode")
        needleImageTransformName = 'T-%02d' % index
        slicer.mrmlScene.AddNode(needleImageTransform)
        needleImageTransform.SetName(needleImageTransformName)
    
        registrationParameters['fixedVolume'] = needleImageNode.GetID()
        registrationParameters['movingVolume'] = planningImageNode.GetID()
        registrationParameters['linearTransform'] = needleImageTransform.GetID()
        if initTransform:
            print 'Series %02d: useCenterOfROIAlign: OFF' % index
            registrationParameters['initialTransform'] = initTransform.GetID()
            registrationParameters['initializeTransformMode'] = 'Off'
        else: # Use label data loaded from the file
            print 'Series %02d: useCenterOfROIAlign: ON' % index
            registrationParameters['initialTransform'] = ''
            registrationParameters['initializeTransformMode'] = 'useCenterOfROIAlign'
        registrationParameters['maskProcessingMode'] = 'ROI'
        registrationParameters['fixedBinaryVolume'] = needleLabelNode.GetID()
        registrationParameters['movingBinaryVolume'] = planningLabelNode.GetID()
        slicer.cli.run(registrationCLI, None, registrationParameters, True)     
    
        slicer.util.saveNode(needleImageTransform, path+'/'+needleImageTransformName+'.h5')
    
        slicer.mrmlScene.RemoveNode(needleImageNode)
        slicer.mrmlScene.RemoveNode(needleLabelNode)
        slicer.mrmlScene.RemoveNode(initTransform)
        slicer.mrmlScene.RemoveNode(needleImageTransform)
        
    slicer.mrmlScene.RemoveNode(planningImageNode)
    slicer.mrmlScene.RemoveNode(planningLabelNode)
    slicer.mrmlScene.RemoveNode(firstNeedleImageNode)
    slicer.mrmlScene.RemoveNode(firstNeedleLabelNode)
    slicer.mrmlScene.RemoveNode(firstNeedleImageTransform)


if __name__ ==  "__main__":
    main();
