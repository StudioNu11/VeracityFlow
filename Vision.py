from google.genai import types
import mss
import mss.tools
import os
import json
from gemini_client import client

def vision():
    try:
        with mss.MSS() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            output_filename = "temp.jpg"

            mss.tools.to_png(screenshot.rgb, screenshot.size, output=output_filename)

        with open("temp.jpg", "rb") as f:
            image_bytes = f.read()

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=["""You are a claim extraction and search query generation system.

            Analyze the provided screenshot and determine the primary factual claim, headline, announcement, report, or message being communicated.

            Ignore advertisements, usernames, profile pictures, comments, reactions, timestamps, navigation bars, and other UI elements unless they are necessary to understand the claim.

            The claim may be implicit. Infer the central message from the surrounding context when necessary.

            Rewrite the claim as a concise, objective statement while preserving important people, organizations, locations, dates, numbers, products, events, and statistics. Remove opinions, clickbait, emotional language, emojis, hashtags, promotional wording, and unnecessary wording.

            Generate 3-4 concise search queries that maximize the chance of finding authoritative evidence. Prefer official documentation, official announcements, product pages, help-center articles, or major news outlets. Avoid generic or redundant queries. Each query should target a different aspect of verifying the claim.

            Search query requirements:
                - Focus on verifying the extracted claim, not simply repeating visible text.
                - Prioritize official sources, announcements, documentation, and major news outlets.
                - Include important names, organizations, products, locations, dates, and numbers where relevant.
                - Use concise keyword-style search queries.
                - Generate different query variations that maximize the chance of finding reliable evidence.
                - Do not include the content creator's name unless the claim is specifically about them.

            If the screenshot contains no meaningful factual claim (for example: a desktop wallpaper, settings page, game menu, blank screen, or ordinary conversation), return:

            {
            "claim": null,
            "search_queries": []
            }

            Otherwise, return ONLY a valid JSON object in this exact format:

            {
            "claim": "Extracted factual claim",
            "search_queries": [
                "Query 1",
                "Query 2",
                "Query 3",
                "Query 4"
                ]
                }

            Rules:
                - Return ONLY the JSON object.
                - Do NOT use Markdown.
                - Do NOT use code blocks.
                - Do NOT include explanations or additional text.
                - The output must be valid JSON that can be parsed directly using Python's json.loads().
                - The output must be valid JSON that can be parsed directly using Python's json.loads().
                - The output must be valid JSON that can be parsed directly using Python's json.loads().
                - The output must be valid JSON that can be parsed directly using Python's json.loads().
                - The output must be valid JSON that can be parsed directly using Python's json.loads().
                - The output must be valid JSON that can be parsed directly using Python's json.loads().
                - The output must be valid JSON that can be parsed directly using Python's json.loads().
                - The output must be valid JSON that can be parsed directly using Python's json.loads().
                - The output must be valid JSON that can be parsed directly using Python's json.loads().""", types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg",
                    )],
            config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

        data = json.loads(response.text)
        return data

    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)
