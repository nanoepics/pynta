# STM32F103 Bluepill signal generator test

A simple firmware for generating a square wave signal with the popular 'bluepill' development board. It only supports changing the frequency.
 When connected to a pc via usb it will show up as virtual serial port (USB CDC device) and the frequency can then be changed by writting single byte values to this device. Each byte indicates the period of the signal times 4ms. So writing `0x01` to the device will cause set its frequency to `1/4ms = 250Hz.` and writing `250` to the device will set the frequency to `1/(250*4ms) = 1 Hz`.

## How-to

### Flashing

Rust embedded relies heavily on `terminal workflow`, you will enter commands in the terminal. This can be strange at first, but this enables usage of great things like continious integration tools.

For Mac OS X consider using `iTerm2` instead of Terminal application.
For Windows consider using `powershell` (win + r -> powershell -> enter -> cd C:\examples\rtic_v5\bluepill_blinky)

### Build

Run `cargo build` to compile the code. If you run it for the first time, it will take some time to download and compile dependencies. After that, you will see comething like:

```bash
>cargo build
Finished dev [optimized + debuginfo] target(s) in 0.10s
```

If you see warnings, feel free to ask for help in chat or issues of this repo.

### Connect the board

You need to connect you bluepill board to ST-Link and connect pins:

| BOARD |    | ST-LINK |
|-------|----|---------|
| GND   | -> | GND     |
| 3.3V  | -> | 3.3V    |
| SWCLK | -> | SWCLK   |
| SWDIO | -> | SWDIO   |

Plug in ST-Link to USB port and wait it to initialize.

### Flashing and running

Flashing with a standard STLink v2 is easy with `cargo-embed`:

```shell
$ cargo install cargo-embed
$ cargo flash --release
```
