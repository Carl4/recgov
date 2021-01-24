from os import environ
from requests import Session
from fake_useragent import UserAgent

class SessionPaginator(Session):

    def get_record_iterator(self, *args, params=None, **kwargs):

        params = params or {}
        total_count=None
        current_count = 0
        while not (current_count == total_count):
            params.update({"limit": 50, "offset": current_count})
            resp = self.get(*args, params=params, **kwargs).json()
            for rec in resp['RECDATA']:
                yield rec 
            current_count += resp['METADATA']['RESULTS']['CURRENT_COUNT']
            total_count = resp['METADATA']['RESULTS']['TOTAL_COUNT']
            if current_count > total_count:
                raise ValueError("Total records was supposed to be {total_count},"
                                 "but we somehow read {current_count}!")

def get_session(apikey:str=None)->SessionPaginator:
    """Gets a session with an apikey set in the headers.

    apikey can be provided either as an input parameter or read from the 
    environment variable "RECREATION_GOV_KEY"

    :param apikey: The API Key (from ridb.recreation.gov)., defaults to None
    :type apikey: str, optional
    :raises RuntimeError: If you don't provide an apikey as described above.
    :return: a requests Session that's authenticated.
    :rtype: requests.Session
    """
    if apikey is None and "RECREATION_GOV_KEY" in environ:
        apikey = environ.get("RECREATION_GOV_KEY")
    if apikey is None:
        raise RuntimeError("apikey must be provided to get_requests either" 
                           "as an input parameter or as an environment "
                           "variable ('RECREATION_GOV_KEY')")
    headers = {"apikey": apikey}        
    sess = SessionPaginator()
    sess.headers.update(headers)
    return sess

def get_anonymous_session():
    HEADERS = {'User-Agent': UserAgent().random}
    sess = Session()
    sess.headers.update(HEADERS)
    return sess 