
ADHD Reel Analyzer - First Version

Setup:

1. Install Python 3.10+

2. Install packages:

pip install -r requirements.txt

3. Rename:
.env.example

to:

.env

4. Add your Gemini API key:

GEMINI_API_KEY=YOUR_KEY

5. Put your Reel video here:

videos/test.mp4

6. Run:

python main.py

The program sends the video to Gemini and returns a detailed analysis.
