from flask import Flask, render_template
from tweet_helper import TwitterHelper

application = Flask(__name__)

@application.route("/")
def index():
  response = TwitterHelper.searchTweets(None, None)
  return render_template("map.html", map_input = response, title = "Map")

@application.route("/keyword.json/<keyword>")
def keyword_search(keyword):
  return TwitterHelper.searchTweets(keyword, None)

@application.route("/location.json")
def location_search(location):
  return TwitterHelper.searchTweets(None, location)

if __name__ == "__main__":
  application.run()