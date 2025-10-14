import os
import time
import random
from datetime import datetime
import tweepy
from dotenv import load_dotenv
from threading import Thread
from flask import Flask

# Load env locally; on Railway, these are set automatically
load_dotenv()

INTERVAL_HOURS = 3
MAX_TWEET_LENGTH = 280

# Twitter API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Initialize Twitter client
twitter_client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET
)

# Topics
TOPICS = [
    "Videography",
    "Cinematography",
    "VFX (Visual Effects)",
    "Fine Art Photography",
    "Color Grading",
    "Film Editing",
    "Movies",
    "Filmmaking",
    "Camera & Lens Technology",
    "Grip & Rigging",
    "Sound Design",
    "Film Theory",
    "Great Cinematographers & Photographers",
    "Production Design"
]

# Groq API
from groq import Groq
groq_client = Groq(api_key=GROQ_API_KEY)
MODEL_ID = "llama-3.3-70b-versatile"

def generate_tweet():
    topic = random.choice(TOPICS)
    prompt = f"Write a short, engaging Fact (under 280 characters) about {topic}. Make it conversational and human-like."

    try:
        response = groq_client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}]
        )

        tweet = response.choices[0].message.content.strip()
        if len(tweet) > MAX_TWEET_LENGTH:
            tweet = tweet[:tweet[:MAX_TWEET_LENGTH].rfind(" ")] if " " in tweet else tweet[:MAX_TWEET_LENGTH]
        return tweet
    except Exception as e:
        print(f"⚠ Error generating tweet: {e}")
        return None

def post_tweet(tweet):
    try:
        response = twitter_client.create_tweet(text=tweet)
        print(f"✅ Tweet posted! ID: {response.data['id']}")
        print(f"📝 {tweet}")
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")

def run_scheduler():
    print("🚀 Groq Twitter Bot Started!")
    while True:
        print("="*60)
        print(f"🕒 Job started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        tweet = generate_tweet()
        if tweet:
            post_tweet(tweet)
        else:
            print("⚠ No tweet generated this cycle.")
        next_time = datetime.now().timestamp() + INTERVAL_HOURS * 3600
        print(f"⏭ Next post at: {datetime.fromtimestamp(next_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        time.sleep(INTERVAL_HOURS * 3600)

# -------------------------------
# Flask server to keep Railway awake
# -------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

if __name__ == "__main__":
    # Run scheduler in a separate thread
    Thread(target=run_scheduler).start()
    app.run(host="0.0.0.0", port=8000)
