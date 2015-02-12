#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import logging
import random
import sys
import time
import uuid

import kombu
from kombu.pools import producers
import queues


def initialize_logging():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def parse_command_line_arguments():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-height", type=int, default=1024,
                        help="The maximum height of the generate image.")
    parser.add_argument("--max-width", type=int, default=1024,
                        help="The maximum width of the generated image.")
    parser.add_argument("--max-xa", type=float, default=-4.0,
                        help="The maximum value for the parameter 'xa'.")
    parser.add_argument("--max-xb", type=float, default=4.0,
                        help="The maximum value for the parameter 'xb'.")
    parser.add_argument("--max-ya", type=float, default=-3,
                        help="The maximum value for the parameter 'ya'.")
    parser.add_argument("--max-yb", type=float, default=3,
                        help="The maximum value for the parameter 'yb'.")
    parser.add_argument("--max-iterations", type=int, default=512,
                        help="The maximum number of iterations.")
    parser.add_argument("--min-height", type=int, default=256,
                        help="The minimum height of the generate image.")
    parser.add_argument("--min-width", type=int, default=256,
                        help="The minimum width of the generated image.")
    parser.add_argument("--min-xa", type=float, default=-1.0,
                        help="The minimum value for the parameter 'xa'.")
    parser.add_argument("--min-xb", type=float, default=1.0,
                        help="The minimum value for the parameter 'xb'.")
    parser.add_argument("--min-ya", type=float, default=-0.5,
                        help="The minimum value for the parameter 'ya'.")
    parser.add_argument("--min-yb", type=float, default=0.5,
                        help="The minimum value for the parameter 'yb'.")
    parser.add_argument("--min-iterations", type=int, default=128,
                        help="The minimum number of iterations.")
    parser.add_argument("--min-pause", type=float, default=1.0,
                        help="The minimum pause in seconds.")
    parser.add_argument("--max-pause", type=float, default=10.0,
                        help="The maximum pause in seconds.")
    parser.add_argument("--min-tasks", type=int, default=1,
                        help="The minimum number of generated tasks.")
    parser.add_argument("--max-tasks", type=int, default=10,
                        help="The maximum number of generated tasks.")
    return parser.parse_args()


def generate_task(args):
    random.seed()

    width = random.randint(args.min_width, args.max_width)
    height = random.randint(args.min_height, args.max_height)
    iterations = random.randint(args.min_iterations, args.max_iterations)
    xa = random.uniform(args.min_xa, args.max_xa)
    xb = random.uniform(args.min_xb, args.max_xb)
    ya = random.uniform(args.min_ya, args.max_ya)
    yb = random.uniform(args.min_yb, args.max_yb)

    return {
        'id': uuid.uuid4(),
        'width': width,
        'height': height,
        'iterations': iterations,
        'xa': xa,
        'xb': xb,
        'ya': ya,
        'yb': yb
    }

def main():
    initialize_logging()
    args = parse_command_line_arguments()

    connection = kombu.Connection('amqp://tutorial:secretsecret@localhost:5672//')

    while True:
        random.seed()
        number = random.randint(args.min_tasks, args.max_tasks)
        logging.info("generating %d task(s)" % number)
        for i in xrange(0,number):
            task = generate_task(args)
            logging.info("generated task: %s" % task)
            with producers[connection].acquire(block=True) as producer:
                producer.publish(task, serializer='pickle',
                                 exchange=queues.task_exchange,
                                 declare=[queues.task_exchange],
                                 routing_key='normal')

        pause = random.uniform(args.min_pause, args.max_pause)
        logging.info("sleeping for %f seconds" % pause)
        time.sleep(pause)

    return 0

if __name__ == '__main__':
    sys.exit(main())