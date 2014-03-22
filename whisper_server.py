from json import dumps
from os import chdir, walk, sep, getcwd
from os.path import join
from struct import unpack
from whisper import __readHeader, pointSize, pointFormat


def extract_archives(fh):
  header = __readHeader(fh)
  for archive in header['archives']:
    fh.seek(archive['offset'])
    a = []
    for _ in xrange(archive['points']):
      packedPoint = fh.read(pointSize)
      timestamp, value = unpack(pointFormat, packedPoint)
      if timestamp and value:
        a.append((timestamp, value))
    a.sort(key=lambda p: p[0])
    archive['points'] = a
  return header


def walk_whisper(path):
  cwd = getcwd()
  try:
    data = {}
    chdir(path)
    for dirpath, _, filenames in walk('.'):
      for name in filenames:
        if not name.endswith('.wsp'):
          continue
        fn = join(dirpath, name)
        stat_name = fn[2:-4].replace(sep, '.')
        with open(fn, 'rb') as fh:
          data[stat_name] = extract_archives(fh)
  finally:
    chdir(cwd)
  return data


def static(resource_path, start_response):
  start_response('200 OK', [('Content-type', 'text/html')])
  return open(resource_path, 'rb')


def serve_path(content_path, whisper_path):
  data = walk_whisper(whisper_path)
  for stat in data:
    data[stat] = dumps([data[stat]])
  stat_names = dumps({'stat_names': sorted(data)})

  def whisper_app(environ, start_response):
    stat_name = environ['PATH_INFO'].strip('/')
    if stat_name.startswith('o/'):
      resource = join(content_path, stat_name[2:])
      return static(resource, start_response)
    res = data.get(stat_name, '[]') if stat_name else stat_names
    start_response('200 OK', [('Content-type', 'application/json')])
    return [res]

  return whisper_app


if __name__ == '__main__':
  from argparse import ArgumentParser
  from wsgiref.simple_server import make_server

  parser = ArgumentParser()
  parser.add_argument(
    'whisper_path',
    help='Path to the whisper database directory.',
    )
  parser.add_argument(
    '-c', '--content_path',
    help='Path to the directory containing the site_content directory.',
    default='.',
    )
  parser.add_argument(
    '-I', '--IP',
    help='IP address to listen on',
    default='',
    )
  parser.add_argument(
    '-p', '--port',
    help='port to listen on',
    type=int,
    default=8000,
    )
  args = parser.parse_args()

  content_path = join(args.content_path, 'site_content')
  wsgi_app = serve_path(content_path, args.whisper_path)
  httpd = make_server(args.IP, args.port, wsgi_app)
  print "Serving on port 8000..."
  httpd.serve_forever()
