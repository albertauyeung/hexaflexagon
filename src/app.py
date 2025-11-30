from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import io
import tempfile
import os
from PIL import Image

try:
    from .hexaflexagon import HexaflexagonGenerator
except ImportError:
    from hexaflexagon import HexaflexagonGenerator

app = FastAPI(title="Hexaflexagon Generator")

# Serve static files
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Serve assets
assets_dir = Path(__file__).parent.parent / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main page"""
    html_file = Path(__file__).parent.parent / "static" / "index.html"
    if html_file.exists():
        return html_file.read_text()
    return "<h1>Hexaflexagon Generator</h1><p>Please create static/index.html</p>"


@app.get("/instructions", response_class=HTMLResponse)
async def read_instructions():
    """Serve the folding instructions page"""
    html_file = Path(__file__).parent.parent / "static" / "instructions.html"
    if html_file.exists():
        return html_file.read_text()
    return "<h1>Instructions</h1><p>Please create static/instructions.html</p>"


@app.post("/generate")
async def generate_hexaflexagon(
    image1: UploadFile = File(..., description="First image for the hexaflexagon"),
    image2: UploadFile = File(..., description="Second image for the hexaflexagon"),
    image3: UploadFile = File(..., description="Third image for the hexaflexagon"),
    image_size: int = 500
):
    """
    Generate a hexaflexagon template from three uploaded images.

    Args:
        image1: First image file
        image2: Second image file
        image3: Third image file
        image_size: Size to scale each image to (default: 500)

    Returns:
        PNG file containing the hexaflexagon template
    """

    # Validate file types
    allowed_types = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
    for img_file in [image1, image2, image3]:
        if img_file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {img_file.content_type}. Only JPEG, PNG, and WebP are allowed."
            )

    # Validate image size
    if image_size < 100 or image_size > 2000:
        raise HTTPException(
            status_code=400,
            detail="Image size must be between 100 and 2000 pixels"
        )

    try:
        # Create temporary files for the uploaded images
        temp_files = []
        temp_dir = tempfile.mkdtemp()

        for idx, upload_file in enumerate([image1, image2, image3], 1):
            # Read the file content
            content = await upload_file.read()

            # Validate it's a valid image
            try:
                img = Image.open(io.BytesIO(content))
                img.verify()
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {upload_file.filename} is not a valid image"
                )

            # Save to temporary file
            temp_path = os.path.join(temp_dir, f"image{idx}.png")
            with open(temp_path, "wb") as f:
                f.write(content)
            temp_files.append(temp_path)

        # Generate the hexaflexagon
        output_path = os.path.join(temp_dir, "hexaflexagon.png")
        generator = HexaflexagonGenerator(
            image_paths=temp_files,
            image_width=image_size,
            output_path=output_path
        )
        generator.generate()

        # Return the generated file
        return FileResponse(
            output_path,
            media_type="image/png",
            filename="hexaflexagon.png",
            headers={
                "Cache-Control": "no-cache",
                "Content-Disposition": "attachment; filename=hexaflexagon.png"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating hexaflexagon: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
