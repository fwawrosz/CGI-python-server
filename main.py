from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from tweepy import API, Cursor, OAuthHandler, Stream
from tweepy.streaming import StreamListener
import tweepy
import json

access_token = "1713619092-rNn56braFDEwRLyAGh9IbWZ8BlqaHqEhYtIx5em"
access_token_secret = "pt3Kevia17SPtO2x7BgrVryi57i4S7snP2fciBKrtxxXa"
consumer_key = "YAPz4IkJ57pW1ODjdgJ1htuob"
consumer_secret = "1M4v1J90uONGrH092pDDbx1wSMjgPX194ZkKJ6TZm7PSXHHg8W"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
tweet_api = tweepy.API(auth, wait_on_rate_limit=True)

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class VideoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Video(name = {name}, views = {views}, likes = {likes})"


find_tweets_args = reqparse.RequestParser()
find_tweets_args.add_argument("subject", type=str, help="Subject for the search is required", required=True)
#find_tweets_args.add_argument("startDate", type=str, help="Start date for search is required", required=True)
number_of_tweets_to_find = 2

places = tweet_api.geo_search(query="Canada", granularity="country")
place_id = places[0].id


resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'views': fields.Integer,
    'likes': fields.Integer
}

tweetsDic = {}

class TweitterScrapper(Resource):
    
    def get(self):
        args = find_tweets_args.parse_args()

        # Creation of query method using parameters
        tweets = tweepy.Cursor(tweet_api.search,q=args['subject'],geocode="45.501689,-73.567256,300km").items(number_of_tweets_to_find)
 
        # Pulling information from tweets iterable object
        tweets_list = [[tweet.id, tweet.text, tweet.user.location, tweet.user.screen_name] for tweet in tweets]
        print(tweets_list)
        return json.dumps(tweets_list)
                


        

   

api.add_resource(TweitterScrapper, "/twittersearch/")



if __name__ == "__main__":
    app.run(debug=True)