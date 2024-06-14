# Joy of Painting Image Converter: Shared Functionality
# Shared functionality for the Joy of Painting Image Converter.

# Imports
import os
import struct
from typing import Any

import numpy as np
from PIL import Image

# Functions
def fullpath(path):
    """
    Returns the full path of a file or directory.
    """
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

def intToHex(n: int) -> str:
    """
    Converts an integer to a hexadecimal string.

    n: The integer to convert.

    Returns a hexadecimal string.
    """
    if n < 0:
        n = n & 0xFFFFFFFF

    return hex(n)

def hexToInt(h: str) -> int:
    """
    Converts a hexadecimal string to a signed integer.

    h: The hexadecimal string to convert.

    Returns a signed integer.
    """
    return struct.unpack(">i", bytes.fromhex(h))[0]

def stringToAsciiInt(o: Any) -> int:
    """
    Converts the object to an ASCII integer representation.

    o: The object to convert. `str()` will be called on the object.

    Returns an integer representing the ASCII sum of the object
    """
    return sum([ord(c) for c in str(o)])

def tileGridIndices(
        gridSize: tuple[int, int],
        tileSize: tuple[int, int],
        startAtZero: bool = False
    ) -> np.ndarray:
        """
        Calculates a 2d numpy array (grid) of pixel indices.

        gridSize: A size tuple representing the size of the total grid to calculate indices for.
        tileSize: A size tuple representing the size of each tile in the grid.
        startAtZero: If `True`, the first grid index will be `(0, 0)`. If `False`, the first grid index will be `(tileSize[0] / 2, tileSize[1] / 2)`.

        Returns the pixel index grid going from top left to bottom right.
        """
        # Calculate starting point
        startPoint = (0, 0)
        if not startAtZero:
            startPoint = (
                round(tileSize[0] / 2),
                round(tileSize[1] / 2)
            )

        # Generate grid indices
        x = np.arange(startPoint[0], gridSize[0], tileSize[0])
        y = np.arange(startPoint[1], gridSize[1], tileSize[1])
        xx, yy = np.meshgrid(x, y)

        # Stack arrays along a new axis
        indexGrid = np.stack((xx, yy), axis=-1)

        return indexGrid

def averageColor(image: Image.Image) -> tuple[int, int, int]:
    """
    Calculates average color of the given image.

    image: A PIL Image.

    Returns the average color of the given image as an RGB tuple.
    """
    # Load list of colors
    colors = np.unique(np.reshape(np.array(image.convert("RGB")), (-1, 3)), axis=0) # RGB list

    # Get the average color
    avgColor = np.mean(colors, axis=0)

    return (
        round(avgColor[0]),
        round(avgColor[1]),
        round(avgColor[2])
    )

def constrainToPowerOfTwo(image: Image.Image, resample: Image.Resampling = Image.Resampling.NEAREST) -> Image.Image:
    """
    Constrains the width and height of the image to the nearest respective power of 2.

    image: A PIL Image.
    resample: The resampling filter to use when resizing the image.

    Returns a new PIL Image with the constrained dimensions. If no change is necessary, a copy of the original image is returned.
    """
    # Get the image size
    width, height = image.size

    # Check if the image is already a power of 2
    if ((width & (width - 1)) == 0) and ((height & (height - 1)) == 0):
        return image.copy()

    # Calculate the nearest power of 2 for width and height
    newWidth = (2 ** int(np.ceil(np.log2(width))))
    newHeight = (2 ** int(np.ceil(np.log2(height))))

    return image.resize((newWidth, newHeight), resample=resample)

# Command Line
if __name__ == "__main__":
    print("No command line exists for this file.")
