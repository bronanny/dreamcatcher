from json import dumps
from os import chdir, walk, sep, getcwd
from os.path import join, splitext
from struct import unpack
from whisper import __readHeader, pointSize, pointFormat


STATIC = 'o/'
N = len(STATIC)
CONTENT_TYPES = dict(
  css='text/css',
  html='text/html',
  js='application/javascript',
  )


ext_of = lambda filename: splitext(filename)[1][1:]


def extract_archives(fh):
  header = __readHeader(fh)
  for archive in header['archives']:
    n = pointSize * archive['points']
    fh.seek(archive['offset'])
    points = fh.read(n)
    a = []
    for i in xrange(0, n, pointSize):
      packedPoint = points[i:i + pointSize]
      timestamp, value = unpack(pointFormat, packedPoint)
      a.append((timestamp, value or 0))
    a.sort(key=lambda p: p[0])
    archive['most_recent'] = a[-1][0] if a else -1
    archive['oldest'] = a[1][0] if a else -1
    archive['points'] = [p for p in a if p[1] is not None]
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


def collect_static_files(content_path, acceptable_extensions=CONTENT_TYPES):
  files = {}
  for dirpath, dirs, filenames in walk(content_path):
    d = dirpath[len(content_path):].strip(sep)
    for filename in filenames:
      if ext_of(filename) in acceptable_extensions:
        files[join(d, filename)] = join(dirpath, filename)
  return files


def static(resource_path, start_response):
  start_response('200 OK', [('Content-type', ctype(resource_path))])
  return open(resource_path, 'rb')


def ctype(path, types=CONTENT_TYPES):
  return types[ext_of(path)]


def serve_path(whisper_path, content_path=None):
  data = walk_whisper(whisper_path)
  for stat in data:
    data[stat] = dumps(data[stat])
  stat_names = dumps({'stat_names': sorted(data)})

  def serve_stat(stat_name, start_response):
    res = data.get(stat_name, '{}') if stat_name else stat_names
    start_response('200 OK', [('Content-type', 'application/json')])
    return [res]

  if content_path:
    content_path = join(content_path, 'site_content')
    static_files = collect_static_files(content_path)

    def whisper_app(environ, start_response):
      stat_name = environ['PATH_INFO'].strip('/')
      if stat_name.startswith(STATIC):
        resource_path = static_files.get(stat_name[N:])
        if not resource_path:
          start_response('404 NOT FOUND', [('Content-type', 'text/html')])
          return ['404 NOT FOUND']
        return static(resource_path, start_response)
      return serve_stat(stat_name, start_response)

  else: # Don't serve static content.

    def whisper_app(environ, start_response):
      stat_name = environ['PATH_INFO'].strip('/')
      return serve_stat(stat_name, start_response)

  return whisper_app


##from pprint import pprint
##pprint(collect_static_files(
##  'C:\\Users\\Jesse\\Desktop\\vag\\dreamcatcher\\dreamcatcher'
##  '\\site_content')
##)

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

  wsgi_app = serve_path(args.whisper_path, args.content_path)
  httpd = make_server(args.IP, args.port, wsgi_app)
  print "Serving on port 8000..."
  httpd.serve_forever()

