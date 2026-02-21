from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from qticket.eval.runner import run_experiment


class Handler(BaseHTTPRequestHandler):
    role = 'node'

    def do_GET(self):
        if self.path == '/health':
            body = json.dumps({'ok': True, 'role': self.role}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(prog='qticket')
    sub = parser.add_subparsers(dest='cmd', required=True)

    n = sub.add_parser('run-node')
    n.add_argument('--role', choices=['anchor', 'ag', 'tg'], required=True)
    n.add_argument('--id', default='')
    n.add_argument('--host', default='0.0.0.0')
    n.add_argument('--port', type=int, default=8000)

    e = sub.add_parser('run-exp')
    e.add_argument('--exp', required=True)
    e.add_argument('--scheme')
    e.add_argument('--schemes', nargs='+')

    args = parser.parse_args()
    if args.cmd == 'run-node':
        Handler.role = args.role if not args.id else f"{args.role}:{args.id}"
        server = HTTPServer((args.host, args.port), Handler)
        print(f"{Handler.role} listening at http://{args.host}:{args.port}")
        server.serve_forever()
        return

    schemes = args.schemes or ([] if not args.scheme else [args.scheme])
    if not schemes:
        raise SystemExit('must provide --scheme or --schemes')
    repo_root = Path(__file__).resolve().parents[2]
    out = run_experiment(args.exp, schemes, repo_root)
    for s, p in out.items():
        print(f'[{s}] outputs at {p}')


if __name__ == '__main__':
    main()
