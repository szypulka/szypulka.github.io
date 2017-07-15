import logging

from thrift import Thrift
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport.TTransport import TTransportException
from thrift.protocol import TBinaryProtocol

from service.client import Client

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter('%(asctime)s %(levelname)s [%(processName)s: %(threadName)s] %(message)s')


def handle_exception(call_server):
    def wrapped(self, measure, *args):
        try:
            call_server(self, measure, *args)
        except Thrift.TException:
            measure['proto_code'] = 500
            LOGGER.exception('TException')
        except TTransportException.TIMED_OUT:
            measure['net_code'] = 110
            measure['proto_code'] = 0
            LOGGER.exception('Timeout')

    return wrapped


class BaseLoadTest(object):
    """Base class for LoadTest.

    This class should not be instantiated.
    """

    def __init__(self, gun):
        self.gun = gun

        test_server = self.gun.get_option('test_server')
        test_port = self.gun.get_option('test_port')

        test_socket = TSocket.TSocket(test_server, test_port)
        socket = test_socket.create()
        self.transport = TTransport.TFramedTransport(socket)

        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = Client(protocol)

    def setup(self, *args, **kwargs):
        self.transport.open()

    def teardown(self, *args, **qwargs):
        self.transport.close()
