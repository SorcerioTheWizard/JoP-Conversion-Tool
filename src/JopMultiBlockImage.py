# Joy of Painting Image Converter: JOP Multi-Canvas Image
# Object representing an image composed of multiple Joy of Painting canvases to create a higher resolution representation of an image.

# Imports
import os
import random
from uuid import uuid4
from typing import Optional

from PIL import Image

from .Shared import fullpath, tileGridIndices, stringToAsciiInt, constrainToPowerOfTwo
from .JopImage import JopCanvasType, JopImage

# Classes
class JopMultiBlockImage:
    """
    Object representing an image composed of multiple Joy of Painting canvases to create a higher resolution representation of an image.
    """
    # Constants
    _MAX_RAND_TIMESTAMP = 10000

    # Constructors
    def __init__(self,
        author: str,
        title: str,
        imageGrid: list[list[JopImage]]
    ) -> None:
        """
        author: The name of the author of the image.
        title: The title of the image.
        imageGrid: A 2D list of `JopImage` objects representing the image.
        """
        # Set properties
        self.author = author
        self.title = title
        self.imageGrid = imageGrid

        # Check if the names are valid
        if not self.areNamesValid():
            print("The names of JopImage objects in the grid are not unique!\nIssues will occur when importing into Minecraft!")

    @classmethod
    def fromImage(
        cls: "JopMultiBlockImage",
        gridSize: tuple[int, int],
        image: Image.Image,
        title: str,
        author: str,
        canvas: JopCanvasType = JopCanvasType.LARGE
    ) -> "JopMultiBlockImage":
        """
        Accepts a PIL Image and converts its grid components into a set of Joy of Painting images.

        gridSize: The size of the grid as a tuple of `(width, height)` where each cell is a Joy of Painting Large Canvas. A size of `(2, 2)` would create a 4 Large Canvas grid.
        image: A PIL image object to convert.
        title: The title of the image.
        author: The name of the author of the image.
        canvas: The type of canvas to use for the image.

        Returns the created `JopMultiBlockImage` object or raises an error.
        """
        # Constrain the grid size to a power of two
        with constrainToPowerOfTwo(image) as imageSized:
            # Get the full image size
            imageFullSize = imageSized.size

            # Calculate the tile size
            tileSize = (imageFullSize[0] // gridSize[0], imageFullSize[1] // gridSize[1])

            # Calculate the grid indicies
            gridIndicies = tileGridIndices(imageFullSize, tileSize, startAtZero=True)

            # Build the root painting id
            rootId = cls.generatePaintingId(title, author)

            # Load the segment grid
            imageGrid: list[list[JopImage]] = [[None for _ in range(gridSize[0])] for _ in range(gridSize[1])]
            curId = rootId
            for y in range(gridSize[1]):
                for x in range(gridSize[0]):
                    # Get the segment image
                    gridTopLeft = gridIndicies[y][x]
                    with imageSized.crop((*gridTopLeft, gridTopLeft[0] + tileSize[0], gridTopLeft[1] + tileSize[1])) as segmentImage:
                        # Convert to a JopImage
                        jopSegment = JopImage.fromImage(
                            segmentImage,
                            canvas,
                            f"{title} ({x}, {y})",
                            author,
                            name=f"{JopImage._ROOT_UUID}_{curId}"
                        )

                    # Record the image in the grid
                    imageGrid[y][x] = jopSegment

                    # Increment the id
                    curId += 1

        return cls(
            author,
            title,
            imageGrid
        )

    @classmethod
    def fromImageFile(
        cls: "JopMultiBlockImage",
        gridSize: tuple[int, int],
        path: str,
        title: str,
        author: str,
        canvas: JopCanvasType = JopCanvasType.LARGE
    ) -> "JopMultiBlockImage":
        """
        Loads a standard image file and converts its grid components into a set of Joy of Painting images.

        gridSize: The size of the grid as a tuple of `(width, height)` where each cell is a Joy of Painting Large Canvas. A size of `(2, 2)` would create a 4 Large Canvas grid.
        path: The path to the image file.
        title: The title of the image.
        author: The name of the author of the image.
        canvas: The type of canvas to use for the image.

        Returns the created `JopMultiBlockImage` object or raises an error.
        """
        # Load the full image
        with Image.open(fullpath(path)) as imageFull:
            return cls.fromImage(
                gridSize,
                imageFull,
                title,
                author,
                canvas=canvas
            )

    # Python Functions
    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        """
        return f"JopMultiBlockImage({self.name}, {self.author}, {self.title}, {self.imageGrid})"

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.
        """
        return self.__str__()

    # Static Functions
    @staticmethod
    def generatePaintingId(title: str, author: str) -> int:
        """
        Generates a painting id that is extremely likely to be unique within any given Minecraft world.

        title: The title of the painting.
        author: The author of the painting.

        Returns an integer identifier.
        """
        return (stringToAsciiInt(f"{title} {author}") + stringToAsciiInt(uuid4()) + random.randint(0, JopMultiBlockImage._MAX_RAND_TIMESTAMP))

    # Functions
    def saveImage(self, path: str, size: Optional[tuple[int, int]]) -> None:
        """
        Saves the current `imageGrid` data as single combined image.

        path: The path to save the images to. Include the file name and extension.
        size: The size of the individual images that will makeup the combined image. If `None` is provided, the original image size will be used. Overall output size is dependent on the size of the individual images and the grid.
        """
        # Expand the path
        path = fullpath(path)

        # Combine the images in the grid
        with Image.new(
            "RGB",
            (
                size[0] * len(self.imageGrid[0]),
                size[1] * len(self.imageGrid)
            )
        ) as combinedImage:
            # Loop through the grid
            for y in range(len(self.imageGrid)):
                for x in range(len(self.imageGrid[y])):
                    # Paste the image onto the combined image
                    combinedImage.paste(self.imageGrid[y][x].getImage(size=size), (x * size[0], y * size[1]))

            # Save the combined image
            combinedImage.save(path)

    def saveImageGrid(self, path: str, size: Optional[tuple[int, int]]) -> list[str]:
        """
        Saves the current `imageGrid` data as a grid of indivigual images.

        path: The path to save the images to. Include the file name and extension. A grid index will be appended to the end of the file name like `name_<x>_<y>.png`.
        size: The size of the individual images to save. If `None` is provided, the original image size will be used.

        Returns a list of the paths to the saved images.
        """
        # Expand the path
        path = fullpath(path)

        # Get the path parts
        dirPath, fileName, fileExt = self._getPathParts(path)

        # Loop through the image grid
        paths = []
        for y in range(len(self.imageGrid)):
            for x in range(len(self.imageGrid[y])):
                # Save the image
                jopPath = os.path.join(dirPath, f"{fileName}_{x}_{y}{fileExt}")
                self.imageGrid[y][x].saveImage(jopPath, size)

                # Record the path
                paths.append(jopPath)

        return paths

    def saveJopImageGrid(self, path: str) -> list[str]:
        """
        Saves the current `imageGrid` data as a grid of Joy of Painting image.

        path: The path to save the Joy of Painting image to. Include the file name and extension. A grid index will be appended to the end of the file name like `name_<x>_<y>.paint`.

        Returns a list of the paths to the saved `.paint` files.
        """
        # Expand the path
        path = fullpath(path)

        # Get the path parts
        dirPath, fileName, _ = self._getPathParts(path)

        # Save the image grid
        paths = []
        for y in range(len(self.imageGrid)):
            for x in range(len(self.imageGrid[y])):
                # Save the image
                jopPath = os.path.join(dirPath, f"{fileName}_{x}_{y}.paint")
                self.imageGrid[y][x].saveJopImage(jopPath)

                # Record the path
                paths.append(jopPath)

        return paths

    def areNamesValid(self) -> bool:
        """
        Checks if all names of Joy of Painting images in the grid are unique.

        Returns `True` if all names are unique and therefore valid.
        """
        # Get all names
        names = [image.name for row in self.imageGrid for image in row]

        # Check for duplicates
        return (len(names) == len(set(names)))

    # Private Functions
    def _getPathParts(self, path: str) -> tuple[str, str, str]:
        """
        Splits the path into parts.

        path: The path to split.

        Returns a tuple of `(dirPath, fileName, fileExt)`.
        """
        # Get the path parts
        dirPath = os.path.dirname(path)
        fileName, fileExt = os.path.splitext(os.path.basename(path))

        if fileExt[0] != ".":
            fileExt = f".{fileExt}"

        return dirPath, fileName, fileExt

# Command Line
if __name__ == "__main__":
    print("No command line exists for this file.")
