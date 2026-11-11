use serde::Serialize;

use crate::AgentConfig;

// use sysinfo::MINIMUM_CPU_UPDATE_INTERVAL;

#[derive(Debug, Serialize)]
pub(crate) struct CpuMetrics {
    machine_id: uuid::Uuid,
    load_avg_perc: Option<f32>,
    load_max_perc: Option<f32>,
    temp_avg: Option<f32>,
    temp_max: Option<f32>,
}

pub(crate) fn collect_cpu_stats(
    system: &mut sysinfo::System,
    machine_id: &AgentConfig,
) -> CpuMetrics {
    system.refresh_cpu_usage();
    let list_cpus = system.cpus();
    let mut max_load: Option<f32> = None;
    let mut sum_load: f32 = 0.0_f32;
    for cpu in list_cpus {
        let usage = cpu.usage();
        sum_load += usage;
        max_load = Some(match max_load {
            Some(previous_max) => previous_max.max(usage),
            None => usage,
        });
    }
    let avg_load = if list_cpus.is_empty() {
        None
    } else {
        Some(sum_load / list_cpus.len() as f32)
    };

    CpuMetrics {
        machine_id: machine_id.machine_id,
        load_avg_perc: avg_load,
        load_max_perc: max_load,
        temp_avg: None,
        temp_max: None,
    }
}
