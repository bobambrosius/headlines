import os
import feedparser
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

RSS_FEEDS = {'bbc': "http://feeds.bbci.co.uk/news/rss.xml",
             'cnn': "http://rss.cnn.com/rss/edition.rss",
             'fox': "http://feeds.foxnews.com/foxnews/latest",
             'iol': "http://rss.iol.io/iol/news"}

@app.route("/")
@app.route("/<publication>")
def get_news(publication='bbc'):
    feed = feedparser.parse(RSS_FEEDS[publication])
    first_article = feed['entries'][0]
    return render_template("home.html", articles=feed['entries'])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__=="__main__":
    app.run(port=4141, debug=True)
