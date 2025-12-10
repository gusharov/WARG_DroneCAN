#!/usr/bin/env python3
'''
dump all messages in YAML format
'''

import dronecan, time, math

# get command line arguments
from argparse import ArgumentParser
parser = ArgumentParser(description='dump all DroneCAN messages')
parser.add_argument("--bitrate", default=1000000, type=int, help="CAN bit rate")
parser.add_argument("--node-id", default=100, type=int, help="CAN node ID")
parser.add_argument("--dna-server", action='store_true', default=False, help="run DNA server")
args = parser.parse_args()
node = dronecan.make_node(None, node_id=args.node_id, bitrate=args.bitrate)
