import sys
from itertools import chain, imap
from statsd import StatsdClient


def f(lines):
  return chain.from_iterable(imap(convert_datum, lines))


def convert_datum((collection, total, read, write)):
  soc, dot, col = collection.partition('.')
  if soc == 'socialvilla' and dot:
    collection = col
  yield collection + '.total', int(total[:-2])
  yield collection + '.read', int(read[:-2])
  yield collection + '.write', int(write[:-2])


def main(data_source, client):
  gauge = client.gauge
  for dataset in data_source:
    for bucket, value in f(dataset):
      gauge(bucket, value)


def acc(line_source):
  a = []
  while True:
    line = line_source()
    if not line:
      break
    line = line.strip()
    if line:
      a.append(line.split())
    else:
      yield a[1:]
      a = []


if __name__ == '__main__':
  from argparse import ArgumentParser

  parser = ArgumentParser()
  parser.add_argument(
    '-I', '--IP',
    help='Host or IP address to which to send stats.',
    default='',
    )
  parser.add_argument(
    '-p', '--port',
    help='Port on which to listen.',
    type=int,
    default=8125,
    )
  parser.add_argument(
    '-P', '--prefix',
    help='Tag to prefix to outgoing stats.',
    default='mongotop',
    )
  args = parser.parse_args()

  client = StatsdClient(
    host=args.host,
    port=args.port,
    prefix=args.prefix,
    )
  main(acc(sys.stdin.readline), client)

