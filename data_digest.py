import feedparser
import os
import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 1. INDUSTRY FEEDS
FEEDS = {
    "dbt": "https://www.getdbt.com/blog/rss.xml",
    "Databricks": "https://www.databricks.com/blog/feed",
    "Airbyte": "https://airbyte.com/blog/rss.xml",
    "Snowflake": "https://www.snowflake.com/blog/feed/",
    "DuckDB": "https://duckdb.org/feed.xml",
    "Dagster": "https://dagster.io/blog/rss.xml",
    "StarRocks": "https://www.starrocks.io/blog/rss.xml",
    "Microsoft Fabric": "https://blog.fabric.microsoft.com/en-us/blog/feed/",
    "AWS Big Data": "https://aws.amazon.com/blogs/big-data/feed/",
    "Google Cloud Data": "https://cloud.google.com/blog/products/data-analytics/rss",
    "Confluent": "https://www.confluent.io/blog/feed/",
    "Pinecone": "https://www.pinecone.io/blog/rss.xml"
}

def fetch_weekly_news():
    digest_input = []
    now = datetime.datetime.now(datetime.timezone.utc)
    print("Selecting top articles for DataWithDhana...")
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]: 
                date_tuple = entry.get('published_parsed') or entry.get('updated_parsed')
                if date_tuple:
                    pub_date = datetime.datetime(*date_tuple[:6], tzinfo=datetime.timezone.utc)
                    if (now - pub_date).days <= 10: 
                        digest_input.append(f"COMPANY: {source} | TITLE: {entry.title} | LINK: {entry.link}")
        except: continue
    return "\n".join(digest_input)

def generate_html_content(news_text):
    prompt = f"""
    You are a Lead Data Architect. Select the TOP 10 most impactful articles.
    
    Output a RESPONSIVE GRID of 10 Box-style Cards.
    
    STYLE RULES:
    - GRID: Use <div class="grid grid-cols-1 md:grid-cols-2 gap-8">.
    - CARD STYLE: Background #0f172a, Border 1px #1e293b, Padding 8 (p-8), Rounded-2xl.
    - NO Markdown (no ```).
    
    FOR EACH CARD (Top 10 Only):
    1. A small, subtle '01' style index number in the top right.
    2. Company Badge: Cyan text (#22d3ee), bold, uppercase, small text.
    3. Title: White text, font-bold, text-xl, 2-line limit.
    4. Strategic Impact: 2 sentences max in slate-400 text.
    5. 'Read Source' Link: Simple cyan link with an arrow (→).
    
    NEWS DATA:
    {news_text}
    """
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "Return ONLY raw HTML tags. No backticks."},
                  {"role": "user", "content": prompt}]
    )
    
    return completion.choices[0].message.content.replace("```html", "").replace("```", "").strip()

def save_as_html_file(ai_content):
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Engineering Weekly News | Data With Dhana</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #020617; color: #f8fafc; }}
            .news-card {{
                background: #0f172a;
                border: 1px solid rgba(255,255,255,0.05);
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                height: 100%;
            }}
            .news-card:hover {{
                border-color: #22d3ee;
                background: #111827;
                transform: translateY(-4px);
                box-shadow: 0 20px 40px -20px rgba(34, 211, 238, 0.2);
            }}
        </style>
    </head>
    <body class="p-6 md:p-16 lg:p-24">
        <div class="max-w-6xl mx-auto">
            <header class="mb-20 text-center md:text-left border-b border-slate-800 pb-12">
                <h1 class="text-4xl md:text-6xl font-extrabold text-white tracking-tighter mb-4">
                    Data Engineering <span class="text-cyan-400">Weekly News</span>
                </h1>
                <div class="flex flex-col md:flex-row justify-between items-center gap-4">
                    <p class="text-slate-500 font-semibold uppercase tracking-widest text-[10px]">
                        Architectural Insights by Data With Dhana
                    </p>
                    <p class="text-cyan-500 font-mono text-sm bg-cyan-500/5 px-4 py-1 rounded-full border border-cyan-500/20">
                        {datetime.date.today().strftime('%d %B %Y')}
                    </p>
                </div>
            </header>

            <main>
                {ai_content}
            </main>

            <footer class="mt-32 text-center py-10 border-t border-slate-900">
                <p class="text-slate-600 text-[9px] tracking-[0.5em] uppercase">
                    &copy; {datetime.datetime.now().year} Data With Dhana • Curated by AI
                </p>
            </footer>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    news = fetch_weekly_news()
    if news:
        html_cards = generate_html_content(news)
        save_as_html_file(html_cards)
        print("Success: 10 Box-Tiles Generated.")
