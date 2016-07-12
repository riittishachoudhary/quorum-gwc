import requests


class QuorumAPI(object):
    """
    An overall wrapper for Quorum's API that enables chainable
    filters and abstracts away the actual HTTP requests to the API.

    Typical usage:
    1. initialize a QuorumAPI object, passing in the username and API key
    2. set the endpoint of this particular QuorumAPI object (optionally can be specified at initialization)
    3. create a set of filters and set the settings on a given API object
    4. run GET to return relevant results

    Example:
    quorum_api = QuorumAPI(username="gwc", api_key="691e43c415d88cd16286edb1f78abb2e348688da")
    quorum_api = quorum_api.set_endpoint("person") \
                    .count(True) \
                    .limit(100) \
                    .offset(20) \
                    .filter(role_type = RoleType.senator, current=True)

    results = quorum_api.GET()
    next_results = quorum_api.NEXT()

    """

    # API constants
    SUPPORTED_ENDPOINTS = ["person",
                           "bill",
                           "vote",
                           "district",
                           "state",
                           "document",
                           "legsession"]
    BASE_URL = "https://www.quorum.us"

    def __init__(self, username, api_key, endpoint=None):

        self.username = username
        self.api_key = api_key
        self.filters = {
                        "decode_enums": True
                       }

        # internal globals with defaults
        self._limit = 20
        self._offset = 0
        self._count = True

        if endpoint:
            self.set_endpoint(endpoint)

    def set_endpoint(self, endpoint):

        if endpoint in self.SUPPORTED_ENDPOINTS:
            self.endpoint = endpoint
        else:
            raise Exception('Unsupported Endpoint')

        return self

    def count(self, return_count=True):
        if return_count in [True, False]:
            self._count = return_count
        else:
            raise Exception('Must be a boolean value.')

        return self

    def limit(self, value=20):
        if isinstance(value, int):
            self._limit = value
        else:
            raise Exception('Must be a numeric value.')

        return self

    def offset(self, value=0):
        if isinstance(value, int):
            self._offset = value
        else:
            raise Exception('Must be a numeric value.')

        return self

    def filter(self, **kwargs):
        for key, value in kwargs.iteritems():
            self.filters[key] = value

        return self

    def process_request(self, request):
        if isinstance(request, dict) and request.get("meta"):
            self.next_url = request["meta"]["next"]
            self.previous_url = request["meta"]["previous"]

    def NEXT(self):
        if hasattr(self, "next_url") and self.next_url:
            self._offset += self._limit
            next_request = requests.get(self.BASE_URL + self.next_url).json()
            self.process_request(next_request)

            return next_request
        else:
            raise Exception("End of results.")

    def PREVIOUS(self):
        if hasattr(self, "previous_url") and self.previous_url:
            self._offset -= self._limit
            next_request = requests.get(self.BASE_URL + self.previous_url).json()
            self.process_request(next_request)

            return next_request
        else:
            raise Exception("Beginning of results.")

    def GET(self):
        """
        The final step in calling the API -- actually
        go out and make the request. Returns a dictionary
        of results.
        """

        # set all the global vals as filters
        for attr in ["_count", "_limit", "_offset", "username", "api_key"]:

            if attr.startswith("_"):
                key = attr[1:]
            else:
                key = attr

            self.filters[key] = getattr(self, attr)

        # convert all the boolean values (True and False) to strings
        for key, value in self.filters.iteritems():
            if value in [True, False] and isinstance(value, bool):
                if value:
                    self.filters[key] = "true"
                else:
                    self.filters[key] = "false"

            # convert all list-like things to comma separated lists
            if isinstance(value, list) or isinstance(value, tuple):
                self.filters[key] = ",".join([str(val) for val in value])

        print (self.filters)

        initial_request = requests.get(self.BASE_URL + "/api/%s/" % self.endpoint,
                                       params = self.filters)
                                  
        print (initial_request.url)

        initial_request = initial_request.json()

        self.process_request(initial_request)

        return initial_request
