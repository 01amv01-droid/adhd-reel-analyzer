from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
import os

from main import upload_video, analyze

app = FastAPI(
    title="ADHD Reel Analyzer API",
    description="Analyze Instagram Reels using Google Gemini",
    version="2.0.0",
    servers=[
        {
            "url": "https://adhd-reel-analyzer-production-3e1a.up.railway.app"
        }
    ]
)"
)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "ADHD Reel Analyzer API",
        "version": "2.0.0"
    }


@app.post("/analyze")
async def analyze_reel(file: UploadFile = File(...)):

    if not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a video file."
        )

    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:

        temp.write(await file.read())
        temp_path = temp.name

    try:

        print("Uploading video to Gemini...")

        video = upload_video(temp_path)

        print("Analyzing video...")

        analysis = analyze(video)

        return {
            "success": True,
            "analysis": analysis
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)