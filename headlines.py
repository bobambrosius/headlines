import datetime
import feedparser
from flask import Flask, make_response, render_template, request, send_from_directory
#from idlelib import query
import json
import os
import ssl
import urllib

app = Flask(__name__)

RSS_FEEDS = {
            'telegraaf': "https://www.telegraaf.nl/nieuws/rss",
            'trouw': "https://www.trouw.nl/home/rss.xml",
            'bbc': "http://feeds.bbci.co.uk/news/rss.xml",
            'cnn': "http://rss.cnn.com/rss/edition.rss",
            'fox': "http://feeds.foxnews.com/foxnews/latest",
            'iol': "http://rss.iol.io/iol/news"}
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=cb932829eacb6a0e9ee4f38bfbf112ed"
CURRENCY_URL = "https://openexchangerates.org/api/latest.json?app_id=569c97195620452ca49e87b02ba8d7da"
DEFAULTS = {'publication':'trouw',
            'city':'Enschede,NL',
            'currency_from': 'EUR',
            'currency_to': 'USD'}

def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

def get_rate(crncy_from, crncy_to):
    all_currency = urllib.request.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(crncy_from.upper())
    to_rate = parsed.get(crncy_to.upper())
    return to_rate/frm_rate, parsed.keys()
    
def get_weather(query):
    query = urllib.parse.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {
            "description":parsed["weather"][0]["description"], 
            "temperature":parsed["main"]["temp"], 
            "city":parsed["name"],
            "country": parsed["sys"]["country"]
        }
    return weather

def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]

@app.route("/")
def home():
    # Voorkom de fout [SSL: CERTIFICATE_VERIFY_FAILED]
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # headlines
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)

    # Weather
    city = get_value_with_fallback('city')
    weather = get_weather(city)
    
    # Currency
    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')
    rate, currencies = get_rate(currency_from, currency_to)
    
    # result
    response = make_response(render_template(
            "home.html",
            publication = publication,
            articles = articles,
            weather = weather,
            currency_from = currency_from,
            currency_to = currency_to,
            rate = rate, 
            currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)    
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response
        
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__=="__main__":
    app.run(port=4141, debug=True)
