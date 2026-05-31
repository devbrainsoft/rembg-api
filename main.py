from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove, new_session
from PIL import Image
import io

app = FastAPI(title="RemBG API", version="1.0.0")

# Preload model at startup
rembg_session = None

@app.on_event("startup")
async def startup_event():
    global rembg_session
    print("Loading U2Net model...")
    rembg_session = new_session("u2net")
    print("Model loaded ✅")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "RemBG API is running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, WEBP allowed")

    try:
        contents = await file.read()
        input_image = Image.open(io.BytesIO(contents))

        # Use preloaded session
        output_image = remove(input_image, session=rembg_session)

        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return Response(
            content=img_byte_arr.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=result.png"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
