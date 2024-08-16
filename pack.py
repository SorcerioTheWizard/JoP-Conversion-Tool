# Joy of Painting Image Converter: Executable Packer
# Packs the Joy of Painting Image Converter executable into a distributable package.

# Imports
import os
import shutil
import zipfile
import platform

# Constants
DIST_DIR = "dist"
DIST_FILE_PREFIX = "JoPPaintingTool_"
ASSET_PATHS = [
    "README.md",
    "LICENSE"
]

# Functions
def fullpath(path: str):
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

def getDistribution():
    # Get the distribution based on the system
    system = platform.system().lower()
    architecture = platform.architecture()[0]
    if system == "windows":
        if architecture == "64bit":
            return "win64"
        elif architecture == "32bit":
            return "win32"
    elif system == "linux":
        return "linux"
    elif system == "darwin":
        return "macos"

    # Unknown distribution
    print("Unknown distribution. Please name manually.")
    return "unknown"

def copyAssets(inputPaths: list[str], outputDir: str):
    # Get absolute paths
    inputPaths = [fullpath(p) for p in inputPaths]
    outputDir = fullpath(outputDir)

    # Copy the assets
    for filepath in inputPaths:
        # Prepare the export path
        exportPath = os.path.join(outputDir, os.path.basename(filepath))

        # Copy file or directory
        if os.path.isfile(filepath):
            shutil.copy(filepath, exportPath)
        elif os.path.isdir(filepath):
            shutil.copytree(filepath, exportPath)

        # Report
        print(f"Copied {os.path.basename(filepath)} to: {exportPath}")

def zipForDist(inputDir: str, outputDir: str, outputFilePrefix: str):
    # Get the full input dir
    inputDir = fullpath(inputDir)

    # Create the output path
    outputPath = os.path.join(fullpath(outputDir), f"{outputFilePrefix}{getDistribution()}.zip")

    # Create the zip file
    with zipfile.ZipFile(outputPath, "w") as zipf:
        # Walk the input directory
        for root, _, files in os.walk(inputDir):
            for file in files:
                # Exclude the zip file
                if os.path.splitext(file)[1] == ".zip":
                    continue

                # Write the file
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), inputDir))

    # Report
    print(f"Created distribution zip file: {outputPath}")

# Command Line
if __name__ == "__main__":
    copyAssets(ASSET_PATHS, DIST_DIR)
    zipForDist(DIST_DIR, DIST_DIR, DIST_FILE_PREFIX)
