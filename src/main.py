import sys

from hexaflexagon import HexaflexagonGenerator


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 4:
        print("Usage: python hexaflexagon.py <image1> <image2> <image3> [output_file] [triangle_size]")
        print("Example: python hexaflexagon.py face1.jpg face2.png face3.jpg output.png 300")
        sys.exit(1)
    
    image_paths = sys.argv[1:4]
    output_path = sys.argv[4] if len(sys.argv) > 4 else 'output.png'
    triangle_size = int(sys.argv[5]) if len(sys.argv) > 5 else 500

    generator = HexaflexagonGenerator(
        image_paths=image_paths,
        image_width=triangle_size,
        output_path=output_path
    )
    generator.generate()
