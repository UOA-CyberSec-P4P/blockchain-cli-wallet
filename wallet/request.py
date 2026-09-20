import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

def get(path: str, base_url: str) -> dict:
    return _request('GET', path, base_url)

def post(path: str, payload: dict, base_url: str) -> dict:
    return _request('POST', path, base_url, payload=payload)

def _request(
    method: str,
    path: str,
    base_url: str,
    payload: dict | None = None,
) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(
        f'{base_url}{path}',
        data=data,
        method=method,
        headers={'Content-Type': 'application/json'} if data is not None else {},
    )
    try:
        with urlopen(request) as response:
            return json.loads(response.read())
    except HTTPError as error:
        body = error.read().decode()
        try:
            message = json.loads(body).get('error', body)
        except json.JSONDecodeError:
            message = body
        raise RuntimeError(f'HTTP {error.code}: {message}') from error
    except URLError as error:
        raise RuntimeError(f'cannot reach blockchain service: {error.reason}') from error