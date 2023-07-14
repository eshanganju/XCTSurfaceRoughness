"""Code for the extraction of voxel locations 
"""

import numpy as np
import tifffile as tiffy
from circle_fit import hyperLSQ, plot_data_circle

VERBOSE = True
TESTING = False

def ComputeSurfaceRoughness(zyxSurfaceLoc):
	"""Compute the surface roughness from zyxLocation

	sa = average(| Height |)

	Height: the distance from peaks or valley to average surface
	"""
	print('\nComputing Surface Roughness')
	heightArray = zyxSurfaceLoc[:,1]
	averageHeight = np.average(heightArray)
	correctedHeightArray = abs(heightArray - averageHeight)
	correctedAverageHeight = np.average(correctedHeightArray)
	f = open("SurfaceRoughness.txt", "w")
	f.write(str(correctedAverageHeight))
	f.close()
	print('Computed Surface Roughness')
	return correctedAverageHeight


def CorrectCylindricalSurfaceProfile(zyxSurfaceLocs):
	"""Correct for curvature of the surface
	"""
	print('\nCorrecting profile for curvature')
	correctedZYXSurfaceLocs = np.zeros_like(zyxSurfaceLocs)
	
	##### Code goes here #####
	maxSliceIndex = int(np.max( zyxSurfaceLocs[ :, 0 ] ))
	indexStart = 0
	for i in range( 0, maxSliceIndex + 1 ):
		print('Checking slice: ' + str(i))
		
		# Extract y, x locations
		nextIndexStart = np.max(np.where(zyxSurfaceLocs[:,0] == i)) + 1
		yxLocations = np.zeros((nextIndexStart-indexStart, 2))
		yxLocations = zyxSurfaceLocs[indexStart:nextIndexStart,1:]
		xyLocations = yxLocations
		xyLocations[:,[0,1]] = xyLocations[:,[1,0]]

		# Fit circle
		xc,yc,r,sigma = hyperLSQ(xyLocations)
		if TESTING: print( str(xc) + ' ' + str(yc) + ' ' + str(r) )
		if TESTING: plot_data_circle(xyLocations, xc, yc, r)

		# Compute corrected y
		if yc > np.average(xyLocations[:,1]): yCorrection = yc - ( r**2 - (xyLocations[:,0] - xc)**2)**0.5
		else: yCorrection = yc + ( r**2 - (xyLocations[:,0] - xc)**2)**0.5

		# Updated correctedZYXSurfaceLocs
		correctedZYXSurfaceLocs[indexStart:nextIndexStart,0] = i
		correctedZYXSurfaceLocs[indexStart:nextIndexStart,1] = xyLocations[:,1] - yCorrection
		correctedZYXSurfaceLocs[indexStart:nextIndexStart,2] = xyLocations[:,0]

		# Update indexStart
		indexStart = nextIndexStart
		print('\tDone')


	##### Code goes here #####
	np.savetxt('CorrectedSurfaceLocation.csv',correctedZYXSurfaceLocs, delimiter=',')
	print('Corrected profile for curvature')

	return correctedZYXSurfaceLocs


def GetSurfacePoints(segmentedVolume):
	"""Extract the surface profile.
	"""
	print('\nGetting surface coordinates')
	segmentedVolume = segmentedVolume//segmentedVolume.max()
	surf = np.zeros_like(segmentedVolume)

	for z in range(0,segmentedVolume.shape[0]):
		for x in range(0,segmentedVolume.shape[2]):
			for y in range(0,segmentedVolume.shape[1]):
				if segmentedVolume[z,y,x] == 1:
					if VERBOSE: print('\tTop:' + str(z) + ','+ str(y) + ',' + str(x))
					surf[z,y,x] = 1
					break
	tiffy.imwrite('surfaceFromCode.tif',surf)

	surfaceCoordinates = np.nonzero(surf)
	surfaceLocArray = np.zeros((surfaceCoordinates[0].shape[0],3))
	surfaceLocArray[:,0] = surfaceCoordinates[0]
	surfaceLocArray[:,1] = surfaceCoordinates[1]
	surfaceLocArray[:,2] = surfaceCoordinates[2]
	np.savetxt('SurfaceLocation.csv',surfaceLocArray, delimiter=',')
	print('Obtained surface coordinates')
	return surfaceLocArray


data = tiffy.imread('0FT-Crop-Bin.tif')
zyxSurfacePoints=GetSurfacePoints(data)
correctedzyxSurfacePoints=CorrectCylindricalSurfaceProfile(zyxSurfacePoints)
surfaceRoughness=ComputeSurfaceRoughness(correctedzyxSurfacePoints)