import jsonapi_requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session, OAuth2
from django.conf import settings

client_id = settings.CLIENT_ID
client_secret = settings.CLIENT_SECRET

client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(token_url='https://www.fimfiction.net/api/v2/token', client_id=client_id, client_secret=client_secret)
auth = OAuth2(client_id=client_id, client=client, token=token)

api = jsonapi_requests.Api.config({
    'API_ROOT': 'https://www.fimfiction.net/api/v2/',
    'APPEND_SLASH': False,
    'AUTH': auth,
})

def getBooks(sort='date_modified', cursor=None):

    q = "?"
    q += 'fields[story]=title,cover_image,date_published,short_description,description_html,author,date_modified,cover_image,tags'
    q += '&fields[story_tag]=name'
    q += '&fields[user]=name'
    q += '&page[size]=100'
    q += '&sort='+sort
    stories_endpoint = api.endpoint('stories' + q)
    api_response = stories_endpoint.get()
    return api_response

