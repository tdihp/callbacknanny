#!/usr/bin/env python

import logging
import subprocess
import os
import re

from flask import Flask, request, abort, jsonify
import pystache


logger = logging.getLogger('callbacknanny')
app = application = Flask(__name__)


app.config.from_pyfile('callbacknanny.cfg', silent=True)
# get all config from env
app.config.update((k, v) for k, v in os.environ.items() if k.startswith('NANNY_'))

# assert 'NANNY_TEMPLATE' in app.config, 'Please at least provide NANNY_TEMPLATE!'


@app.route("/nanny.json", methods=['POST'])
def nanny():
    """Nanny reciever endpoint

    if recieved is post and legit json, app.config['NANNY_TEMPLATE'] is then
    passed to pystache, otherwise app.config['NANNY_SCRIPT'] is used directly.

    ALWAYS returns true, no questions asked
    """
    data = request.get_json()

    for t, p in app.config.get('NANNY_PEEK', []):
        to_peek = pystache.render(t, data)
        m = re.match(to_peek)
        if not m:
            logging.info('unable to match re %s with %s (from template %s)', p, to_peek, t)
            abort(400)
        data.update(m.groupdict())

    template = app.config['NANNY_TEMPLATE']

    script = pystache.render(template, request.json)

    if not script.strip():
        logging.info('Nanny got empty script, ignoring...')
        abort(400)

    logging.info('Nanny to run script: \n%s', script)
    subprocess.Popen(script, shell=True)
    return jsonify(status='OK')


def main():
    import argparse
    parser = argparse.ArgumentParser(description='callbacknanny cmd tool')
    parser.add_argument('--host', help='host ip')
    parser.add_argument('--port', type=int, help='host port')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='toggle flask debug')
    parser.add_argument('-t', '--template', type=argparse.FileType('r'),
                        help='the mustache template to use')
    parser.add_argument('--peek', nargs=2, action='append',
                        help="peek into a template using regular expression. "
                             "All peeks must succeed to run the main template. "
                             "e.g. --peek foo ^abc$"
                        )
    args = parser.parse_args()
    if not args.template is None:
        app.config['NANNY_TEMPLATE'] = args.template.read()

    if args.peek:
        app.config['NANNY_PEEK'] = args.peek

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
