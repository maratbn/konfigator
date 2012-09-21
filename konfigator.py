#!/usr/bin/python

import argparse

argument_parser = argparse.ArgumentParser(
                        description='Search the Linux kernel Kconfig files.')

argument_parser.add_argument(
    '-k', '--kernel',
    default='/usr/src/linux/',
    help='path to the Linux kernel source tree to search (default: %(default)s)',
    metavar='path')

args = argument_parser.parse_args()


print args
