# Joy of Painting Image Converter: JOP Image
# Object representing a Joy of Painting image.

# Imports
from typing import Optional
from time import time
from enum import Enum
from math import floor

import nbtlib
from PIL import Image

from .Shared import intToHex, hexToInt, fullpath, tileGridIndices, averageColor

# Enums
class JopCanvasType(Enum):
    """
    The type of canvas used in a Joy of Painting image.
    """
    # Cases
    SMALL = 0
    LARGE = 1
    LONG = 2
    TALL = 3

    # Functions
    def getSize(self) -> tuple[int, int]:
        """
        Gets the native `.paint` pixel size of the image.

        Returns a size tuple of `(width, height)`.
        """
        # Get the size
        if self == JopCanvasType.SMALL:
            return (16, 16)
        elif self == JopCanvasType.LARGE:
            return (32, 32)
        elif self == JopCanvasType.LONG:
            return (32, 16)
        elif self == JopCanvasType.TALL:
            return (16, 32)
        else:
            return (0, 0)

# Classes
class JopImage:
    """
    Object representing a Joy of Painting image.
    """
    # Constants
    _ROOT_UUID = "d1ebe29f-f4e9-4572-83cd-8b2cdbfc2420"
    _CANVAS_GEN = 1
    _CANVAS_VER = 2

    # Constructors
    def __init__(self,
        canvasType: JopCanvasType,
        author: str,
        title: str,
        pixels: list[str],
        name: Optional[str] = None,
    ) -> None:
        """
        canvasType: The type of canvas used in the image.
        author: The name of the author of the image.
        title: The title of the image.
        pixels: A list of hexadecimal strings representing the colors of the pixels in the image.
        name: The UUID and Unix Timestamp identifier of the image like `<uuid>_<timestamp>`. If `None` is provided, the `_ROOT_UUID` and current Unix Timestamp will be used.
        """
        # Set the core properties
        self.canvasType = canvasType
        self.author = author
        self.title = title
        self.pixels = pixels

        # Set the name
        if name is None:
            self.name = f"{self._ROOT_UUID}_{int(time())}"
        else:
            self.name = name

    @classmethod
    def fromJopFile(cls: "JopImage", path: str) -> "JopImage":
        """
        Loads a Joy of Painting image from a file.

        path: The path to a Joy of Painting `.paint` file.

        Returns the created `JopImage` object or raises an error.
        """
        # Load the NBT data
        nbtData = nbtlib.load(path)

        # Build the pixel list
        pixels = []
        for pixel in nbtData[""]["pixels"]:
            # Get color hex
            colorHex = intToHex(pixel)

            # Remove prefix
            colorHex = colorHex[4:]

            # Add color
            pixels.append(colorHex)

        # Build the object
        return cls(
            JopCanvasType(nbtData[""]["ct"]),
            nbtData[""]["author"],
            nbtData[""]["title"],
            pixels,
            nbtData[""]["name"]
        )
    
    @classmethod
    def fromImage(
        cls: "JopImage",
        image: Image.Image,
        canvas: JopCanvasType,
        title: str,
        author: str,
        name: Optional[str] = None
    ) -> "JopImage":
        """
        Loads a standard image file and converts it to a Joy of Painting image.

        image: A PIL Image object.
        canvas: The type of canvas to use for the image. It is recommended to use a canvas type that matches the aspect ratio of the image.
        title: The title of the image.
        author: The name of the author of the image.
        name: The UUID and Unix Timestamp identifier of the image like `<uuid>_<timestamp>`. If `None` is provided, the `_ROOT_UUID` and current Unix Timestamp will be used.

        Returns the created `JopImage` object or raises an error.
        """
        # Handle name
        if name is None:
            name = f"{cls._ROOT_UUID}_{int(time())}"

        # Get sizes
        origSize = image.size
        canvasSize = canvas.getSize()

        # Calculate tile size size
        tileSize = (
            floor(origSize[0] / canvasSize[0]),
            floor(origSize[1] / canvasSize[1])
        )

        # Calculate the grid indices
        gridIndices = tileGridIndices(origSize, tileSize, startAtZero=True)

        # Loop through the grid
        pixels = []
        for gridRow in gridIndices:
            for gridTopLeft in gridRow:
                # Calculate the grid bounding box
                gridBtmRight = (
                    gridTopLeft[0] + tileSize[0],
                    gridTopLeft[1] + tileSize[1]
                )
                gridBB = (gridTopLeft[0], gridTopLeft[1], gridBtmRight[0], gridBtmRight[1])

                # Get the average color
                with image.crop(gridBB) as gridSquare:
                    # Calculate the average color
                    avgColor = averageColor(gridSquare)

                    # Convert to hex
                    colorHex = "%02x%02x%02x" % avgColor

                    # Record the color
                    pixels.append(colorHex)

        # Build the object
        return cls(
            canvas,
            author,
            title,
            pixels,
            name=name
        )

    @classmethod
    def fromImageFile(
        cls: "JopImage",
        path: str,
        canvas: JopCanvasType,
        title: str,
        author: str,
        name: Optional[str] = None
    ) -> "JopImage":
        """
        Loads a standard image file and converts it to a Joy of Painting image.

        path: The path to a standard image file.
        canvas: The type of canvas to use for the image. It is recommended to use a canvas type that matches the aspect ratio of the image.
        title: The title of the image.
        author: The name of the author of the image.
        name: The UUID and Unix Timestamp identifier of the image like `<uuid>_<timestamp>`. If `None` is provided, the `_ROOT_UUID` and current Unix Timestamp will be used.

        Returns the created `JopImage` object or raises an error.
        """
        # Handle name
        if name is None:
            name = f"{cls._ROOT_UUID}_{int(time())}"

        # Expand the path
        path = fullpath(path)

        # Load the image
        with Image.open(path) as image:
            # Load from the image
            return cls.fromImage(image, canvas, title, author, name=name)

    # Python Functions
    def __str__(self) -> str:
        return f"JopImage({self.canvasType}, {self.author}, {self.title}, {self.pixels}, {self.name})"

    def __repr__(self) -> str:
        return self.__str__()

    # Functions
    def getImage(self, size: Optional[tuple[int, int]] = None) -> Image.Image:
        """
        Gets the content of this `JopImage` as a PIL Image object.

        size: The size to save the conveted image as. Be sure to maintain the aspect ratio! If `None` is provided, the native `.paint` size will be used.
        """
        # Get the size of the canvas
        canvasSize = self.canvasType.getSize()

        # Create a new image
        image = Image.new("RGB", canvasSize, "white")

        # Iterate over grid
        for y in range(canvasSize[1]):
            for x in range(canvasSize[0]):
                # Get the pixel
                pixel = self.pixels[y * canvasSize[0] + x]

                # Convert to RGB
                r = int(pixel[0:2], 16)
                g = int(pixel[2:4], 16)
                b = int(pixel[4:6], 16)

                # Set the pixel
                image.putpixel((x, y), (r, g, b))

        # Resize the image
        if size is not None:
            image = image.resize(size, resample=Image.Resampling.NEAREST)

        return image

    def saveImage(self, path: str, size: Optional[tuple[int, int]] = None) -> None:
        """
        Saves the current `pixel` data as an image of the type specified in the `path`.

        path: The path to save the image to. Include the file name and extension.
        size: The size to save the conveted image as. Be sure to maintain the aspect ratio! If `None` is provided, the native `.paint` size will be used.
        """
        # Expand the path
        path = fullpath(path)

        # Get the image
        with self.getImage(size=size) as image:
            # Save the image
            image.save(path)

    def saveJopImage(self, path: str) -> None:
        """
        Saves the current `pixel` data as a Joy of Painting `.paint` file.

        path: The path to save the Joy of Painting image to.
        """
        # Expand the path
        path = fullpath(path)

        # Create the output data
        outputData = nbtlib.File({
            "": nbtlib.Compound({
            "generation": nbtlib.Int(self._CANVAS_GEN),
            "ct": nbtlib.Byte(self.canvasType.value),
            "pixels": nbtlib.IntArray([hexToInt(f"ff{pixel}") for pixel in self.pixels]),
            "v": nbtlib.Int(self._CANVAS_VER),
            "author": nbtlib.String(self.author),
            "name": nbtlib.String(self.name),
            "title": nbtlib.String(self.title)
            })
        })

        # Save the data
        outputData.save(path)

# Command Line
if __name__ == "__main__":
    print("No command line exists for this file.")
