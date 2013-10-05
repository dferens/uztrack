import requests
from urlparse import urljoin


HOST_URL = 'http://booking.uz.gov.ua/'


class APIException(Exception):
    pass


class UzGovUaAPIException(Exception):
    def __init__(self, url, message):
        message = '(%s): %s' % (url, message)
        super(UzGovUaAPIException, self).__init__(message)



def get_station_id(station_name):
    url = urljoin(HOST_URL, 'purchase/station/')
    url = urljoin(url, station_name)
    
    try:
        response = requests.post(url)
    except requests.ConnectionError:
        raise APIException('Host is down: %s' % HOST_URL)
    
    content_type = response.headers['content-type']
    if not content_type.startswith('application/json'):
        raise APIException('Host returned "%s", expected "application/json"' % content_type)
    
    json_data = response.json()
    if json_data['error']:
        raise UzGovUaAPIException('Error occured: %s' % json_data['error'])
    
    results = json_data['value']
    if len(results) == 0:
        return None
    else:
        for result_item in results:
            station_id, title = result_item['station_id'], result_item['title']

            if title == station_name:
                # Exact match
                return station_id
        else:
            # Closest match
            return results[0]['station_id']