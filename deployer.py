import re
import os.path
import sys
import logging
import subprocess
from config import *

DEPLOYER_LOG_PATH = "/tmp/deployer.log"

MOUNTPOINT = "/mnt"
BADGE_SERIAL_DEV = "/dev/badge_serial"

BOOTLOADER_INFO_FILENAME = "INFO_UF2.TXT"
FIRMWARE_UPDATE_FILENAME = "firmware.uf2"
APP_BOOT_FILENAME = "boot_out.txt"

verbosity = logging.INFO
if DEBUG:
    verbosity = logging.DEBUG

logging.basicConfig(filename=DEPLOYER_LOG_PATH,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=verbosity)


def run_cmd(cmd):
    output = subprocess.check_output(cmd, shell=True, encoding='UTF-8')
    if len(output):
        logging.debug(f"run_cmd: {cmd} output: {output}")
    return output


def is_mounted(device):
    return os.path.ismount(device)


def mount(device, path):
    if is_mounted(path):
        return
    try:
        run_cmd(f"mount {device} {path}")
        return True
    except subprocess.CalledProcessError:
        return False


def umount(device):
    if not is_mounted(device):
        return
    run_cmd(f"umount {device}")


def update_bootloader():
    update_command = f"{ADAFRUIT_NRFUTIL_PATH} --verbose dfu serial --package {BOOTLOADER_BUILDED_ZIP_PATH} -p {BADGE_SERIAL_DEV} -b 115200 --singlebank --touch 1200"
    output = run_cmd(update_command)
    logging.debug("done updaing bootloader, see output:")
    logging.debug(output)
    assert 'Device programmed.' in output


def deploy_bootloader(mountpoint):
    info_filename = f"{mountpoint}/{BOOTLOADER_INFO_FILENAME}"
    if not os.path.exists(info_filename):
        logging.debug("can't find info file, not in bootloader mode")
        return False

    logging.debug("check if update is required ...")
    should_update = False
    with open(info_filename, "r") as f:
        data = f.read()
        assert "Badge" in data
        # stop condition, avoid getting into update loops
        should_update = (UPDATED_BOOTLOADER_DATE_IN_INFO not in data) or FORCE_UPDATE

    if should_update:
        logging.debug("updating bootloader")
        update_bootloader()

    logging.info("bootloader is up to date")

    logging.debug("copying firmware ...")
    run_cmd(f"cp {FIRMWARE_PATH} {mountpoint}/{FIRMWARE_UPDATE_FILENAME}")
    return True


def deploy_app(mountpoint):
    info_filename = f"{mountpoint}/{APP_BOOT_FILENAME}"
    if not os.path.exists(info_filename):
        logging.debug("can't find app boot file, not in app mode")
        return False

    logging.debug(f"copying {APP_FOLDER} content to {mountpoint}")
    run_cmd(f"cp -r {APP_FOLDER}/* {mountpoint}/")
    return True


def handle_mount(mountpoint, is_partition_dev):
    logging.debug(f"handling {mountpoint}")

    if is_partition_dev:
        if deploy_app(mountpoint):
            logging.info("app deployed")
            return
        logging.info("unexpected state: partition dev, can't deploy app")
    else:
        if deploy_bootloader(mountpoint):
            logging.info("bootloader deployed")
            return
        logging.info("unexpected state: not partition dev, can't deploy bootloader/fw")

    logging.info("unexpected state, no bootloader info or boot info")


def main():
    logging.debug("invoked with " + str(sys.argv))
    _, dev_path = sys.argv
    try:
        is_partition_dev = re.search(r'\d+$', dev_path)

        logging.debug(f"mounting {dev_path} at {MOUNTPOINT}")
        if mount(dev_path, MOUNTPOINT):
            handle_mount(MOUNTPOINT, is_partition_dev)
    except:
        logging.exception('[!] exception during deployment')
    finally:
        logging.debug(f"unmounting {dev_path} from {MOUNTPOINT}")
        umount(MOUNTPOINT)


main()
