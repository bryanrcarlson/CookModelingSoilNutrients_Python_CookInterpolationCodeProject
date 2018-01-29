import pandas as pd
import arcpy
import os
from os import listdir
from os.path import isfile, join
import argparse

# ---- FUNCTIONS ----

def interpolateFieldVariablesFile(
    arcpyWorkspace,
    inputFilePath,
    startColumn
):
    EXTENT_COOK_EAST = "493370.923667054 5180613.73134777 493976.389445712 5180995.70484399"
    EXTENT_COOK_WEST = "492842.2706117 5180831.8982194 493350.270611698 5181287.89821941"

    arcpy.env.workspace = arcpyWorkspace
    arcpy.env.overwriteOutput = True
    tempDirName = "temp"
    tempDir = os.path.join(arcpy.env.workspace, tempDirName)
    arcpy.CreateFolder_management(arcpy.env.workspace, tempDirName)
    arcpy.env.scratchWorkspace = tempDir

    #inFile = inputFilePath
    #inFilePath = os.path.join(arcpy.env.workspace, "Input", inFile)
    df = pd.read_csv(inputFilePath, sep = ",", header="infer")

    BoundaryCookWest = os.path.join(
        arcpy.env.workspace, 
        "Input", 
        "Boundaries", 
        "CWcatchment_line.shp")
    
    BoundaryCookEast = os.path.join(
        arcpy.env.workspace, 
        "Input", 
        "Boundaries", 
        "CookEastDUwS_Conservative_line.shp")
    
    # Make feature layer from input
    inputLayer = "inputLayer"
    spRef = arcpy.SpatialReference(r"Input\32611.prj")
    arcpy.MakeXYEventLayer_management(
        inputFilePath, 
        "EASTING", 
        "NORTHING", 
        inputLayer, spRef)

    # Get site so we know what boundaries to us
    # NOTE: This assumes one site per file
    siteId = df["SITE"][1]
    boundary = ""
    if(siteId == "Cook East"):
        arcpy.env.extent = EXTENT_COOK_EAST
        boundary = BoundaryCookEast
    elif(siteId == "Cook West"):
        arcpy.env.extent = EXTENT_COOK_WEST
        boundary = BoundaryCookWest

    # Get depth, convert to string - this is for naming the file
    # NOTE: Assumes one depth per file
    depth = str(df["DEPTH_CM"][1])
    fieldName = siteId.replace(" ", "")

    # Do the work
    for column in df.columns[int(startColumn):]:
        varName = column.replace(" ", "")
        outFileName = fieldName + "_" + varName + "_" + depth + "cm"
        outFilePath = os.path.join(arcpy.env.workspace, "Output", outFileName + ".tif")
        
        print("Processing %s..." % varName)
        try:
            arcpy.gp.Idw_sa(inputLayer, column, outFilePath, "", "2", "VARIABLE 12", boundary)
            print("... Created file %s" % outFilePath)
        except Exception as e: 
            print("... Failed to create file: %s" % e)

def interpolateFieldVariablesDirectory(
    arcpyWorkspace,
    inputDirPath,
    startColumn
):
    inFiles = [f for f in listdir(inputDirPath) if isfile(join(inputDirPath, f))]
    inFiles = [f for f in inFiles if f.endswith(".csv")]

    print("Found %s input files" % len(inFiles))

    

    for f in inFiles:
        if(f.endswith(".csv")):
            print("Processing file: %s" % f)
            interpolateFieldVariablesFile(
                arcpyWorkspace, 
                join(inputDirPath, f), 
                startColumn)
            print("... Created file: %s" % join(inputDirPath, f))
        else:
            print("... Skipping file: %s" % f)

    outFiles = [join(arcpyWorkspace, "Output", f) for f in listdir(join(arcpyWorkspace, "Output")) if isfile(join(arcpyWorkspace, "Output", f))]
    outFiles = [f for f in outFiles if f.endswith(".tif")]

    print("Finished interpolation, moving on to mosaic...")
    print("Found %s generated files" % len(outFiles))

    while len(outFiles)  > 0:
        f = outFiles[0]
        if(f.endswith(".tif")):
            # Get list of similar tifs
            nameWithoutFieldId = f.replace(f.split("_")[0] + "_", "")
            rasters = [f for f in outFiles if nameWithoutFieldId in f]
            
            if(len(rasters) > 1):
                # Combine similar fields using Mosaic function
                print("Combining files similar to: %s..." % f)
                try:
                    arcpy.MosaicToNewRaster_management(";".join(rasters), "Output", nameWithoutFieldId, "", "32_BIT_FLOAT", "", 1, "LAST", "FIRST")
                    print("... Created file %s" % nameWithoutFieldId)
                except Exception as e: 
                    print("... Failed to create file: %s" % e)
                
            # Remove this and similar file(s) from file list
            outFiles = [f for f in outFiles if f not in rasters]
            
        else:
            print("Skipping file: %s" % f)

# ---- MAIN ----

parser = argparse.ArgumentParser(
    description="Description"
)
parser.add_argument('-i', '--inputpath', help = 'Absolute path to file or directory with spatial data (in csv format) to be interpolated', required=True)
parser.add_argument('-c', '--startcol', help = "Column number of which you wish to interporlate it and all columns to the right of it", required=True)
parser.add_argument('-wd', '--workingdir', help = "Working directory for ArcPy, creates a \"temp\" and assumes an \"Output\" directory", required=True)

args = parser.parse_args()

print("Input dir: %s" % args.inputpath)
print("Start column: %s" % args.startcol)
print("Working dir: %s" % args.workingdir)

if(isfile(args.inputpath)):
    print("Input path is a file, assuming interpolation of a single file and not multiple files in a directory.")
    arcpy.CheckOutExtension("spatial")
    interpolateFieldVariablesFile(
        args.workingdir, 
        args.inputpath, 
        args.startcol)
    arcpy.CheckInExtension("spatial")
else:
    print("Input path is a directory, assuming interpolation of all files in directory and mosaic similarly named files.")
    arcpy.CheckOutExtension("spatial")
    interpolateFieldVariablesDirectory(
        args.workingdir,
        args.inputpath,
        args.startcol)
    arcpy.CheckInExtension("spatial")

print("==== DONE ====")