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



def main():

    p1 = numpy.array([0, 10.0, 0.0])
    p2 = numpy.array([8.6602540378443873, 4.999999999999999, 0.0])
    p3 = numpy.array([8.0901699437494745, 5.8778525229247318, 0.0])

    radius = FitCircle(p1, p2, p3)
    
    #print intersect
    print radius


if __name__ ==  "__main__":
    main();
