#!/usr/bin/env python3
"""Run the Flask app with a small CLI helper.

Usage examples:
  source .venv/bin/activate
  python3 run_server.py --port 5002

Options:
  --host    Host to bind (default 0.0.0.0)
  --port    Port to listen on (default 5002)
  --debug   Run Flask in debug mode (default False)
"""

import argparse
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', default='0.0.0.0', help='Host to bind')
    p.add_argument('--port', type=int, default=5002, help='Port to listen on')
    p.add_argument('--debug', action='store_true', help='Enable Flask debug mode')
    args = p.parse_args()

    # Import app lazily so environment can be prepared first
    try:
        from app import app
    except Exception as e:
        print('Failed to import Flask app (are you in the project dir and venv active?):', e)
        sys.exit(1)

    print(f'Starting server on http://{args.host}:{args.port} (debug={args.debug})')
    app.run(host=args.host, port=args.port, threaded=True, debug=args.debug)


if __name__ == '__main__':
    main()
