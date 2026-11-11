use crate::cpustats::CpuMetrics;
use anyhow::Context;
use reqwest::blocking::Client;

pub(crate) fn senddata(
    cpudata: &CpuMetrics,
    client: &reqwest::blocking::Client,
    endpoint: &str,
) -> anyhow::Result<()> {
    let response = client
        .post(endpoint)
        .json(cpudata)
        .send()?
        .error_for_status()?;
    let status = response.status();
    let body = response.text()?;
    print!("CPU upload: {status}\n{body}");
    anyhow::ensure!(status.is_success(), "CPU upload failed:{status}");
    Ok(())
}
