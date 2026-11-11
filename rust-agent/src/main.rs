use anyhow::Context;
use reqwest::blocking::Client;
use serde::{Deserialize, Serialize};
use sysinfo::System;

use crate::cpustats::collect_cpu_stats;
use crate::senddata::senddata;
use std::{
    fs::{self, File},
    io::{ErrorKind::NotFound, Write},
    path::Path,
    thread, time,
};
use uuid::Uuid;
mod cpustats;
mod senddata;
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
struct AgentConfig {
    pub machine_id: uuid::Uuid,
}
#[derive(Serialize)]
struct RegPayload {
    hostname: String,
}

const CPU_POST_ENDPOINT: &str = "/metrics/cpu";
const BACKEND_LINK: &str = "http://127.0.0.1:8001";

fn main() -> anyhow::Result<()> {
    let hname_os = hostname::get()?;
    let hname = hname_os.to_string_lossy().into_owned();
    let client = Client::builder()
        .timeout(std::time::Duration::from_secs(3))
        .build()?;
    let p = Path::new("agent.json");
    let m_id = get_machine_id(&client, p, hname)?;
    let machine_unique: AgentConfig = AgentConfig { machine_id: m_id };
    let mut system = System::new()?;
    system.refresh_all();
    let refresh_rate = time::Duration::from_secs(2);
    println!("Monitoring machine: {m_id}");
    let temp_url_string = format!("{BACKEND_LINK}{CPU_POST_ENDPOINT}");
    loop {
        //collect cpu/gpu/netword/relevant data
        thread::sleep(refresh_rate);
        let cpu_data = collect_cpu_stats(&mut system, &machine_unique);

        senddata(&cpu_data, &client, &temp_url_string);
        print!("{cpu_data:?}")
    }
}

fn get_machine_id(
    client: &reqwest::blocking::Client,
    config_path: &std::path::Path,
    hname: String,
) -> anyhow::Result<uuid::Uuid> {
    match fs::read_to_string(config_path) {
        Ok(json_str) => {
            let config: AgentConfig =
                serde_json::from_str(&json_str).context("Failed to parse saved agent config")?;
            Ok(config.machine_id)
        }
        Err(e) if e.kind() == NotFound => {
            let payload = RegPayload { hostname: hname };
            let config = register_machine(client, &payload)?;

            save_config_data(config_path, &config)?;
            Ok(config.machine_id)
        }

        Err(e) => Err(e).with_context(|| {
            format!(
                "Failed to read agent configuration at {}",
                config_path.display()
            )
        }),
    }
}
fn save_config_data(target_path: &Path, config: &AgentConfig) -> anyhow::Result<()> {
    let tmp_path = target_path.with_extension("json.tmp");
    let json_bytes = serde_json::to_vec(config)?;
    {
        let mut tmp_file = File::create(&tmp_path)?;
        tmp_file.write_all(&json_bytes)?;
        tmp_file.sync_all()?;
    }
    fs::rename(&tmp_path, target_path)?;
    Ok(())
}
fn register_machine(
    client: &reqwest::blocking::Client,
    payload: &RegPayload,
) -> anyhow::Result<AgentConfig> {
    let registration_url = format!("{}/machines", BACKEND_LINK.trim_end_matches('/'));
    let response = client
        .post(registration_url)
        .json(&payload)
        .send()
        .context("Failed to send machine reg. request")?
        .error_for_status()
        .context("Backend rejected machine reg.")?;
    Ok(response.json::<AgentConfig>()?)
}
