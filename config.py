# IMPORTANT: install requirements.txt as root also!
ADAFRUIT_NRFUTIL_PATH = "adafruit-nrfutil"

# we use the date field in the info file of the bootloader as a verifier for an up to date version.
UPDATED_BOOTLOADER_DATE_IN_INFO = "Jun  7 2021"
# local path to bootloader build
BOOTLOADER_BUILDED_ZIP_PATH = "/home/pi/bootloader.zip"
# local path to firmware build
FIRMWARE_PATH = "/home/pi/firmware.uf2"
# the app folder must include everything (including full lib directory), will be mirrored onto CP partition
APP_FOLDER = "/home/pi/app"