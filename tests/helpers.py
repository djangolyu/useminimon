from multiprocessing import synchronize
import os


def answers_size() -> int:
    return (6+3+1+1+10+10+1)


# How to emulate serial communication?
#    - Use aiofiles ?  https://github.com/Tinche/aiofiles
def consume_serial_data(primary: str, size, done: synchronize.Event, results):
    with os.fdopen(primary, "rb") as fd:
        # FIXME: read() is blocking I/O, Non-blocking I/O is needed.
        buf = fd.read(size)
    results.put(buf)


def check_received_data(sent_file: str, actual: bytes) -> None:
    with open(sent_file, 'rb') as fd:
        expected_content = fd.read()

    assert actual[:6] == 'xls2\r\n'.encode('ascii')
    assert actual[6:9] == '3\r\n'.encode('ascii')
    assert actual[9:11] == 'YY'.encode('ascii')
    assert actual[11:21] == 'E6320000\r\n'.encode('ascii')
    assert actual[21:31] == '00000000\r\n'.encode('ascii')
    assert actual[31:-1] == expected_content
    assert actual[-1:] == 'y'.encode('ascii')
