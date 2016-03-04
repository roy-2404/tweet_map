import os
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch_dsl import Search, Q
from requests_aws4auth import AWS4Auth
import json

class TwitterHelper:
  AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
  AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
  REGION = 'us-east-1'
  AWS_ELASTICSEARCH_HOST = os.environ.get("AWS_ELASTICSEARCH_HOST")
  AWSAUTH = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, REGION, 'es')

  ES = Elasticsearch(
    hosts=[{'host': AWS_ELASTICSEARCH_HOST, 'port': 443}],
    http_auth=AWSAUTH,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
  )

  @staticmethod
  def searchTweets(keyword, latlondist):
    #Variables that contains the user credentials to access Twitter API 
    if TwitterHelper.AWS_ACCESS_KEY == None:
      raise KeyError("Please, set the AWS_ACCESS_KEY env. variable")
    
    if TwitterHelper.AWS_SECRET_KEY == None:
      raise KeyError("Please, set the AWS_SECRET_KEY env. variable")

    s = Search(using=TwitterHelper.ES, index="tweets")

    if latlondist != None:
      q = Q('bool',
        must=[Q('match_all')],
        filter= {'geo_distance' : {'distance': latlondist['distance'], 'location': {'lat':latlondist['lat'],'lon':latlondist['lon']}}}
      )
      s = s.query(q)
    
    if keyword != None:
      q = Q("match_phrase", text=keyword)
      s = s.query(q)
      #s = s.filter('text', tags=[keyword])

    s = s.params(size=99999999)
    response = s.execute()
    arr = []
    for hit in response:
      d = {}
      d['name'] = hit.name
      d['text'] = hit.text
      d['lat'] = hit.location.lat
      d['lon'] = hit.location.lon
      arr.append(d)

    allD = {}
    allD['tweets'] = arr
    mapInput = json.dumps(allD)
    return mapInput