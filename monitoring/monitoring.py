import platform
import json
from pathlib import Path
from time import sleep
from typing import Any
from uuid import UUID

import psutil
import requests

from lhm_sensors import Computer, get_cpu_temps
from monitoring.conversions import seconds_conversion

BASE_URL="http://127.0.0.1:8001"
prev_temp=None
#Information that is useful->Temperature(track min/max/avg), current load(min/max), uptime
def monitoring_statistics(update_rate:float=2.0)->None:
    #ensure librehardwaremonitor dll/runtimes needs are up and running
    m_id=get_machine_id()
    computer=Computer()
    computer.IsCpuEnabled=True
    computer.IsGpuEnabled=True
    computer.IsMemoryEnabled=True
    try:
        computer.Open()

        while reg_and_auth()==True:
            cpu_statistics(m_id,computer)
            ram_statistics()
            gpu_statistics()
            sleep(update_rate)
    except KeyboardInterrupt:
        pass
    finally:
        computer.Close()


def get_machine_id()->str:
    pc = platform.node() or "Unknown pc"
    f = Path("agent.json")

    try:
        if f.exists():
            with open(f, "r") as file:
                data = json.load(file)
                m_id = data["machine_id"]

               # Verify saved machine ID
            UUID(m_id)
            return m_id

        response = send_payload(
               {"hostname": pc},
               "machines"
            )

        m_id = response.json()["machine_id"]

           # Validate before saving
        UUID(m_id)

        data = {"machine_id": m_id}

        temp_file = f.with_name(f.name + ".tmp")

        with open(temp_file, "w") as file:
            json.dump(data, file)

        temp_file.replace(f)

        return m_id

    except (ValueError, KeyError, TypeError, OSError) as e:
        print(f"Machine ID error: {e}")
        raise

def cpu_statistics(m_id:str,comp:Computer)->None:
    cpu_times=psutil.cpu_times()
    conv_user=seconds_conversion(cpu_times.user)
    conv_sys=seconds_conversion(cpu_times.system)
    conv_idle=seconds_conversion(cpu_times.idle)
    #cpu_load=psutil.cpu_percent(interval=0.1,percpu=True) don't use percpu just yet
    cpu_load=psutil.cpu_percent(interval=0.1)
    # cpu_frequency=psutil.cpu_freq(percpu=True)
    # if len(cpu_frequency)>0: psutil on win 11 does not properly get the frequency
    #     for cpu in cpu_frequency:
    #         print(f"current: {cpu.current}")
    #         print(f"min: {cpu.min}")
    #         print(f"max: {cpu.max}")

    #validate/convert data before sending
    temp_payload:float|None=get_cpu_temps(comp)
    responset=send_payload({
        "machine_id":m_id,
        "cpu_usage":cpu_load,
        "cpu_temperature":temp_payload
    },"metrics/cpu")
    print(responset.status_code)
    print(responset.json())

def prepare_cpu_data(temp:float|None,loads:float|list[float]):
    #if abs(temp_data-prev_temp)>=2:
        # temp_payload=temp_data
    pass

def ram_statistics():
    pass

def gpu_statistics():
    pass

def send_payload(payload:dict[str,Any],folder:str)->requests.Response:
    responseb=requests.post(
        f"{BASE_URL}/{folder}",
        json=payload,
        timeout=5,
    )
    print(responseb.status_code)
    print(responseb.text)
    responseb.raise_for_status()
    return responseb
#will eventually ask backend to register for first time and save the info for future cases
# will also authenticate self later on but for now it will always return true
def reg_and_auth()->bool:
    return True

if __name__ == "__main__":
    monitoring_statistics()
