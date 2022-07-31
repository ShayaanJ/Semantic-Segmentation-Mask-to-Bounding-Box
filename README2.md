# README - Omaha, NE
## Dataset contents & structure:
 - [Train|Val|Extra]  (Folders containing the different data subsets)
	 - 001 (Data derived from satelite image 001)
		 - OMA\_Tile\_\<Tile Index>\_\<Layer>\_\<Satelite Image Index>[.tif|.json] (See next section for more info on image-tile layers)
		 - ...
	 - 002 (Data derived from satelite image 002)
	 - ...
 - Metadata
	 - OMA_NITF_METADATA_\<Satelite Image Index>.json (satelite image metadata)
	 - ...
 - PointClouds.zip (See section on point clouds for format details)
	 - OMA\_Tile\_\<Tile Index>\_PC-classification.txt
	 - OMA\_Tile\_\<Tile Index>\_PC-reduced.txt
	 - ...


## Image-Tile Layers
 - AGL: Above ground height, stored as single-precision floating point values in meters.  NaN values are used to represent areas where the AGL is undetermined.
 - BLDG_FTPRINT: Building footprint, stored as 8-bit unsigned integer.  The various values represent:
	 - 2: Not a building footprint
	 - 6: Building footprint
	 - 65: Unclassified
 - CLS: Classification, stored as 8-bit unsigned integers.  The various values represent:
	 - 0: Unclassified
	 - 2: Ground
	 - 5: Foliage
	 - 6: Building
	 - 9: Water
	 - 17: Elevated Roadway
	 - 65: Unclassified
 - FACADE: Building facades, stored as 8-bit integers.  The various values represent:
	 - 6: Building (not facade)
	 - 64: Building Facades
	 - 65: Unclassified
 - PANSHARP_MSI: 8-band, pansharpened MSI imagery stored as 16-bit integers.
 - RGB: Color imagery stored as 8-bit integers.
 - SHDW: Solar shadow information stored as 8-bit integers.  The various values represent:
	 - 0: Illuminated
	 - 65: Undetermined
	 - 255: In Shadow
 - VFLOW: A JSON file containing information relevant to mapping features to ground level in pixel space.  The JSON file contains two scalar values: scale (unitless), and angle (radians).  The mapping for a particular pixel is computed by using the corresponding AGL value as follows:
 Delta_Row = AGL\*scale\*cos(angle)
 Delta_Column = AGL\*scale\*sin(angle)
 - XYZ: X,Y, and Z coordinates for each pixel, stored as single-precision floating point offsets in meters.  To convert X and Y values to full UTM coordinates, extract the metadata from the file with TIF tags 3086 (ProjFalseOriginEastingGeoKey) and 3087 (ProjFalseOriginNorthingGeoKey) and add them to X and Y respectively (the offset for Z is 0).

## Point Clouds Format
Point clouds are stored in SEMANTIC3D.NET format, i.e. comma-delimited ascii files.  The points are stored in the *-reduced.txt files, with each row defining a point, and the columns representing the following data:

 1. UTM Easting
 2. UTM Northing
 3. UTM Up
 4. Intensity
 5. Return Number

Matching classifications are stored in the corresponding rows in the *-classification.txt files, with the same values as are used in the CLS image-tile layers,

