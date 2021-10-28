import os
from multiprocessing import Process, Event, SimpleQueue

try:
    import pty
except ImportError:
    pty = None

import pytest

from use_minimon.responder import Responder
from helpers import check_received_data, consume_serial_data, answers_size


@pytest.fixture
def responder_cr():
    responder = Responder(target="starter-kit-cr", port="loop://")
    yield responder


def test_raise_exc_if_target_is_wrong():
    with pytest.raises(ValueError):
        Responder(target="salvator", port="loop://")


def test_get_flashmap():
    responder = Responder(target="starter-kit-cr", port="loop://")
    assert responder.flashmap.get('crbl2') is not None
    crbl2 = responder.flashmap.get('crbl2')
    assert crbl2.get('text_base') == 0xE630_4000


def test_get_flashmap2(responder_cr):
    assert responder_cr.flashmap.get('crbl2') is not None


def test_get_addresses(responder_cr):
    addresses = responder_cr.get_addresses(name="crbl2")
    assert(len(addresses) == 2)
    assert(addresses.get("flash_base") == 0x0004_0000)
    assert(addresses.get("text_base") == 0xE630_4000)


def test_get_available_partitions(responder_cr):
    partitions = responder_cr.get_available_partitions()
    assert partitions == "bootp, crbl2, bl2, sa6, bl31, optee, ubootca, ubootcr, rtos"


def test_get_addresses_raises_exc(responder_cr):
    with pytest.raises(ValueError):
        responder_cr.get_addresses(name="crbl")


def test_send_file_raises_exception(responder_cr):
    with pytest.raises(FileNotFoundError, match='No such file') as exc_info:
        responder_cr.send_file(name="crbl2", path='./dog')
    assert 'dog' in exc_info.value.args[0]


def test_open_serial_port_raises_exception(responder_cr, data_dir):
    with pytest.raises(ValueError):
        responder = Responder(target="starter-kit-cr", port="/dev/ttyUSBdog")
        srec_file = os.path.join(data_dir, 'bootparam.srec')
        responder.send_file(name="bootp", path=srec_file)


@pytest.mark.skipif(pty is None, reason="pty module not supported on platform")
def test_send_file(data_dir):
    primary, replica = pty.openpty()
    done = Event()
    srec_file = os.path.join(data_dir, 'bootparam.srec')
    srec_size = os.stat(srec_file).st_size
    sent_size = srec_size + answers_size()
    results = SimpleQueue()
    reader = Process(target=consume_serial_data, args=(primary, sent_size, done, results))
    responder = Responder(target="starter-kit-cr", port=os.ttyname(replica))
    reader.start()
    responder.send_file(name="bootp", path=srec_file)
    done.set()
    reader.join()
    check_received_data(srec_file, results.get())
