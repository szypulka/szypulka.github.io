import logging
import requests
import time

class LoadTest(object):
    """ Some class for LoadTest """

    def __init__(self, gun):
        self.gun = gun
        self.test_server = self.gun.get_option('test_server')
        self.test_port = self.gun.get_option('test_port', default='443')
        self.api_path = self.gun.get_option('api_path')

    def default(self, missile):

        get_url = 'http://{}:{}{}'.format(self.test_server, self.test_port, self.api_path)
        first_url = get_url + '/tank/status.json'
        second_url = get_url + '/not/existent/path'

        current_session = requests.Session()
        current_session.headers.update({'X-Some-Header-With-ID': missile})
        logging.debug('Headers for the session: %s', current_session.headers)

        with self.gun.measure('first_req'):
            first_req = current_session.get(first_url)
        if first_req.status_code == 200:
            logging.info('First req done. Response is %s', first_req.text)
        else:
            logging.warning('First req got response code %s', first_req.status_code)
        time.sleep(1)

        with self.gun.measure('second_req'):
            second_req = current_session.get(second_url)
            logging.info('Second request is done.')
            logging.debug('Second request got status code %, response is %s',
                          second_req.status_code, second_req.text)
        time.sleep(1)
