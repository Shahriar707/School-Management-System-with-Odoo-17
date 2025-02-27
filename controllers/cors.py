from odoo.http import Controller, request, Response

class CorsController(Controller):
    @staticmethod
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization'
        return response

    def dispatch(self, *args, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            response = Response()
            return self.add_cors_headers(response)
        response = super(CorsController, self).dispatch(*args, **kwargs)
        return self.add_cors_headers(response)