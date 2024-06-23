import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from textblob import TextBlob

# List of RSS feed URLs
#rss_feeds = ['https://news.google.com/news/rss/headlines/section/geo/india?hl=en-IN&gl=IN&ceid=IN%3Aen']

rss_feeds = [
'https://news.ycombinator.com/rss',
'http://qz.com/feed/',
'http://feeds.feedburner.com/TheAtlantic',
'http://www.inc.com/rss/homepage.xml',
'https://nautil.us/feed/',
'https://aeon.co/feed.rss',
'http://www.newyorker.com/services/mrss/feeds/everything.xml',
'http://www.datasociety.net/feed/',
'http://www.npr.org/rss/rss.php?id=1007',
'http://feeds.arstechnica.com/arstechnica/everything',
'https://restofworld.org/feed/',
'http://daily.jstor.org/feed/',
'http://www.quantamagazine.org/feed/',
'http://feeds.harvardbusiness.org/harvardbusiness/',
'http://atlasobscura.com/rss.xml',
'http://theconversation.com/au/home-page/articles.atom',
'http://bigthink.com/feeds/main.rss',
'http://longreads.com/rss'
]

# Email credentials
email_address = ''
email_password = ''
smtp_server = 'smtp.gmail.com'
smtp_port = 587
to_email_address = ['']

# List of political keywords
political_keywords = [
    'election', 'government', 'politics', 'president', 'prime minister', 
    'senate', 'congress', 'parliament', 'policy', 'politician', 'campaign'
]

def is_political_article(title, summary):
    content = f"{title} {summary}".lower()
    for keyword in political_keywords:
        if keyword in content:
            return True
    return False

def fetch_rss_feeds(feed_urls):
    articles = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if not is_political_article(entry.title, entry.summary):
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.summary
                })
    return articles

def analyze_title_sentiment(title):
    analysis = TextBlob(title)
    return analysis.sentiment.polarity

def calculate_score(article):
    # Sentiment analysis score
    sentiment_score = analyze_title_sentiment(article['title'])
    # Length of summary score (assuming longer summaries might be more comprehensive)
    length_score = len(article['summary'])
    # You can add more criteria and their respective weights here

    # Total score (weights can be adjusted)
    total_score = (sentiment_score * 0.5) + (length_score * 0.5)
    return total_score

def rank_articles(articles, top_n=5):
    # Calculate score for each article
    for article in articles:
        article['score'] = calculate_score(article)
    
    # Sort articles by score in descending order
    sorted_articles = sorted(articles, key=lambda x: x['score'], reverse=True)
    return sorted_articles[:top_n]

def send_email(subject, body, to_email):
    msg = MIMEMultipart()
    msg['From'] = "Automated News Service"
    msg['To'] = ', '.join(to_email)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_address, email_password)
        server.sendmail(email_address, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except smtplib.SMTPAuthenticationError as e:
        print(f"Failed to send email: {e.smtp_code}, {e.smtp_error}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    articles = fetch_rss_feeds(rss_feeds)
    top_articles = rank_articles(articles)
    
    email_body = '''
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
                padding: 20px;
            }
            .container {
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: 0 auto;
            }
            h1 {
                color: #0056b3;
            }
            .article {
                margin-bottom: 20px;
            }
            .article h2 {
                margin: 0 0 10px;
            }
            .article a {
                color: #0056b3;
                text-decoration: none;
            }
            .article a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Top 5 News Articles For Today</h1>
            <p class="intro">This email contains links to the top 5 news articles from various sources.</p>
    '''

    for article in top_articles:
        email_body += f'''
            <div class="article">
                <h2><a href="{article['link']}">{article['title']}</a></h2>
            </div>
        '''

    email_body += '''
            <p class="quote">""</p>
        </div>
    </body>
    </html>
    '''

    send_email('Top 5 News Articles for Today', email_body, to_email_address)

if __name__ == "__main__":
    main()
