import json
from http import HTTPStatus

from httpx import AsyncClient

__all__ = ('HTTPError', 'RestSession')


class HTTPError(Exception):
    def __init__(self, msg, response):
        super().__init__(msg)
        self.response = response


class RestSession(AsyncClient):
    def __init__(self, client, *args, **kwargs):
        self.loop = client.loop
        self.client = client

        self.authorization = self.client.token
        self.api_version = self.client.api_version

        self.global_headers = kwargs.pop('global_headers', {})
        self.global_headers.update({
            'Authorization': self.authorization,
        })

        kwargs['timeout'] = None
        super().__init__(*args, **kwargs)

    async def request(self, method, url, fmt, *args, **kwargs):
        url = url % fmt
        response = await super().request(method, url, *args, **kwargs)
        await response.aclose()

        data = response.content

        content_type = response.headers.get('content-type')
        if (content_type is not None
                and content_type.lower() == 'application/json'):
            data = json.loads(data)

        status_code = response.status_code
        if status_code >= 400:
            status = HTTPStatus(status_code)
            raise HTTPError(
                f'{method} {url} responded with {status} {status.phrase}: '
                f'{data}', response)

        return data