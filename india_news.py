import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# List of RSS feed URLs
rss_feeds = ['https://news.google.com/news/rss/headlines/section/geo/india?hl=en-IN&gl=IN&ceid=IN%3Aen']
#rss_feeds =['https://news.google.com/news/rss?hl=en-IN&gl=IN&ceid=IN:en&hl=en-IN']
#rss_feeds2 = [
#'http://timesofindia.indiatimes.com/rssfeedmostread.cms'
#'https://thewire.in/rss',
#'http://www.newslaundry.com/feed/',
#'http://www.thehindu.com/news/national/?service=rss',
#'http://feeds.reuters.com/reuters/topNews?irpc=69',
#'http://www.rte.ie/rss/news.xml',
#'http://www.guardian.co.uk/rssfeed/0,,1,00.xml',
#'http://feeds.wired.com/wired/index',
#'http://rss.dw-world.de/rdf/rss-en-all',
#'http://www.independent.ie/rss',
#'http://feeds.gawker.com/gizmodo/full',
#'http://www.theverge.com/rss/full.xml',
#'https://news.ycombinator.com/rss',
#'http://qz.com/feed/',
#'http://feeds.feedburner.com/TheAtlantic',
#'http://www.inc.com/rss/homepage.xml',
#'https://nautil.us/feed/',
#'https://aeon.co/feed.rss',
#'http://www.newyorker.com/services/mrss/feeds/everything.xml',
#'http://www.datasociety.net/feed/',
#'http://www.npr.org/rss/rss.php?id=1007',
#'http://feeds.arstechnica.com/arstechnica/everything',
#'https://restofworld.org/feed/',
#'http://daily.jstor.org/feed/',
#'http://www.quantamagazine.org/feed/',
#'http://feeds.harvardbusiness.org/harvardbusiness/',
#'http://atlasobscura.com/rss.xml',
#'http://theconversation.com/au/home-page/articles.atom',
#'http://bigthink.com/feeds/main.rss',
#'http://longreads.com/rss'
#]


# Email credentials
email_address = ''
email_password = ''
smtp_server = 'smtp.gmail.com'
smtp_port = 587
to_email_address = [
]


def fetch_top_articles(rss_urls, top_n=20):
    articles = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:top_n]:
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'summary': entry.summary
            })
    articles.sort(key=lambda x: x['title'])  # Sorting articles by title for consistency
    return articles[:top_n]

def send_email(subject, body, to_email):
    msg = MIMEMultipart()
    msg['From'] = f"Automated News Service"
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


#def main():
#    articles = fetch_top_articles(rss_feeds)
#    email_body = '<h1>Top Articles</h1>'
#    for article in articles:
#        email_body += f"<h2><a href='{article['link']}'>{article['title']}</a></h2>"
#        email_body += f"<p>{article['summary']}</p>"

#    send_email('Top 10 Articles from Your RSS Feeds', email_body, to_email_address)




def main():
    articles = fetch_top_articles(rss_feeds)
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
            .article p {
                margin: 0;
                color: #555;
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
            <h1>News Headlines For Today</h1>
            <p class="intro">This email contains news articles from various sources to help avoid bias. Each news article includes up to 5 different sources.</p>
    '''

    for article in articles:
        email_body += f'''
            <div class="article">
                <h2><a href="{article['link']}">{article['title']}</a></h2>
                <p>{article['summary']}</p>
            </div>
        '''

    email_body += '''
            <p class="quote">"Anything that you want to put here"</p>
        </div>
    </body>
    </html>
    '''

    send_email('News headlines for today', email_body, to_email_address)


if __name__ == "__main__":
    main()
