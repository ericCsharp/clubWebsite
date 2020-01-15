from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer
import join
import mimetypes
import common, email_confirmation

static_files = {'/about.html', '/contact.html', '/faq.html', '/index.html', '/join.html'}
def serve_file(environ, start_response):
    if environ['REQUEST_METHOD'] != "GET":
        yield from common.error_page(environ, start_response, "Bad request", code="405 Method Not Allowed")
        return
    try:
        with open('.' + environ['PATH_INFO'], 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        yield from common.error_page(environ, start_response, "404 Not Found", code="404 Not Found")
        return
    else:
        start_response('200 OK', [('Content-Type', mimetypes.guess_type(environ['PATH_INFO'])[0] )])
        yield data

def application(environ, start_response):
    try:
        path = environ['PATH_INFO']
        if path == '/join':
            yield from join.application(environ, start_response)
        elif path == '/confirm':
            yield from email_confirmation.confirm(environ, start_response)
        elif path == '/email_sent':
            yield from join.email_sent_page(environ, start_response)
        elif path in static_files or path.startswith('/stylesheets/') or path.startswith('/images/'):
            yield from serve_file(environ, start_response)
        else:
            yield from common.error_page(environ, start_response, "404 Not Found", code="404 Not Found")
            return

    except Exception as e:
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')] )
        yield b'500 Internal Server Error'
        raise

server = WSGIServer(('127.0.0.1', 8080), application)
print('Started httpserver on port ' , 8080)
server.serve_forever()
