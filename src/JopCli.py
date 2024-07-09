# Joy of Painting Image Converter: Command Line
# Command line program for converting images to and from the Joy of Painting `.paint` format.

# Imports
import os
import argparse

from .JopConverter import JopImageConverter
from .JopImage import JopCanvasType

# Constants
_KEY_COMMAND_EXPORT = "export"
_KEY_COMMAND_IMPORT = "import"

_PREV_SIZE_MULTIPLIER = 32

# Functions
def runJopCli():
    """
    Starts the Joy of Painting Image Converter command line program.
    """
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Utility for conversion of images to the Joy of Painting `.paint` format and vice versa."
    )

    # Setup the subparsers
    subparsers = parser.add_subparsers(dest="command", title="commands")

    # Setup the export parser
    exportParser = subparsers.add_parser(_KEY_COMMAND_EXPORT, help="Convert a Joy of Painting `.paint` file to a standard image format.")

    exportParser.add_argument("inPath", type=str, help="An input file path pointing to a Joy of Painting `.paint` file.")
    exportParser.add_argument("outPath", type=str, help="An output file path to save the converted image to with extension.")

    exportParser.add_argument("-s", "--size", nargs=2, action="append", metavar=("WIDTH", "HEIGHT"), help="An explicit size to save the converted image as. Be sure to maintain the aspect ratio!", type=int, default=None)

    # Setup the import parser
    importParser = subparsers.add_parser(_KEY_COMMAND_IMPORT, help="Convert a standard image file to a Joy of Painting `.paint` format.")

    importParser.add_argument("inPath", type=str, help="An input file path pointing to a standard image file. For best results, input an image with dimensions that are a power of 2. The image will be resized to the nearest power of 2 before conversion if necessary.")
    importParser.add_argument("outPath", type=str, help="An output file path to save the converted Joy of Painting `.paint` file to with the `.paint` extension.")

    importParser.add_argument("-t", "--title", type=str, help="The title of the image.", default="Untitled")
    importParser.add_argument("-a", "--author", type=str, help="The name of the author of the image.", default="Unknown")
    importParser.add_argument("-c", "--canvasType", type=str, help="The canvas type to use for the Joy of Painting image. This defines the aspect ratio and size of the resulting `.paint` image.", choices=[canvasType.name.lower() for canvasType in JopCanvasType], default=JopCanvasType.LARGE.name.lower())
    importParser.add_argument("-p", "--preview", help="If provided, a preview `.png` image of a visible size will be included alongside the `.paint` file.", action="store_true")
    importParser.add_argument("-g", "--grid", nargs=2, action="append", metavar=("WIDTH", "HEIGHT"), help="If provided, the image will be imported as a grid of Joy of Painting Canvases. This creates a larger but higher resolution representation of the input image. A size of `2 2` would create a 2x2 grid made of 4 Large Canvases.", type=int, default=None)

    # Parse the arguments
    args = parser.parse_args()

    # Create the converter
    converter = JopImageConverter()

    # Execute command
    if args.command == _KEY_COMMAND_EXPORT:
        # Define size
        if args.size is None:
            outSize = None
        else:
            outSize = tuple(args.size[0])

        # Export image
        converter.exportImage(args.inPath, args.outPath, outSize)
    elif args.command == _KEY_COMMAND_IMPORT:
        # Attempt to get the canvas type
        canvasType = JopCanvasType[args.canvasType.upper()]

        # Create the preview path
        previewPath = os.path.join(os.path.dirname(args.outPath), f"{os.path.splitext(os.path.basename(args.outPath))[0]}_preview.png")

        # Calculate the preview size
        previewSize = (
            canvasType.getSize()[0] * _PREV_SIZE_MULTIPLIER,
            canvasType.getSize()[1] * _PREV_SIZE_MULTIPLIER
        )

        # Import image
        if args.grid:
            # Import as grid
            jopGrid = converter.importImageOnGrid(args.inPath, args.outPath, args.grid[0], args.title, args.author, canvasType=canvasType)

            # Check for preview
            if args.preview:
                # Export the grid previews
                jopGrid.saveImage(previewPath, previewSize)
                outCells = jopGrid.saveImageGrid(previewPath, previewSize)

                # Report
                print(f"Exported {os.path.basename(args.inPath)} to: {previewPath}")
                print(f"Exported {os.path.basename(args.inPath)} grid to:")
                for i, cell in enumerate(outCells):
                    print(f"\t{i}: {cell}")
        else:
            # Import as single image
            jopImage = converter.importImage(args.inPath, args.outPath, args.title, args.author, canvasType=canvasType)

            # Check for preview
            if args.preview:
                # Export the preview
                jopImage.saveImage(previewPath, previewSize)

                # Report
                print(f"Exported {os.path.basename(args.inPath)} preview to: {previewPath}")

# Command Line
if __name__ == "__main__":
    runJopCli()
