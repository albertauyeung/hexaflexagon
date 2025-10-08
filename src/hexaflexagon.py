from PIL import Image, ImageDraw, ImageOps
import math

from utils import draw_dash_line, rotate_and_crop


class HexaflexagonGenerator:

    """
    Configuration for arranging triangles in the final template
    - Each tuple is (image_index, triangle_index, rotation_angle)
    - Indices are 1-based
    - Rotation angles are in degrees anti-clockwise
    - Triangles are indexed clockwise starting from bottom-left one
    """
    configuration_row_1 = [
        (1, 2, 240),
        (1, 3, 240),
        (2, 5, 60),
        (2, 6, 60),
        (3, 5, 60),
        (3, 6, 60),
        (1, 6, 120),
        (1, 1, 120),
        (2, 3, 300),
        (2, 4, 300),
    ]
    configuration_row_2 = [
        (3, 3, 300),
        (3, 4, 300),
        (1, 4, 0),
        (1, 5, 0),
        (2, 1, 180),
        (2, 2, 180),
        (3, 1, 180),
        (3, 2, 180),
    ]

    def __init__(self, image_paths: list[str], image_width: int, output_path: str):
        """
        Args:
            image_paths (list[str]): List of 3 image file paths.
            image_width (int): Width and height to which each image will be resized (square).
            output_path (str): Path to save the final hexaflexagon template image.
        """
        self.image_paths = image_paths
        self.image_width = image_width
        self.output_path = output_path

    def _crop_and_scale(self, image: Image) -> Image.Image:
        """
        Crop and scale the input image to a square of the specified size.
        """
        return ImageOps.fit(image, (self.image_width, self.image_width), Image.LANCZOS)

    def _get_hexagon_vertices(self, image: Image) -> list[tuple[float, float]]:
        """
        Return the vertices of a hexagon drawn on the image.
        """
        draw = ImageDraw.Draw(image)
        width, height = image.size
        cx, cy = width // 2, height // 2  # centre of the image
        rad = width // 2  # radius of the hexagon (half the size of the image)

        # Calculate the vertices of the hexagon
        vertices = [
            (
                cx + rad * math.cos(math.radians(angle)),
                cy + rad * math.sin(math.radians(angle))
            )
            for angle in range(0, 360, 60)
        ]

        # Draw the hexagon
        draw.polygon(vertices, outline="grey", width=2)

        # Draw dashed diagonal lines from center to each vertex
        for vertex in vertices:
            draw_dash_line(
                image=image,
                start=(cx, cy),
                end=vertex,
                fill="grey",
            )

        return vertices

    def _get_hexagon_triangles(
        self, 
        image: Image, 
        vertices: list[tuple[float, float]]
    ) -> list[Image.Image]:
        cx, cy = image.size[0] // 2, image.size[1] // 2  # Center of the image
        num_triangles = len(vertices)  # 6 triangles in total

        triangles = []

        for i in range(num_triangles):
            tri_vertices = [vertices[i], vertices[(i + 1) % num_triangles], (cx, cy)]

            # Create a blank, transparent background image
            triangle_img = Image.new("RGBA", image.size, (0, 0, 0, 0))

            # Create a mask to define the triangle
            mask = Image.new("L", image.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.polygon(tri_vertices, fill=255)

            # Paste the original image onto the transparent image using the mask
            triangle_img.paste(image, mask=mask)

            # Crop to the smallest bounding box of the triangle (optional step)
            bbox = mask.getbbox()
            if bbox:
                triangle_img = triangle_img.crop(bbox)

            triangles.append(triangle_img)
        
        return triangles

    def generate(self):
        """
        Generate the hexaflexagon template and save it to the output path.
        """
        # Load the images
        images = [
            self._crop_and_scale(Image.open(path).convert("RGBA"))
            for path in self.image_paths
        ]

        # Extract triangles from each image
        triangles = {}
        for idx, image in enumerate(images):
            vertices = self._get_hexagon_vertices(image)

            triangles[idx + 1] = {}
            for j, triangle in enumerate(self._get_hexagon_triangles(image, vertices)):
                triangles[idx + 1][j + 1] = triangle

        # Create the output canvas
        canva_length = int(5.5 * self.image_width / 2)
        canva_height = int(2 * (0.5 * math.sqrt(3) * self.image_width / 2))
        canva_size = (canva_length, canva_height)
        canva = Image.new("RGBA", canva_size, (255, 255, 255))

        # Paste the triangles onto the canvas based on the configuration
        # First row
        x_offset = 0
        y_offset = 0
        for img, index, degree in self.configuration_row_1:
            tri = triangles[img][index]
            tri = rotate_and_crop(tri, degree)
            position = (x_offset, y_offset)
            canva.paste(tri, position, tri)
            x_offset += int(self.image_width / 4)

        # Second row
        x_offset = int(self.image_width / 4)
        y_offset = int(canva_height / 2)
        for img, index, degree in self.configuration_row_2:
            tri = triangles[img][index]
            tri = rotate_and_crop(tri, degree)
            position = (x_offset, y_offset)
            canva.paste(tri, position, tri)
            x_offset += int(self.image_width / 4)

        # Draw lines of the white triangles
        draw = ImageDraw.Draw(canva)
        draw.line(
            [
                (0, int(canva_height / 2)),
                (int(self.image_width/4), canva_height)
            ],
            fill="grey",
            width=3
        )
        draw.line(
            [
                (5 * self.image_width / 2, int(canva_height / 2)),
                (int(5.5 * self.image_width / 2), canva_height)
            ],
            fill="grey",
            width=3
        )
        draw.line(
            [
                (int(4.5 * self.image_width / 2), canva_height),
                (int(5.5 * self.image_width / 2), canva_height)
            ],
            fill="grey",
            width=3
        )

        # Output the image
        canva.save(self.output_path)
