#Import the necessary methods from tweepy library
import os
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

#Variables that contains the user credentials to access Twitter API 
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
REGION = 'us-east-1'
AWS_ELASTICSEARCH_HOST = os.environ.get("AWS_ELASTICSEARCH_HOST")
AWSAUTH = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION, 'es')

es = Elasticsearch(
    hosts=[{'host': AWS_ELASTICSEARCH_HOST, 'port': 443}],
    http_auth=AWSAUTH,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

class ElasticSearchStreamListener(StreamListener):
  'This class is a stream-listener that redirects the stream to be stored in ElasticSearch'
  def on_data(self, data):
    try:
      if data.find('"geo":') != -1 & data.find('"geo":null') == -1:
        # Parse json
        jsondata = json.loads(data)
        print(jsondata['geo'])

        # Build own dictionary with subset of the data
        d = {}
        d['text'] = jsondata['text']
        d['name'] = jsondata['user']['name']
        d['created_at'] = jsondata['created_at']
        lat_degdec = jsondata['geo']['coordinates'][0]
        lon_degdec = jsondata['geo']['coordinates'][1]
        coordict = {}
        coordict['lat'] = float(lat_degdec)
        coordict['lon'] = float(lon_degdec)
        d['location'] = coordict

        # Encode as json
        processed = json.dumps(d)

        # Send to back-end for storage
        es.index(index="tweets", doc_type='tweet', body=processed)
    except KeyboardInterrupt:
        print("Interrupted by Ctrl-C.")
        raise KeyboardInterrupt
    return True

def on_error(self, status):
  print ("Reached on_error() for ElasticSearchStreamListener.")
  print ("status: ", status)

if __name__ == '__main__':
  #This handles Twitter authetification and the connection to Twitter Streaming API
  #es.indices.delete(index='tweets')
  # mapping = '''
  # {
  #   "mappings" : {
  #     "tweet" : {
  #       "properties" : {
  #         "text" : {"type" : "string"},
  #         "name" : {"type" : "string"},
  #         "created_at" : {"type" : "string"},
  #         "location" : {"type" : "geo_point"}
  #       }
  #     }
  #   }
  # }'''
  # es.indices.create(index='tweets', ignore=400, body=mapping)
  l = ElasticSearchStreamListener()
  auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
  stream = Stream(auth, l)

  i = 0
  keepGoing = True
  while keepGoing:
    try:
      i = i + 1
      print ('Streaming... ' + str(i))
      # Get tweets from every corner of the world
      stream.filter(locations=[-180,-90,180,90])
      #stream.sample()
    except KeyboardInterrupt:
      #print ('Interrupted by Ctrl-C.')
      keepGoing = False
    except Exception as e:
      print ('Caught exception...')
      print ( e )
      continue