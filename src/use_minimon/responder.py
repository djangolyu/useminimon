"""
    The Responder class answers questions of the Renesas' Mini-Monitor
    to flash a binary into the HyperFlash memory.
"""

import logging
import os
import sys
import time
from typing import Dict

import tqdm
import toml
import serial

logger = logging.getLogger("Responder")


class Responder:
    def __init__(self, target: str, port: str):
        """Initialize the Responder class
            1. Read flashmap.toml
            2. Save the serial port name
        """
        logger.debug(f"Flasher.init({target}, {port})")
        flashmap_data = self.load_flashmap()
        if (flashmap := flashmap_data.get(target)) is None:
            raise ValueError("Invalid target board")
        else:
            self.flashmap = flashmap
        self.port = port

    def load_flashmap(self):
        """Load the flashmap.toml resided in the source directory"""
        # TODO: an user could specify their own flashmap.
        file_path = os.path.dirname(os.path.abspath(__file__))
        flashmap_file = os.path.join(file_path, "flashmap.toml")
        if os.path.isfile(flashmap_file):
            logger.info("Found flashmap.toml")
        else:
            raise FileNotFoundError("No such file: flashmap.toml")

        try:
            with open(flashmap_file) as f:
                flashmap_data = toml.load(f)
                logger.info("Loaded flashmap.toml")
        except (toml.TomlDecodeError, KeyError):
            raise ValueError("Invalid flashmap.toml")
        return flashmap_data

    def get_available_partitions(self) -> str:
        """Return available partition names"""
        return ', '.join(self.flashmap.keys())

    def show_partitions(self) -> None:
        """Show available partitions with description"""
        print('{:>10} {:<25} {}'.format(
            'Name', 'Description', 'Sector Addrress'))
        fmt = "{name:>10}: {description:<25} {flashbase:>08X}"
        for key in self.flashmap.keys():
            info = self.flashmap.get(key)
            print(fmt.format(
                name=key,
                description=info['description'],
                flashbase=info['flash_base']))

    def get_addresses(self, name: str) -> Dict:
        """Return base addresses given partition name
            MiniMonitor requires two bases addresses: TEXT, FLASH
        """
        if (content := self.flashmap.get(name)) is None:
            raise ValueError(f"Invalid partition name \"{name}\"")
        return {k: v for k, v in content.items() if k.endswith("base")}

    def _write_file(self, path: str, ser: serial.Serial) -> int:
        """dump the binary file to the serial port"""
        time.sleep(.5)  # Take a break, ORER ???
        written = 0
        total = os.stat(path).st_size
        try:
            with tqdm.tqdm(total=total) as pbar:
                chunk_size = 4096
                with open(path, 'rb') as f:
                    while True:
                        buf = f.read(chunk_size)
                        if len(buf) == 0:
                            break
                        try:
                            sent = ser.write(buf)
                            ser.flush()
                        except serial.SerialTimeoutException as exp:
                            raise exp
                        written += sent
                        pbar.update(sent)

        except KeyboardInterrupt:
            sys.exit(1)
        print("")
        time.sleep(0.2)
        return written

    def _send_answer(self, answer: str, ser: serial.Serial) -> None:
        """Send an answer to the target board"""
        ser.write(answer.encode('ascii'))
        # Wait for a second while The MiniMonitor prints some messages
        time.sleep(0.2)

    def send_file(self, name: str, path: str) -> None:
        """Send a file to MiniMonitor via the serial port opened

            1. Check an input file
            2. Open a serial port
            3. Answers the questions of the MiniMonitor
            4. Send a binary file
            5. Confirm the write operation of the MiniMonitor
        """

        try:
            addresses = self.get_addresses(name)
        except ValueError as exc:
            raise exc

        path = os.path.abspath(path)
        if os.path.isfile(path):
            logger.info(f"Found {path}")
        else:
            raise FileNotFoundError(f"No such file: {path}")

        minimon_answers = [
            'xls2\r\n',     # A MiniMontor command
            '3\r\n',
            'Y',        # Dip switch 1?
            'Y',        # Dip switch 6.3?
            '{:08X}\r\n'.format(int(addresses.get('text_base', 0xffff_fffff))),
            '{:08X}\r\n'.format(int(addresses.get('flash_base', 0xffff_ffff))),
        ]

        try:
            with serial.serial_for_url(self.port,
                                       baudrate=115200,
                                       timeout=1,
                                       write_timeout=5) as ser:

                for answer in minimon_answers:
                    self._send_answer(answer, ser)

                written = self._write_file(path, ser)
                logger.info(f"{written} bytes being sent")

                # Confirm
                self._send_answer('y', ser)
        except serial.serialutil.SerialException as exp:
            raise ValueError(f"Invalid port: {self.port} ({exp}))") from None
        except serial.SerialTimeoutException as exp:
            raise exp
