# `Use-Minimon`

This package is an in-house tool that makes it easy to use `Renesas MiniMonitor`.

Using the `MiniMonitor` is a cumbersome thing.
You have to type a couple of 'Y' and hex addresses just to flash a binary.
This package is a simple script to automatically answer questions of `MiniMonitor`
and send a binary file to `MiniMonitor` to flash it into HyperFlash memory.


## Installation

Use-Minimon is published on [PyPI](https://pypi.org/project/use-minimon-dj/)
and can be install from there

```shell
pip install -U use-minimon-dj
```


## How to Use

1. Bringing up `MiniMonitor` stored in QSPI NOR Flash memory

    These DIP switches and jumper must be configured like this:

    ```
    SW1 = OFF
    SW6 = ON ON OFF ON (A57, QSPI, DDR3200)
    JP1 = 1-2 Short
    ```

1. Turning on the target board

    Push the switch No. 8 to turn on the target board.

    ```
    R-Car Gen3 Sample Loader V5.08 2018.10.22
    For Salvator , Kriek , and StarterKit.(R-CarH3/R-CarM3)
    Board Judge     : Used Board-ID
    DDR_Init        : boardcnf[8] Salvator (H3SIP_VER2.0/3.0-2rank)
    INITIAL SETTING : Starter Kit Premier / R-Car H3 ES3.0
    CPU / BOOT MODE : AArch64 CA57-CPU0 / CA57 Boot Mode (MD15:AArch64)
    DRAM            : LPDDR4 DDR3200 / 8GB_2RANK
    DEVICE          : QSPI Flash(S25FS128) at 40MHz DMA
    BOOT            : Normal Boot
    BACKUP          : DDR Cold Boot
    jump to 0xE6330000

    R-Car Gen3 MiniMonitor V5.08 2018.10.22
    Work Memory     : SystemRAM Board Judge     : Used Board-ID
    Board Name      : Starter Kit Premier
    Product Code    : R-Car H3 ES3.0

    >
    ```

1. Configuring DIP switches to enable HyperFlash memory

    ```
    SW1 = ON
    SW6 = ON ON ON ON (A57, HyperFlash 80 MHz, DDR3200)
    ```

1. Executing `mm-flashing` command like so on your workstation

    ```shell
    $ mm-flashing crbl2 crbl2.srec
    ```


The output of the target board will be something like this
```
R-Car Gen3 Sample Loader V5.08 2018.10.22
 For Salvator , Kriek , and StarterKit.(R-CarH3/R-CarM3)
 Board Judge     : Used Board-ID
 DDR_Init        : boardcnf[8] Salvator (H3SIP_VER2.0/3.0-2rank)
 INITIAL SETTING : Starter Kit Premier / R-Car H3 ES3.0
 CPU / BOOT MODE : AArch64 CA57-CPU0 / CA57 Boot Mode (MD15:AArch64)
 DRAM            : LPDDR4 DDR3200 / 8GB_2RANK
 DEVICE          : QSPI Flash(S25FS128) at 40MHz DMA
 BOOT            : Normal Boot
 BACKUP          : DDR Cold Boot
 jump to 0xE6330000

R-Car Gen3 MiniMonitor V5.08 2018.10.22
 Work Memory     : SystemRAM
 Board Judge     : Used Board-ID
 Board Name      : Starter Kit Premier
 Product Code    : R-Car H3 ES3.0

>xls2
===== Qspi/HyperFlash writing of Gen3 Board Command =============
Load Program to Spiflash
Writes to any of SPI address.
Please select,FlashMemory.
   1 : QspiFlash       (U5 : S25FS128S)
   2 : QspiFlash Board (CN2: S25FL512S)
   3 : HyperFlash      (SiP internal)
  Select (1-3)>3
 READ ID OK.
Program Top Address & Qspi/HyperFlash Save Address
===== Please Input Program Top Address ============
  Please Input : H'51000000

===== Please Input Qspi/HyperFlash Save Address ===
  Please Input : H'740000
Work RAM(H'50000000-H'53FFFFFF) Clear....
please send ! ('.' & CR stop load)
SPI Data Clear(H'FF) Check : OK
SAVE SPI-FLASH....... complete!

======= Qspi/HyperFlash Save Information  =================
 SpiFlashMemory Stat Address : H'00740000
 SpiFlashMemory End Address  : H'007FF9C7
===========================================================
```
