from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from models import DBSession

def main(global_config, **settings):
#def main():
    """ This function returns a Pyramid WSGI application.
    """
#    engine = engine_from_config(settings, 'sqlalchemy.')
#    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
#    config = Configurator()
#    config.add_view(views.ProvisioningViews)
    config.add_static_view('deform_static', 'deform:static', cache_max_age=0)
    config.add_static_view('static', 'static')
#    config.scan("views")
    config.scan()
    return config.make_wsgi_app()



#if __name__ == '__main__':
#    app = main("serve ../development.ini")
#    server = make_server('0.0.0.0', 8080, app)
#    server.serve_forever()