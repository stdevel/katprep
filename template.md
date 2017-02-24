# System maintenance report for @hostname@

## Meta information
|:----|:-----|:------|:-------|:------|:------|
| IP: | @ip@ | Date: | @date@ | Time: | @time |
| Owner: | @owner@ | | | | |

## Checklist
|:-----|:-------|:------------------|
| **Task** | **Status** | **Description/Notes** |
| Snapshot created | @vlog_snapshot_created@ | @host_status@ |
| Monitoring disabled | @vlog_monitoring_disabled@ | @host_status@ |
| System rebooted | @vlog_reboot@ | @patch_reboot@ |
| Monitoring status | @vlog_monitoring_status@ | @vlog_monitoring_status_detail@ |
| Monitoring enabled | @vlog_monitoring_enabled@ | @host_status@ |

## Patch list
<!--
## This is just a comment
-->
|:---------|:---------|:---------|:----------------|:--------------------|
| **Type** | **Name** | **Date** | **Description** | **Reboot required** |
| @errata_type@ | @errata_name@ | @errata_date@ | @errata_desc@ | @errata_reboot@ |

