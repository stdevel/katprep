# System maintenance report $if(params.name)$for $params.name$$endif$

## Meta information
IP | Date | Time | Owner
-- | ---- | ---- | -----
$if(params.ip)$$params.ip$$endif$ | $if(params.date)$$params.date$$endif$ | $if(params.time)$$params.time$$endif$ | $if(params.owner)$$params.owner$$endif$ |

## Task checklist
Task | Status | Description/Notes
---- | ------ | -----------------
Snapshot created | $if(params.system_snapshot)$yes$else$no$endif$ | $if(params.system_physical)$physical system$endif$
Monitoring disabled | $if(monitoring_disabled)$yes$else$no$endif$ | $if(params.environment)$$params.environment$ lifecycle$endif$
System rebooted | $if(params.system_rebooted)$yes$else$no$endif$ | 
Monitoring status | $if(params.monitoring_status)$$params.monitoring_status$$endif$ | $if(params.monitoring_status_detail)$$params.monitoring_status_detail$$endif$
Monitoring enabled | $if(params.monitoring_enabled)$$params.monitoring_enabled$$endif$ | $if(params.environment)$$params.environment$ lifecycle$endif$

## Patch list
Type | Name | Date | Description | Reboot required?
---- | ---- | ---- | ----------- | ----------------
$for(errata)$
$if(errata.type)$$errata.type$$endif$ | $if(errata.summary)$$errata.summary$$endif$ | $if(errata.issued)$$errata.issued$$endif$ | $if(errata.description)$$errata.description$$endif$ | $if(errata.reboot_suggested)$yes$else$no$endif$
$endfor$

*This report was created automatically by [katprep](https://github.com/stdevel/katprep)*
