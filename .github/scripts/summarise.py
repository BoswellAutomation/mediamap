import openai
import feedparser
from datetime import datetime, timedelta
import json
import os

openai.api_key = os.environ['OPENAI_API_KEY']

feeds = [
    "https://feeds.bbci.co.uk/news/england/london/rss.xml",
    # Add more RSS feeds here if you want!
]

yesterday = datetime.utcnow() - timedelta(days=1)
stories = []
for url in feeds:
    d = feedparser.parse(url)
    for entry in d.entries:
        pub = getattr(entry, 'published_parsed', None)
        if pub and datetime(*pub[:6]) > yesterday:
            desc = getattr(entry, 'summary', '')
            stories.append(f"{entry.title} — {desc}")

text = '\n'.join(stories)[:12000]
prompt = (
    "Summarise these London news stories from the past 24 hours into a short, readable daily update for the public. "
    "Group similar stories and mention any important themes, events, or patterns. "
    "Write it in the style of a daily briefing, like 'London today: ...'. Highlight recurring themes and only mention the most important news.\n"
    + text
)

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=400,
)
summary = response.choices[0].message.content

with open("summaries/daily-summary.json", "w") as f:
    json.dump({"summary": summary, "updated": datetime.utcnow().isoformat()}, f, indent=2)

print("Summary written to summaries/daily-summary.json")
