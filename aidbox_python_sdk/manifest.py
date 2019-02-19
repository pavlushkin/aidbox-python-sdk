from fhirpy import FHIRClient
from aiohttp import BasicAuth


class Manifest(object):

    def __init__(self, settings):
        self._settings = settings
        self._subscriptions = {}
        self._subscription_handlers = {}
        self._operations = {}
        self._operation_handlers = {}
        self._manifest = {
            'id': settings.APP_ID,
            'resourceType': 'App',
            'type': 'app',
            'apiVersion': 1,
            'endpoint': {
                'url': settings.APP_URL,
                'type': 'http-rpc',
                'secret': settings.APP_SECRET,
            }
        }


    def init_client(self, config):
        basic_auth = BasicAuth(
            login=config['client']['id'],
            password=config['client']['secret'])
        self.client = FHIRClient('{}/fhir'.format(config['box']['base-url']),
                                 authorization=basic_auth.encode())

    def build(self):
        if self._subscriptions:
            self._manifest['subscriptions'] = self._subscriptions
        if self._operations:
            self._manifest['operations'] = self._operations
        return self._manifest

    def subscription(self, entity):
        def wrap(func):
            path = func.__name__
            self._subscriptions[entity] = {'handler': path}
            self._subscription_handlers[path] = func
            return func
        return wrap

    def get_subscription_handler(self, path):
        return self._subscription_handlers.get(path)

    def operation(self, method, path):
        def wrap(func):
            if not isinstance(path, list):
                raise ValueError('`Path` must be a list')
            operation_id = func.__name__
            self._operations[operation_id] = {
                'method': method,
                'path': path,
            }
            self._operation_handlers[operation_id] = func
            return func
        return wrap

    def get_operation_handler(self, operation_id):
        return self._operation_handlers.get(operation_id)
