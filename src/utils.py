from PIL import Image, ImageDraw, ImageChops


def draw_dash_line(
    image: Image.Image,
    start: tuple[float, float],
    end: tuple[float, float],
    dash_length=10,
    gap_length=5,
    line_width=2,
    fill="black"
) -> Image:
    """
    Draw a dashed line on the image from start to end.
    
    Args:
        image (PIL.Image): The image to draw on.
        start (tuple): Starting point (x, y).
        end (tuple): Ending point (x, y).
        dash_length (int): Length of each dash.
        gap_length (int): Length of the gap between dashes.
        line_width (int): Width of the line.
        fill (str or tuple): Color of the line.

    Returns:
        PIL.Image: The image with the dashed line drawn on it.
    """
    draw = ImageDraw.Draw(image)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = (dx**2 + dy**2) ** 0.5
    
    if distance == 0:
        return  # No line to draw
    
    unit_x = dx / distance
    unit_y = dy / distance
    
    current_distance = 0
    drawing_dash = True
    
    while current_distance < distance:
        segment_length = dash_length if drawing_dash else gap_length
        end_distance = min(current_distance + segment_length, distance)
        
        if drawing_dash:
            start_x = start[0] + current_distance * unit_x
            start_y = start[1] + current_distance * unit_y
            end_x = start[0] + end_distance * unit_x
            end_y = start[1] + end_distance * unit_y
            draw.line([(start_x, start_y), (end_x, end_y)], fill=fill, width=line_width)
        
        current_distance = end_distance
        drawing_dash = not drawing_dash

    return image


def rotate_and_crop(image: Image.Image, degree: float) -> Image.Image:
    """
    Rotate and crop the image to remove any white space.

    Args:
        image (PIL.Image): The image to rotate and crop.
        degree (float): The angle to rotate anticlockwise.
    
    Returns:
        PIL.Image: The rotated and cropped image.
    """
    # 1. Rotate the image with expand=True
    rotated = image.rotate(degree, expand=True, fillcolor=(255,255,255,0))

    # 2. Crop white space (here, we assume white is exactly 255,255,255
    # We'll make a mask of all non-white pixels
    def crop_white(im):
        bg = Image.new(im.mode, im.size, (255,255,255,0))
        diff = ImageChops.difference(im, bg)
        bbox = diff.getbbox()
        return im.crop(bbox)
    
    cropped = crop_white(rotated)
    
    # 3. Make white fully transparent
    datas = cropped.getdata()
    newData = []
    for item in datas:
        # item is (R, G, B, A)
        if item[0] >= 250 and item[1] >= 250 and item[2] >= 250:
            # set alpha to 0 for white (adjust threshold if desired)
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    cropped.putdata(newData)
    return cropped
