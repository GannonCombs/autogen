# python

from googleapiclient.discovery import build

# you need to provide your own Google API credentials
api_key = "<your-API-key>"
cse_id = "<your-custom-search-engine-id>"

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res

# query for APIs with transaction capabilities
results = google_search("APIs that allow transactions and purchases with credit card or crypto", api_key, cse_id)

# print the urls
for result in results["items"]:
    print(result["link"])