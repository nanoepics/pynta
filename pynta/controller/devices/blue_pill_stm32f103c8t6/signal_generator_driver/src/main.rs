#![deny(unsafe_code)]
#![deny(warnings)]
#![no_main]
#![no_std]

use cortex_m::asm::delay;
use embedded_hal::digital::v2::OutputPin;
use panic_halt as _;
use rtic::app;
use stm32f1xx_hal::prelude::*;
use stm32f1xx_hal::usb::{Peripheral, UsbBus, UsbBusType};
use stm32f1xx_hal::{
    gpio::{gpiob::PB7, PushPull},
    // time::U32Ext,
    pac::TIM4,
    pwm,
    pwm::Channel,
    timer::{Tim4NoRemap, Timer},
};
use usb_device::bus;
use usb_device::prelude::*;
use usbd_serial::{SerialPort, USB_CLASS_CDC};
type PwmPin = pwm::Pwm<TIM4, Tim4NoRemap, pwm::C2, PB7<stm32f1xx_hal::gpio::Alternate<PushPull>>>;
// We need to pass monotonic = rtic::cyccnt::CYCCNT to use schedule feature fo RTIC
#[app(device = stm32f1xx_hal::pac, peripherals = true, monotonic = rtic::cyccnt::CYCCNT)]
const APP: () =
    {
        struct Resources {
            led: PwmPin,
            usb_dev: UsbDevice<'static, UsbBusType>,
            serial: SerialPort<'static, UsbBusType>,
        }

        #[init()]
        fn init(cx: init::Context) -> init::LateResources {
            static mut USB_BUS: Option<bus::UsbBusAllocator<UsbBusType>> = None;

            // Enable cycle counter
            let mut core = cx.core;
            core.DWT.enable_cycle_counter();

            let device: stm32f1xx_hal::stm32::Peripherals = cx.device;

            // Setup clocks
            let mut flash = device.FLASH.constrain();
            let mut rcc = device.RCC.constrain();

            let mut afio = device.AFIO.constrain(&mut rcc.apb2);
            let clocks = rcc
                .cfgr
                .use_hse(8.mhz())
                .sysclk(48.mhz())
                .pclk1(24.mhz())
                .freeze(&mut flash.acr);
            assert!(clocks.usbclk_valid());
            // Setup LED
            let mut gpioa = device.GPIOA.split(&mut rcc.apb2);
            let mut usb_dp = gpioa.pa12.into_push_pull_output(&mut gpioa.crh);
            usb_dp.set_low().unwrap();
            delay(clocks.sysclk().0 / 100);
            let usb_dm = gpioa.pa11;
            let usb_dp = usb_dp.into_floating_input(&mut gpioa.crh);

            let usb = Peripheral {
                usb: device.USB,
                pin_dm: usb_dm,
                pin_dp: usb_dp,
            };

            *USB_BUS = Some(UsbBus::new(usb));
            let serial = SerialPort::new(USB_BUS.as_ref().unwrap());
            let usb_dev =
                UsbDeviceBuilder::new(USB_BUS.as_ref().unwrap(), UsbVidPid(0x16c0, 0x27dd))
                    .manufacturer("Pynta Project")
                    .product("Serial port")
                    .serial_number("Toy Signal Generator")
                    .device_class(USB_CLASS_CDC)
                    .build();

            let mut gpiob = device.GPIOB.split(&mut rcc.apb2);
            let pin = gpiob.pb7.into_alternate_push_pull(&mut gpiob.crl);
            let mut pwm = Timer::tim4(device.TIM4, &clocks, &mut rcc.apb1)
                .pwm::<Tim4NoRemap, _, _, _>(pin, &mut afio.mapr, 1.khz());
            pwm.enable(Channel::C2);
            let max = pwm.get_max_duty();
            pwm.set_duty(Channel::C2, max / 2);
            pwm.set_period(500.ms());
            init::LateResources {
                led: pwm,
                usb_dev,
                serial,
            }
        }
        #[task(binds = USB_HP_CAN_TX, resources = [usb_dev, serial, led])]
        fn usb_tx(mut cx: usb_tx::Context) {
            usb_poll(
                &mut cx.resources.usb_dev,
                &mut cx.resources.serial,
                &mut cx.resources.led,
            );
        }
        #[task(binds = USB_LP_CAN_RX0, resources = [usb_dev, serial, led])]
        fn usb_rx0(mut cx: usb_rx0::Context) {
            usb_poll(
                &mut cx.resources.usb_dev,
                &mut cx.resources.serial,
                &mut cx.resources.led,
            );
        }
        extern "C" {
            fn EXTI0();
        }
    };

fn usb_poll<B: bus::UsbBus>(
    usb_dev: &mut UsbDevice<'static, B>,
    serial: &mut SerialPort<'static, B>,
    pwm: &mut PwmPin,
) {
    if !usb_dev.poll(&mut [serial]) {
        return;
    }

    let mut buf = [0u8; 1024];

    match serial.read(&mut buf) {
        Ok(count) if count > 0 => {
            let period_ms = (buf[count - 1] as u32) * 4;
            pwm.set_period(stm32f1xx_hal::time::MilliSeconds(period_ms));
            serial.write(&buf[count - 1..count]).ok();
        }
        _ => {}
    }
}
