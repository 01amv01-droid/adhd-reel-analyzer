import os
import json
import time
from dotenv import load_dotenv
from google import genai

# ==========================
# Load API Key
# ==========================
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

client = genai.Client(api_key=API_KEY)

VIDEO_PATH = "videos/test.mp4"

PROMPT = r"""
You are an expert multimodal Instagram Reels analysis system specialized in short-form viral content.

Your only job is to objectively analyze the uploaded Reel and provide structured information that will later be used to generate an original ADHD meme and Instagram caption.

Never generate captions.
Never generate memes.
Never rewrite dialogue.
Never imitate the creator.

Analyze only what is supported by visual or audible evidence.

If something cannot be confirmed, return "uncertain".

Return ONLY valid JSON.

{
  "video_overview":{
    "summary":"",
    "core_idea":"",
    "main_topic":"",
    "main_message":""
  },
  "timeline":[
    {
      "time":"",
      "scene":"",
      "actions":[],
      "characters":[
        {
          "name":"",
          "role":"",
          "facial_expression":"",
          "body_language":"",
          "emotion":"",
          "emotion_confidence":"",
          "emotion_reason":"",
          "eye_contact":"",
          "voice_tone":"",
          "intention":""
        }
      ],
      "dialogue":[
        {
          "speaker":"",
          "text":"",
          "meaning":"",
          "hidden_meaning":"",
          "sarcasm":false,
          "irony":false
        }
      ],
      "camera":{
        "shot":"",
        "movement":"",
        "angle":""
      },
      "environment":"",
      "objects":[],
      "ocr":[]
    }
  ],
  "comedy":{
    "is_funny":true,
    "humor_style":"",
    "comedic_structure":"",
    "setup":"",
    "expectation":"",
    "payoff":"",
    "why_it_works":"",
    "funniest_moment":"",
    "timing_importance":"",
    "facial_expression_importance":"",
    "body_language_importance":""
  },
  "psychology":{
    "viewer_emotion":"",
    "psychological_trigger":"",
    "emotional_progression":"",
    "share_trigger":"",
    "save_trigger":""
  },
  "adhd_fit":{
    "supported":true,
    "confidence":"",
    "best_match":"",
    "other_possible_matches":[],
    "visual_evidence":[],
    "reasoning":"",
    "unsupported_symptoms":[]
  },
  "content_strategy":{
    "core_relatable_moment":"",
    "meme_pattern":"",
    "caption_angle":"",
    "viral_trigger":"",
    "shareability":"",
    "audience_takeaway":""
  },
  "story":{
    "hook":"",
    "setup":"",
    "conflict":"",
    "climax":"",
    "ending":""
  },
  "editing":{
    "pace":"",
    "cuts":"",
    "transitions":""
  },
  "references":{
    "movie":"",
    "tv_show":"",
    "internet_meme":"",
    "game":"",
    "characters":[]
  }
}

Rules
- Analyze every scene.
- Analyze every visible action.
- Analyze facial expressions.
- Analyze body language.
- Analyze timing.
- Analyze emotional progression.
- Analyze why people laugh.
- Analyze why people share.
- Analyze why people save.
- Detect sarcasm.
- Detect irony.
- Detect absurd humor.
- Detect reaction humor.
- Detect expectation vs payoff.
- Extract all OCR.
- Never invent context.
- Never invent ADHD symptoms.
- Never assume the Reel is about ADHD.
- ADHD matches must be visually supported.
- If uncertain, return "uncertain".
- Return ONLY valid JSON.
"""

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


def analyze(video):
    print("Analyzing...\n")

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[video, PROMPT],
    )

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(text)
        raise RuntimeError("Gemini did not return valid JSON.")


def save_json(data):
    with open("analysis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("analysis.json saved successfully.")


def main():
    if not os.path.exists(VIDEO_PATH):
        raise FileNotFoundError(VIDEO_PATH)

    video = upload_video(VIDEO_PATH)
    data = analyze(video)
    save_json(data)

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()
