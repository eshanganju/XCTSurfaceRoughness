Pre code:
	1-Orient data to have average surface normal aligned with +y direction
	2-Extract subvolume
	3-Binarized subvolume

Code:
	1-Extract the top surface of the binarized subvolume
	2-Correct for curvature (to be implemented as of 07.09.2023)
	3-Compute average surface height (of corrected surface)
	4-Subtract average suface height from surface elevation
	5-Computed average of the absolute subtracted heights to get Sa
