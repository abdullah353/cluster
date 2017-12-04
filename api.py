import logging
from flask import Flask, g, _app_ctx_stack
from flask import jsonify
import argparse
import json
import pickle

app = Flask(__name__)


@app.route("/cluster", methods=['GET'])
def expose_cluster_stat():
    return json.dumps(pickle.load(open("index.p", "rb"))), 200, {
        'Content-Type': 'application/json; charset=utf-8'}


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description='Expose K-Mean cluster')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Adjust the host of the server.')
    parser.add_argument('--port', type=int, default=80,
                        help='Adjust the port of the server.')
    parser.add_argument('--debug', type=bool, default=False,
                        help='Enable app debugging.')

    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)
