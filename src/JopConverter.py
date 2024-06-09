# Joy of Painting Image Converter: Converter
# Utility for conversion of images to the Joy of Painting `.paint` format and vice versa.

# Imports
import os
from typing import Optional

from .Shared import fullpath
from .JopImage import JopImage, JopCanvasType
from .JopMultiBlockImage import JopMultiBlockImage

# Classes
class JopImageConverter:
    """
    Utility for conversion of images to the Joy of Painting `.paint` format and vice versa.
    """
    # Functions
    def exportImage(self,
        inPath: str,
        outPath: str,
        size: Optional[tuple[int, int]]
    ) -> JopImage:
        """
        Converts a Joy of Painting `.paint` format image to a standard image format.

        inPath: A Joy of Painting `.paint` file to convert.
        outPath: The path to save the converted image with extension.
        size: The size to save the converted image as. Be sure to maintain the aspect ratio! If `None` is provided, the native `.paint` size will be used.

        Returns the created `JopImage` object.
        """
        # Convert the paths
        inPath = fullpath(inPath)
        outPath = fullpath(outPath)

        # Load the input file
        jopImage: JopImage = JopImage.fromJopFile(inPath)

        # Export the image
        jopImage.saveImage(outPath, size=size)

        # Report
        print(f"Exported {os.path.basename(inPath)} to: {outPath}")

        return jopImage

    def importImage(self,
        inPath: str,
        outPath: str,
        title: str,
        author: str,
        canvasType: JopCanvasType = JopCanvasType.LARGE
    ) -> JopImage:
        """
        Converts a standard image format to a Joy of Painting `.paint` format.

        inPath: A standard image file to convert.
        outPath: The path to save the converted `.paint` file.
        title: The title of the image.
        author: The name of the author of the image.
        canvasType: The canvas type to use for the Joy of Painting image. This defines the aspect ratio and size of the resulting `.paint` image.

        Returns the created `JopImage` object.
        """
        # Convert the paths
        inPath = fullpath(inPath)
        outPath = fullpath(outPath)

        # Load the input file
        jopImage: JopImage = JopImage.fromImageFile(
            inPath,
            canvasType,
            title,
            author
        )

        # Save the Joy of Painting image
        jopImage.saveJopImage(outPath)

        # Report
        print(f"Imported {os.path.basename(inPath)} to: {outPath}")

        return jopImage

    def importImageOnGrid(self,
        inPath: str,
        outPath: str,
        gridSize: tuple[int, int],
        title: str,
        author: str,
        canvasType: JopCanvasType = JopCanvasType.LARGE
    ) -> JopMultiBlockImage:
        """
        Converts a standard image format to a grid of Joy of Painting `.paint` format images creating a high resolution representation out of multiple canvases.

        inPath: A standard image file to convert.
        outPath: The path to save the converted `.paint` file. A grid index will be appended to the end of the file name like `name_<x>_<y>.paint`.
        gridSize: The size of the grid as a tuple of `(width, height)` where each cell is a Joy of Painting Large Canvas. A size of `(2, 2)` would create a 4 Large Canvas grid.
        title: The title of the image.
        author: The name of the author of the image.
        canvasType: The canvas type to use for the Joy of Painting image. This defines the aspect ratio and size of the resulting `.paint` images in the grid.

        Returns the created `JopMultiBlockImage` object.
        """
        # Convert the paths
        inPath = fullpath(inPath)
        outPath = fullpath(outPath)

        # Load the input file
        jopMultiImage: JopMultiBlockImage = JopMultiBlockImage.fromImageFile(
            gridSize,
            inPath,
            title,
            author,
            canvas=canvasType
        )

        # Save the Joy of Painting image
        outPaths = jopMultiImage.saveJopImageGrid(outPath)

        # Report
        print(f"Imported {os.path.basename(inPath)} to:")
        for i, path in enumerate(outPaths):
            print(f"\t{i}: {path}")

        return jopMultiImage

# Command Line
if __name__ == "__main__":
    print("No command line exists for this file.")
