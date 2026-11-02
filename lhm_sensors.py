import sys
from pathlib import Path

from pythonnet import load

#setup for libreharwaremonitor runtime/dll

load("coreclr")

import clr

DLL_DIR = (
    Path(__file__).resolve().parent
    / "vendor"
    / "librehardwaremonitor"
)


sys.path.append(str(DLL_DIR))
assembly = clr.AddReference(# pyright: ignore[reportAttributeAccessIssue]
    str(DLL_DIR / "LibreHardwareMonitorLib.dll")
)
from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType # pyright: ignore[reportMissingImports]

def get_cpu_temps(comp:Computer)->float|None:
    temps={}
    for hardware in comp.Hardware:
        if hardware.HardwareType!=HardwareType.Cpu:
            continue
        hardware.Update()
        for sensor in hardware.Sensors:
            if sensor.SensorType==SensorType.Temperature:
                name=str(sensor.Name)
                if "TjMax" in name or (not name.startswith(("P-Core #","E-Core #"))):
                    continue
                val=sensor.Value
                temps[str(sensor.Identifier)]=(None if val is None else float(val))
    coll_readings:float=0
    count_readings:int=0
    for k,v in temps.items():
        if v!=None:
            coll_readings+=v
            count_readings+=1

    if count_readings==0:
        return None
    return float(coll_readings/count_readings)
