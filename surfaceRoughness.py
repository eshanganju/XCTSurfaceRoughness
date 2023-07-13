"""Code for the extraction of voxel locations 
"""

import numpy as np
import tifffile as tiffy
VERBOSE = True

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
	"""Fit a cylindrical curve to zyxLocations and subtract the curve to get corrected profile zyx
	Option1: https://stackoverflow.com/questions/43784618/fit-a-cylinder-to-scattered-3d-xyz-point-data
	Option2: https://github.com/CristianoPizzamiglio/py-cylinder-fitting
	Option3: https://github.com/xingjiepan/cylinder_fitting
	"""
	print('\nCorrecting profile for curvature')
	##### Code goes here #####


	##### Code goes here #####
	print('Corrected profile for curvature')
	return zyxSurfaceLocs


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


data = tiffy.imread('/home/crg/Documents/Datasets/AnkitSurfaceRoughness/0 FT/0FT-Crop-Bin.tif')
zyxSurfacePoints=GetSurfacePoints(data)
correctedzyxSurfacePoints=CorrectCylindricalSurfaceProfile(zyxSurfacePoints)
surfaceRoughness=ComputeSurfaceRoughness(correctedzyxSurfacePoints)