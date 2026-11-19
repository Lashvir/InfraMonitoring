use serde::Serialize;

pub(crate) fn senddata<T: Serialize>(
    payload: &T,
    client: &reqwest::blocking::Client,
    endpoint: &str,
) -> anyhow::Result<()> {
    let response = client.post(endpoint).json(payload).send()?;
    let status = response.status();
    let body = response.text()?;
    print!("CPU upload: {status}\n{body}");
    anyhow::ensure!(status.is_success(), "CPU upload failed:{status}");
    Ok(())
}
