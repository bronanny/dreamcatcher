from json import dumps
from os import chdir, walk, sep
from os.path import join
from struct import unpack
from whisper import __readHeader, pointSize, pointFormat


ROOT_PATH = r'C:\Users\Jesse\Desktop\vag\dreamcatcher\dreamcatcher\site_content'


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
  return data


def static(resource_name, environ, start_response):
  f = open(resource_name, 'rb')
  start_response('200 OK', [('Content-type', 'text/html')])
  return f


def serve_path(path):
  data = walk_whisper(path)
  for stat in data:
    data[stat] = dumps([data[stat]])
  stat_names = dumps({'stat_names': sorted(data)})

  def whisper_app(environ, start_response):
    stat_name = environ['PATH_INFO'].strip('/')
    if stat_name.startswith('o/'):
      resource = join(ROOT_PATH, stat_name[2:])
      return static(resource, environ, start_response)
    res = data.get(stat_name, '[]') if stat_name else stat_names
    start_response('200 OK', [('Content-type', 'application/json')])
    return [res]

  return whisper_app


if __name__ == '__main__':
  from wsgiref.simple_server import make_server
  path = r'C:\Users\Jesse\Desktop\vag\mongo-whisper\stats'
  httpd = make_server('', 8000, serve_path(path))
  print "Serving on port 8000..."
  httpd.serve_forever()
