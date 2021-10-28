import os
from multiprocessing import Process, Event, SimpleQueue

try:
    import pty
except ImportError:
    pty = None

import pytest

import use_minimon.flashing as flashing
from helpers import check_received_data, consume_serial_data, answers_size


def test_get_parser_paths():
    argv = ['crbl2', 'crbl2.srec',
            'bl2', 'build/deploy/images/bl2.srec']
    parser = flashing.get_parser()
    args = parser.parse_args(argv)
    args = vars(args)
    assert args.get('paths') is not None
    paths = args.get('paths')
    assert paths[0] == 'crbl2'
    assert paths[1] == 'crbl2.srec'
    assert paths[2] == 'bl2'
    assert paths[3] == 'build/deploy/images/bl2.srec'


@pytest.mark.option
def test_option_port_is_default():
    argv = []
    parser = flashing.get_parser()
    args = parser.parse_args(argv)
    args = vars(args)
    assert(args.get('port') == '/dev/ttyUSB0')


@pytest.mark.option
def test_port_could_be_set_by_user():
    argv = ['-p', '/dev/ttyUSB17',
            'crbl2', 'crbl2.srec']
    parser = flashing.get_parser()
    args = parser.parse_args(argv)
    args = vars(args)
    assert(args.get('port') == '/dev/ttyUSB17')


# How to test the main function?
# For now, multiprocessing is enough.
# How about asyncio or concurrent.futures?
@pytest.mark.skipif(pty is None, reason="pty module not supported on platform")
def test_main_send_file(data_dir):
    primary, replica = pty.openpty()
    done = Event()
    srec_file = os.path.join(data_dir, 'bootparam.srec')
    srec_size = os.stat(srec_file).st_size
    # file content + 'xlr2\r\n' + other answers  ...
    sent_size = srec_size + answers_size()
    results = SimpleQueue()
    reader = Process(target=consume_serial_data, args=(primary, sent_size, done, results))
    argv = [
        '-p',
        os.ttyname(replica),
        'bootp',
        srec_file,
    ]
    reader.start()
    flashing.main(argv)
    done.set()
    reader.join()
    actual = results.get()
    check_received_data(srec_file, actual)
