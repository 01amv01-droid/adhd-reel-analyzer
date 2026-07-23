import os
import json
import time
from dotenv import load_dotenv
from google import genai

# ==========================
# Load API Key
# ==========================
load_dotenv()  # يقرأ .env محليًا فقط إذا كان موجودًا

API_KEY = os.getenv("GEMINI_API_KEY")

# للتشخيص (احذفه لاحقًا)
print("API_KEY =", repr(API_KEY))

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is missing."
    )

client = genai.Client(api_key=API_KEY)

VIDEO_PATH = "videos/test.mp4"

PROMPT = """
You are an expert multimodal video analysis system.

Analyze the video objectively and describe only what is supported by visual or audible evidence. Do not invent information or infer unsupported facts.

Identify in maximum detail:
- Scene-by-scene timeline
- Characters and their roles
- Dialogue and speakers
- OCR (all visible text)
- Actions and interactions
- Facial expressions
- Body language and gestures
- Emotions (with confidence level)
- Eye contact
- Tone of voice
- Camera shots, angles and movements
- Environment and setting
- Objects and their relevance
- Audio, music and sound effects
- Story structure (setup, conflict, climax, ending)
- References to movies, TV shows, memes, games or internet culture

For every interpretation that is not directly observable, mark it as "uncertain".

Return ONLY valid JSON.
Do not use Markdown.
Do not explain your reasoning.
Do not omit important details.

Return ONLY valid JSON.

{
  "summary": "",
  "main_topic": "",
  "main_message": "",
  "timeline": [
    {
      "time": "",
      "scene": "",
      "actions": [],
      "characters": [
        {
          "name": "",
          "role": "",
          "emotion": "",
          "emotion_reason": "",
          "facial_expression": "",
          "body_language": "",
          "eye_contact": "",
          "voice_tone": "",
          "intention": ""
        }
      ],
      "dialogue": [
        {
          "speaker": "",
          "text": "",
          "meaning": "",
          "hidden_meaning": "",
          "humor_type": "",
          "sarcasm": false
        }
      ],
      "camera": {
        "shot": "",
        "movement": "",
        "angle": ""
      },
      "environment": "",
      "objects": [],
      "ocr": []
    }
  ],
  "psychology": {
    "viewer_emotion": "",
    "psychological_trigger": "",
    "why_it_is_funny": "",
    "humor_style": "",
    "emotional_progression": ""
  },
  "story": {
    "hook": "",
    "setup": "",
    "conflict": "",
    "punchline": "",
    "ending": ""
  },
  "editing": {
    "pace": "",
    "cuts": "",
    "transitions": ""
  },
  "references": {
    "movie": "",
    "tv_show": "",
    "characters": [],
    "internet_meme": ""
  }
}

Rules:
- Analyze every scene.
- Explain facial expressions.
- Explain body language.
- Explain emotions.
- Explain intentions.
- Explain dialogue.
- Explain hidden meanings.
- Explain context.
- Detect sarcasm.
- Detect irony.
- Detect absurd humor.
- Extract all OCR text.
- Never invent unsupported facts.
- If uncertain, say "uncertain".
- Return ONLY JSON.
"""

# ==========================
# Upload Video
# ==========================
def upload_video(path):

    print("Uploading video...")

    video = client.files.upload(file=path)

    while True:

        video = client.files.get(name=video.name)

        state = getattr(video.state, "name", str(video.state))

        print("Status:", state)

        if state == "ACTIVE":
            print("Video ready.\n")
            return video

        if state == "FAILED":
            raise RuntimeError("Video processing failed.")

        time.sleep(2)


# ==========================
# Analyze Video
# ==========================
def analyze(video):

    print("Analyzing...\n")

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[video, PROMPT]
    )

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(text)
        return data

    except json.JSONDecodeError:

        print(text)

        raise Exception("Gemini did not return valid JSON.")


# ==========================
# Save JSON
# ==========================
def save_json(data):

    with open("analysis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("analysis.json saved successfully.")


# ==========================
# Main
# ==========================
def main():

    if not os.path.exists(VIDEO_PATH):
        raise FileNotFoundError(VIDEO_PATH)

    video = upload_video(VIDEO_PATH)

    data = analyze(video)

    save_json(data)

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()