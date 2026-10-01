#!/usr/bin/env python3
"""Shared Snipe-IT API transport; workflows belong in skills."""

import argparse
import json
import math
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def configuration():
    values = {}
    env_file = ROOT / '.env'
    if env_file.is_file():
        for line in env_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, sep, value = line.removeprefix('export ').partition('=')
            key = key.strip()
            if sep and key in ('SNIPE_IT_URL', 'SNIPE_IT_TOKEN'):
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                values[key] = value
    return {key: os.environ.get(key, values.get(key, '')).strip()
            for key in ('SNIPE_IT_URL', 'SNIPE_IT_TOKEN')}


def request_url(base, endpoint, params):
    parts = urlsplit(base)
    if (not parts.hostname or parts.username is not None or parts.password is not None
            or parts.query or parts.fragment):
        raise ValueError('SNIPE_IT_URL must be an instance URL without credentials or query parameters.')
    if parts.scheme != 'https' and not (
            parts.scheme == 'http' and parts.hostname in ('localhost', '127.0.0.1', '::1')):
        raise ValueError('HTTPS is required; HTTP is allowed only on localhost.')
    # Reject encoded separators and path traversal before attaching the token.
    if not re.fullmatch(r'/?[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*/?', endpoint):
        raise ValueError('Endpoint must be an API path, e.g. hardware/123, without a URL or query string.')
    path = parts.path.rstrip('/')
    if path.endswith('/api/v1'):
        raise ValueError('Set SNIPE_IT_URL without /api/v1.')
    query = []
    for item in params:
        key, sep, value = item.partition('=')
        if not sep or not key:
            raise ValueError('--param requires KEY=VALUE.')
        query.append((key, value))
    return urlunsplit((parts.scheme, parts.netloc,
                       path + '/api/v1/' + endpoint.strip('/'), urlencode(query), ''))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('method', type=str.upper, choices=('GET', 'POST', 'PUT', 'PATCH', 'DELETE'))
    parser.add_argument('endpoint', help='Path relative to /api/v1, e.g. hardware')
    parser.add_argument('--param', action='append', default=[], metavar='KEY=VALUE')
    parser.add_argument('--data', help='JSON or @path to a JSON file')
    parser.add_argument('--apply', action='store_true', help='Execute a write instead of printing a plan')
    parser.add_argument('--timeout', type=float, default=30, help='Timeout in seconds (default: 30)')
    args = parser.parse_args()
    token = ''
    try:
        config = configuration()
        token = config['SNIPE_IT_TOKEN']
        if not config['SNIPE_IT_URL'] or not token:
            raise ValueError('Set SNIPE_IT_URL and SNIPE_IT_TOKEN in the environment or local .env.')
        if not math.isfinite(args.timeout) or args.timeout <= 0:
            raise ValueError('--timeout must be a positive finite number.')
        url = request_url(config['SNIPE_IT_URL'], args.endpoint, args.param)
        payload = None
        if args.data is not None:
            if args.method == 'GET':
                raise ValueError('GET accepts --param, not --data.')
            raw = (Path(args.data[1:]).read_text(encoding='utf-8')
                   if args.data.startswith('@') else args.data)
            payload = json.loads(raw)
        if args.method != 'GET' and not args.apply:
            result = {'mode': 'plan', 'method': args.method, 'url': url, 'data': payload}
        else:
            body = None if args.data is None else json.dumps(payload).encode('utf-8')
            req = Request(url, data=body, method=args.method,
                          headers={'Authorization': 'Bearer ' + token,
                                   'Accept': 'application/json', 'Content-Type': 'application/json'})
            try:
                with build_opener(NoRedirect()).open(req, timeout=args.timeout) as response:
                    raw = response.read()
            except HTTPError as exc:
                # Do not print server error bodies: they may contain headers or secrets.
                raise ValueError(f'HTTP {exc.code}; check access, endpoint and payload.') from None
            result = json.loads(raw)
            if isinstance(result, dict) and result.get('status') == 'error':
                details = json.dumps(result.get('messages', 'No details'), ensure_ascii=False)
                raise ValueError('API error: ' + details)
        output = json.dumps(result, ensure_ascii=False, indent=2)
        print(output.replace(token, '[REDACTED]'))
        return 0
    except (OSError, ValueError, URLError) as exc:
        message = str(exc)
        if token:
            message = message.replace(token, '[REDACTED]')
        print('Error: ' + message, file=sys.stderr)
        if args.method != 'GET' and args.apply:
            print('Do not retry a write before checking its outcome in Snipe-IT.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
