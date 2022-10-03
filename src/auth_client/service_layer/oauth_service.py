import abc
import aiohttp

class AbstractOAuthService(abc.ABC):
    def __init__(self, service_url):
        self.service_url = service_url

    def post(self, endpoint, data):
        return self._post(endpoint, data)

    @abc.abstractmethod
    def _post(self, *args):
        raise NotImplementedError()

    @property
    def url(self):
        return self._url
    
    @property
    def _params(self):
        return self.params

class OAuthService(AbstractOAuthService):
    async def _post(self, endpoint, data):
        async with aiohttp.ClientSession() as session:
            self._url = f"{self.service_url}{endpoint}"
            response = session.post(
                url=self._url,
                data=data
            )
            return response
    
