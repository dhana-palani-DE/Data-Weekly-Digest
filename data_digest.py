import feedparser
import os
import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 1. INDUSTRY FEEDS & BRAND COLORS
# Mapping brand colors for the AI to use
BRAND_COLORS = {
    "dbt": "#FF694B",
    "Databricks": "#FF3621",
    "Snowflake": "#29B5E8",
    "Airbyte": "#6132FF",
    "Google Cloud": "#4285F4",
    "AWS": "#FF9900",
    "Microsoft Fabric": "#00A4EF",
    "Confluent": "#EA2B91",
    "DuckDB": "#FFF000",
    "Dagster": "#4F43E8",
    "StarRocks": "#3D3DFF",
    "Pinecone": "#22C55E"
}

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
    print("Selecting top articles and mapping brand colors...")
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]: 
                date_tuple = entry.get('published_parsed') or entry.get('updated_parsed')
                if date_tuple:
                    pub_date = datetime.datetime(*date_tuple[:6], tzinfo=datetime.timezone.utc)
                    if (now - pub_date).days <= 10: 
                        # Attach the hex color to the input text
                        color = BRAND_COLORS.get(source, "#22d3ee")
                        digest_input.append(f"COMPANY: {source} | COLOR: {color} | TITLE: {entry.title} | LINK: {entry.link}")
        except: continue
    return "\n".join(digest_input)

def generate_html_content(news_text):
    prompt = f"""
    You are a Lead Data Architect. Select the TOP 10 most impactful articles.
    
    Output a RESPONSIVE GRID of 10 Box-style Cards.
    
    STYLE RULES:
    - GRID: Use <div class="grid grid-cols-1 md:grid-cols-2 gap-8">.
    - CARD BASE: Background #0f172a, Border 1px #1e293b, Rounded-xl.
    - BRANDING: Each card MUST have a 4px TOP-BORDER using the provided COMPANY COLOR.
    
    FOR EACH CARD (Top 10 Only):
    1. Apply the COMPANY COLOR hex to the top border.
    2. Company Badge: Use the COLOR for the text, uppercase, bold.
    3. Title: White text, font-bold, text-xl.
    4. Strategic Impact: 2 sentences max in slate-400 text.
    5. 'Read More' Link: Styled with the brand color.
    
    NEWS DATA:
    {news_text}
    """
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "Return ONLY raw HTML tags. Do not use markdown backticks or ```html blocks."},
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
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                height: 100%;
            }}
            .news-card:hover {{
                transform: translateY(-5px);
                background: #111827;
                box-shadow: 0 15px 30px -10px rgba(0,0,0,0.5);
            }}
        </style>
    </head>
    <body class="p-6 md:p-16 lg:p-24">
        <div class="max-w-6xl mx-auto">
            <header class="mb-20 text-center md:text-left border-b border-slate-800 pb-12">
                <h1 class="text-4xl md:text-6xl font-extrabold text-white tracking-tighter mb-4 leading-none">
                    Data Engineering <span class="text-cyan-400">Weekly News</span>
                </h1>
                <div class="flex flex-col md:flex-row justify-between items-center gap-4">
                    <p class="text-slate-500 font-semibold uppercase tracking-[0.3em] text-[10px]">
                        Architectural Insights by Data With Dhana
                    </p>
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                        <p class="text-cyan-500 font-mono text-sm tracking-widest uppercase">
                            {datetime.date.today().strftime('%d %B %Y')}
                        </p>
                    </div>
                </div>
            </header>

            <main>
                {ai_content}
            </main>

            <footer class="mt-40 text-center py-10 border-t border-slate-900 opacity-40">
                <p class="text-slate-600 text-[10px] tracking-[0.8em] uppercase">
                    &copy; {datetime.datetime.now().year} Data With Dhana • Professional Digest
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
        print("Success: Generated color-coded box tiles.")
