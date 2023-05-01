#!/usr/bin/env python

import requests
import time
from rich import print
import datetime

from pyShelly.relay import Relay
from pyShelly import pyShelly

from config import (MAX_FAILED_RESPONSES, SLEEP_TIME, RESET_SLEEP_TIME, HASS_URL,
                    WATCHDOG_WEBHOOK, SHELLY_RELAY_ID)

hass_alive = False
failed_responses = 0

relay_device = None

def ping_hass():
    global failed_responses
    global hass_alive

    try:
        now = datetime.datetime.now()
        print(f"----- {now} -----")
        print("Pinging hass.. ", end="" )
        url = f"{HASS_URL}/api/webhook/{WATCHDOG_WEBHOOK}"
        # print(f"URL: {url}")
        r = requests.post(url)
        print(f"[bold green]Alive![/bold green] {r.text}")
        hass_alive = True

    except Exception as exc:
        failed_responses += 1
        print(f"[bold red]Down![/bold red] Exception: [red]{exc}[/red] Failed: {failed_responses}")
        if hass_alive and failed_responses > MAX_FAILED_RESPONSES:
            hass_alive = False


def is_hass_alive():
    return hass_alive


def turn_off_shelly():
    print("Turning off shelly device.. ", end="")
    if not relay_device:
        print("[bold red]ERROR: Shelly device not found yet![/bold red]")
        return False

    relay_device.turn_off()

    print("Done!")
    return True


def turn_on_shelly():
    print("Turning on shelly device.. ", end="")
    if not relay_device:
        print("[bold red]ERROR: Shelly device not found yet![/bold red]")
        return False

    relay_device.turn_on()
    print("Done!")

    return True


def reset_hass():
    if not turn_off_shelly():
        return

    time.sleep(5)

    if not turn_on_shelly():
        return

    print(f"Waiting for {RESET_SLEEP_TIME} seconds to check health again.")
    time.sleep(RESET_SLEEP_TIME)

def main():
    while True:
        ping_hass()

        if not is_hass_alive():
            print("Resetting hass")
            reset_hass()

        print(f"Sleeping for {SLEEP_TIME} seconds")
        time.sleep(SLEEP_TIME)


def shelly_init():
    shelly = pyShelly()
    print("version:", shelly.version())

    shelly.cb_device_added.append(device_added)
    shelly.start()
    shelly.discover()


def device_added(dev, code):
    global relay_device

    if not dev.id.startswith(SHELLY_RELAY_ID):
        print(f"Device {dev.id} ignored.", end="\r")
        return

    if not isinstance(dev, Relay):
        # print("Device type is not Relay")
        return

    print ("[bold green]Device found!![/bold green]: ", end="")

    print(f"{dev.id} | {dev.friendly_name()} | {dev.state}")

    relay_device = dev


if __name__ == "__main__":
    shelly_init()
    main()
