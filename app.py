from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tempfile
import requests
import os

from main import upload_video, analyze

app = FastAPI(
    title="ADHD Reel Analyzer API",
    description="Analyze Instagram Reels using Google Gemini",
    version="3.0.0",
    servers=[
        {
            "url": "https://adhd-reel-analyzer-production-3e1a.up.railway.app"
        }
    ]
)

S3_BASE_URL = "https://adhd-videos.s3.eu-north-1.amazonaws.com/adhd.all"


class VideoRequest(BaseModel):
    video_id: int


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "ADHD Reel Analyzer API",
        "version": "3.0.0"
    }


@app.post("/analyze")
async def analyze_reel(request: VideoRequest):

    filename = f"{request.video_id:03d}.mp4"

    video_url = f"{S3_BASE_URL}/{filename}"

    response = requests.get(video_url, stream=True)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail=f"Video {filename} not found."
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:

        for chunk in response.iter_content(chunk_size=8192):
            temp.write(chunk)

        temp_path = temp.name

    try:

        print("Uploading video to Gemini...")

        video = upload_video(temp_path)

        print("Analyzing video...")

        analysis = analyze(video)

        return {
            "success": True,
            "video_id": request.video_id,
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