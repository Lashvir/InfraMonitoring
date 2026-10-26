import platform
from time import sleep
from typing import Any

import psutil
import requests
from urllib3.util import response

from monitoring.conversions import seconds_conversion

BASE_URL="http://127.0.0.1:8001"

#Information that is useful->Temperature(track min/max/avg), current load(min/max), uptime
def monitoring_statistics()->None:
    update_rate=2
    while reg_and_auth()==True:
        cpu_statistics()
        ram_statistics()
        gpu_statistics()
        sleep(update_rate)

def cpu_statistics()->None:
    #cpu_stats=psutil.cpu_stats()
    cpu_times=psutil.cpu_times()
    pc=platform.processor() or "Unknown cpu"
    print(f"cpu used: {pc}")

    print(f"user: {cpu_times.user}")
    conv_user=seconds_conversion(cpu_times.user)
    print(f"user conv: {conv_user}")
    #print(f"nice:{cpu_times.nice}") linux only
    print(f"system: {cpu_times.system}")
    conv_sys=seconds_conversion(cpu_times.system)
    print(f"system conv: {conv_sys}")
    print(f"idle:{cpu_times.idle}")
    conv_idle=seconds_conversion(cpu_times.idle)
    print(f"idle conv: {conv_idle}")
    #cpu_load=psutil.cpu_percent(interval=0.1,percpu=True) don't use percpu just yet
    cpu_load=psutil.cpu_percent(interval=0.1)
    print(f"Cpu load: {cpu_load}%")
    # cpu_frequency=psutil.cpu_freq(percpu=True)
    # if len(cpu_frequency)>0: psutil on win 11 does not properly get the frequency
    #     for cpu in cpu_frequency:
    #         print(f"current: {cpu.current}")
    #         print(f"min: {cpu.min}")
    #         print(f"max: {cpu.max}")

    #validate/convert data before sending
    responset=send_payload({
        "name":pc,
        "load":cpu_load,
        "times":{"user":conv_user,"system":conv_sys}
    },"cpu")
    print(responset.status_code)
    print(responset.json())

def ram_statistics():
    pass

def gpu_statistics():
    pass

def send_payload(payload:dict[str,Any],folder:str)->requests.Response:
    responseb=requests.post(
        f"{BASE_URL}/metrics/{folder}",
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
