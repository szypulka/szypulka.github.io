import os
import json
import logging.handlers

from base_load_test import BaseLoadTest, FORMATTER, LOGGER
from base_load_test import handle_exception
from service.client import parse_cluster_state

RETRY_LIMITS = 500

FILE_HANDLER = logging.handlers.RotatingFileHandler(
    ''.join((os.path.splitext(os.path.basename(__file__))[0], os.path.extsep, 'log')),
    maxBytes=1024 * 1024,
    backupCount=5)
FILE_HANDLER.setLevel(logging.DEBUG)
FILE_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(FILE_HANDLER)


class LoadTest(BaseLoadTest):
    def __init__(self, gun):

        super(LoadTest, self).__init__(gun)
        self.wait_for_activation = json.loads(gun.get_option('wait_for_activation', 'true'))

    @handle_exception
    def get_state(self):
        with self.gun.measure('get_state') as measure:
            response = self.client.get_state()
            if not response:
                measure['proto_code'] = 404

        return response

    @handle_exception
    def apply(self, cluster_state):

        configuration = parse_cluster_state(cluster_state)
        with self.gun.measure('apply') as measure:
            self.client.apply(configuration)

    @handle_exception
    def check_state(self):
        with self.gun.measure('check_state') as measure:
            state = self.client.check_state()
        return state

    def default(self):
        current_state = self.get_state()
        with self.gun.measure('activated'):
            self.apply(current_state)
            if self.wait_for_activation:
                counter = 0
                state = False
                while not state and counter < RETRY_LIMITS:
                    state = self.check_state()
                    counter += 1
