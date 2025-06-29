# ==============================================================================
# FILE: app.py
# Main Flask application - entry point
# ==============================================================================

from flask import Flask, render_template, request, jsonify
import os
import json
from src.config import Config
from src.database import Database

from src.news_aggregator import get_news_articles
from src.filter_top_k import get_top_articles
from src.prompt_generator import generate_meme_prompts
from src.meme_generator import generate_meme_image


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config) 
    
    @app.route('/api/generate', methods=['POST'])
    def generate_meme():
        # Get JSON data from request body
        data = request.get_json()
        
        # Extract fields with defaults
        trends = data.get('trends', [])  # List of keywords
        duration = data.get('duration', 1)  # Days back, default to 1
        
        # Call your methods with the extracted data
        articles = get_news_articles(trends, days_back=duration)
        top_articles = get_top_articles(articles, 10, trends)
        prompts = generate_meme_prompts(top_articles)
        memes = generate_meme_image(prompts)

        # Filter successful memes
        successful_memes = [meme for meme in memes["memes"] if meme["success"]]
        
        if successful_memes:
            # Read existing memes
            try:
                with open("database/memes.json", "r") as f:
                    existing_memes = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_memes = []
            
            # Append new memes
            existing_memes.extend(successful_memes)
            
            # Write back
            with open("database/memes.json", "w") as f:
                json.dump(existing_memes, f, indent=2)
        
        # Return the prompts as JSON
        return jsonify(memes)
    
    @app.route('/api/memes')
    def get_memes():
        with open("database/memes.json", "r") as f:
            memes = json.load(f)
        return jsonify(memes)
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🎭 Starting AI Meme Factory...")
    print("🔑 Make sure to set your OPENAI_API_KEY and NEWS_API_KEY environment variables!")
    print(f"📰 News API Key configured: {'✅' if Config.NEWS_API_KEY != 'your-news-api-key-here' else '❌'}")
    print(f"🤖 OpenAI API Key configured: {'✅' if Config.OPENAI_API_KEY != 'your-openai-key-here' else '❌'}")
    app.run(debug=True, host='0.0.0.0', port=5000)
