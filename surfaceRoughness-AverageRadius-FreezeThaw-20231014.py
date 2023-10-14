"""Code for the extraction of voxel locations 
"""

import numpy as np
import tifffile as tiffy
from circle_fit import hyperLSQ, plot_data_circle

VERBOSE = True
TESTING = False

def ComputeSurfaceRoughness(zyxSurfaceLoc,fileName='',ofl=''):
	"""Compute the surface roughness from zyxLocation
	sa = average(| Height |)
	Height: the distance from peaks or valley to average surface
	"""
	print('\nComputing Surface Roughness')
	heightArray = zyxSurfaceLoc[:,1]
	averageHeight = np.average(heightArray)
	standardDeviation = np.std(heightArray)

	fileOutputName = ofl + fileName + '-SurfaceRoughnessValue.csv'
	f = open(fileOutputName,"w")
	f.write(str(averageHeight) + ',' + str(standardDeviation))
	f.close()
	print('Computed Surface Roughness')
	return averageHeight, standardDeviation


def CorrectCylindricalSurfaceProfile(zyxSurfaceLocs,fileName='',ofl=''):
	"""Correct for curvature of the surface
	"""

	print('\nCorrecting profile for curvature')
	correctedZYXSurfaceLocs = np.zeros_like(zyxSurfaceLocs)

	maxSliceIndex = int(np.max( zyxSurfaceLocs[ :, 0 ] ))
	indexStart = 0

	locAndR =np.zeros((maxSliceIndex+1,5)).astype('float')

	for i in range( 0, maxSliceIndex + 1 ):
		print('Checking slice: ' + str(i))

		# Extract y, x locations
		nextIndexStart = np.max(np.where(zyxSurfaceLocs[:,0] == i)) + 1
		yxLocations = np.zeros((nextIndexStart-indexStart, 2))
		yxLocations = zyxSurfaceLocs[indexStart:nextIndexStart,1:]
		# xyLocations = yxLocations
		# xyLocations[:,[0,1]] = xyLocations[:,[1,0]]

		# Fit circle
		yc,xc,r,sigma = hyperLSQ(yxLocations)
		locAndR[i,0] = i
		locAndR[i,1] = yc
		locAndR[i,2] = xc
		locAndR[i,3] = r
		locAndR[i,4] = sigma

		if TESTING: print( str(xc) + ' ' + str(yc) + ' ' + str(r) )
		if TESTING: plot_data_circle(xyLocations, xc, yc, r)

		# Update indexStart
		indexStart = nextIndexStart
		print('\tDone')

	averageY = np.average(locAndR[:,1])
	averageX = np.average(locAndR[:,2])
	averageR = np.average(locAndR[:,3])

	# print(averageX)
	# print(averageY)
	# print(averageR)

	correctedZYXSurfaceLocs[:,0] = zyxSurfaceLocs[:,0]	# Z
	correctedZYXSurfaceLocs[:,1] = np.absolute((( zyxSurfaceLocs[:,2] - averageX )**2 + (zyxSurfaceLocs[:,1] - averageY)**2 )**0.5 - averageR)						# Y
	correctedZYXSurfaceLocs[:,2] = zyxSurfaceLocs[:,2]	# X


	fileOutputName = ofl + fileName + '-CorrectedSurfaceLocation.csv'
	fileOutputName2 = ofl + fileName + '-centersAndRadii.csv'
	np.savetxt(fileOutputName, correctedZYXSurfaceLocs, delimiter=',')
	np.savetxt(fileOutputName2, locAndR, delimiter=',')
	print('Corrected profile for curvature')

	return correctedZYXSurfaceLocs


def GetSurfacePoints(segmentedVolume,fileName='',ofl=''):
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
	imageOutName = ofl + fileName + '-Surface.tif'
	tiffy.imwrite(imageOutName,surf)

	surfaceCoordinates = np.nonzero(surf)
	surfaceLocArray = np.zeros((surfaceCoordinates[0].shape[0],3))
	surfaceLocArray[:,0] = surfaceCoordinates[0]
	surfaceLocArray[:,1] = surfaceCoordinates[1]
	surfaceLocArray[:,2] = surfaceCoordinates[2]

	fileOutputName = ofl + fileName + '-SurfaceLocation.csv'
	np.savetxt(fileOutputName,surfaceLocArray, delimiter=',')
	print('Obtained surface coordinates')
	return surfaceLocArray


ofl = '/home/crg/Documents/Datasets/AnkitSurfaceRoughness/Freeze-Thaw/WithCorrosionLayer/OutputFiles/'
ifl = '/home/crg/Documents/Datasets/AnkitSurfaceRoughness/Freeze-Thaw/WithCorrosionLayer/'
files = ['450FT','800FT','1100FT','1600FT']

for file in files:
	data = tiffy.imread( ifl + file + '.tif' )
	zyxSurfacePoints=GetSurfacePoints(data,fileName=file,ofl=ofl)
	correctedzyxSurfacePoints=CorrectCylindricalSurfaceProfile(zyxSurfacePoints,fileName=file,ofl=ofl)
	surfaceRoughness, stdRoughness = ComputeSurfaceRoughness(correctedzyxSurfacePoints,fileName=file,ofl=ofl)
	print(surfaceRoughness)
	print(stdRoughness)