import asyncio
import logging
from bleak import discover

from .. import fhem


class discover_ble:
    def __init__(self, logger):
        self.logger = logger
        # disable bleak discovery messages
        logging.getLogger("bleak.backends.bluezdbus.discovery").setLevel(logging.ERROR)
        self.hash = None
        self.blescanTask = None
        return

    async def runBleScan(self):
        while True:
            try:
                devices = await discover()
                for d in devices:
                    if d.name == "GfBT Project":
                        if not await fhem.checkIfDeviceExists(
                            self.hash, "TYPE", "GFPROBT", "MAC", d.address
                        ):
                            self.logger.debug(
                                "create device: "
                                + d.name
                                + " / "
                                + d.address
                                + " / rssi: "
                                + str(d.rssi)
                            )
                            await fhem.CommandDefine(
                                self.hash,
                                d.name
                                + "_"
                                + d.address.replace(":", "")
                                + " GFPROBT '"
                                + d.address
                                + "'",
                            )
                        else:
                            self.logger.debug(
                                "existing device: "
                                + d.name
                                + " / "
                                + d.address
                                + " / rssi: "
                                + str(d.rssi)
                            )
                    elif d.name == "CC-RT-BLE":
                        if not await fhem.checkIfDeviceExists(
                            self.hash, "PYTHONTYPE", "eq3bt", "MAC", d.address
                        ):
                            self.logger.debug(
                                "create device: "
                                + d.name
                                + " / "
                                + d.address
                                + " / rssi: "
                                + str(d.rssi)
                            )
                            await fhem.CommandDefine(
                                self.hash,
                                d.name
                                + "_"
                                + d.address.replace(":", "")
                                + " PythonModule eq3bt '"
                                + d.address
                                + "'",
                            )
                        else:
                            self.logger.debug(
                                "existing device: "
                                + d.name
                                + " / "
                                + d.address
                                + " / rssi: "
                                + str(d.rssi)
                            )
                    elif d.name[0:7] == "Expert_":
                        if not await fhem.checkIfDeviceExists(
                            self.hash, "PYTHONTYPE", "nespresso_ble", "MAC", d.address
                        ):
                            self.logger.debug(
                                "create device: "
                                + d.name
                                + " / "
                                + d.address
                                + " / rssi: "
                                + str(d.rssi)
                            )
                            await fhem.CommandDefine(
                                self.hash,
                                d.name
                                + "_"
                                + d.address.replace(":", "")
                                + " PythonModule nespresso_ble '"
                                + d.address
                                + "'",
                            )
                        else:
                            self.logger.debug(
                                "existing device: "
                                + d.name
                                + " / "
                                + d.address
                                + " / rssi: "
                                + str(d.rssi)
                            )
                    else:
                        self.logger.debug(
                            "found unhandled device: "
                            + d.name
                            + ", "
                            + d.address
                            + ", rssi: "
                            + str(d.rssi)
                        )
            except:
                self.logger.error("BLE Scan failed, retry in 600s", exc_info=True)
            await asyncio.sleep(600)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "active")
        await fhem.readingsEndUpdate(hash, 1)

        if await fhem.AttrVal(self.hash["NAME"], "icon", "") == "":
            await fhem.CommandAttr(self.hash, self.hash["NAME"] + " icon rc_SEARCH")

        if self.blescanTask:
            self.blescanTask.cancel()

        self.blescanTask = asyncio.create_task(self.runBleScan())

        return ""

    # FHEM FUNCTION
    async def Undefine(self, hash):
        if self.blescanTask:
            self.blescanTask.cancel()
        return