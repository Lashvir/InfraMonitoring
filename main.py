from typing import Any
from uuid import UUID

from fastapi import FastAPI
from psycopg.rows import dict_row
from pydantic.fields import Field
from pydantic.main import BaseModel
from starlette.exceptions import HTTPException

from database import get_connection
from monitoring.monitoring import monitoring_statistics

app=FastAPI(title="InfraMonitoring", description="The backend for monitoring")

class CpuData(BaseModel):
    name:str|None=None
    load:float|list[float]=Field(description="either load for the cpu or list if/when available")
    times:dict[str,Any]=Field(description="uptimes of cpu, nested dict if data available")
    #temps:float|dict[str,float]=Field(description="temp of cpu, nested dict if per core is available")

class CpuMetricsCreate(BaseModel):
    machine_id:UUID
    cpu_usage:float=Field(ge=0,le=100)
    cpu_temperature:float|None=None

class MachineCreate(BaseModel):
    hostname:str=Field(min_length=1,description="Name of machine")

@app.post("/machines",status_code=201)
def register_machine(machine:MachineCreate):
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO machines (hostname)
            VALUES (%s)
            RETURNING machine_id, hostname
            """,
            (machine.hostname,)
        )
        result=cur.fetchone()
    return result

@app.post("/metrics/cpu")
def handle_data(cpu_data:CpuMetricsCreate):

    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO cpu_metrics (machine_id,cpu_usage,cpu_temperature)
            VALUES (%s,%s,%s)
            RETURNING entry_id,machine_id,cpu_usage,cpu_temperature,recorded_at
            """,
            (cpu_data.machine_id,cpu_data.cpu_usage,cpu_data.cpu_temperature)
        )
        result=cur.fetchone()
    return result;
    #return {"Success":"it passed"}

@app.get("/machines/{machine_id}/cpu/latest")
def get_latest_cpu(machine_id:UUID):
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        result=cur.execute(
            """
            SELECT *
            FROM cpu_metrics
            WHERE machine_id=%s
            ORDER BY recorded_at DESC, entry_id DESC
            LIMIT 1
            """,
            (machine_id,)
        ).fetchone()
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No CPU measurements found"
        )
    return result

def main():
    #monitoring_statistics()
    pass

if __name__ =='__main__':
    main()
