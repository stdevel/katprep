# System maintenance report $if(hostname)$for $hostname$$endif$

## Meta information
IP | Date | Time | Owner
-- | ---- | ---- | -----
$if(ip)$$ip$$endif$ | $if(date)$$date$$endif$ | $if(time)$$time$$endif$ | $if(owner)$$owner$$endif$ |

## Task checklist
Task | Status | Description/Notes
---- | ------ | -----------------
Snapshot created | $if(system_snapshot)$yes$else$no$endif$ | $if(system_cycle)$$system_cycle$ lifecycle$if(system_physical)$physical system$endif$$endif$
Monitoring disabled | $if(monitoring_disabled)$yes$else$no$endif$ | $if(system_cycle)$$system_cycle$ lifecycle$endif$
System rebooted | $if(system_rebooted)$yes$else$no$endif$ | 
Monitoring status | $if(monitoring_status)$$monitoring_status$$endif$ | $if(monitoring_status_detail)$$monitoring_status_detail$$endif$
Monitoring enabled | $if(monitoring_enabled)$$monitoring_enabled$$endif$ | $if(system_cycle)$$system_cycle$ lifecycle$endif$

## Patch list
Type | Name | Date | Description | Reboot required?
---- | ---- | ---- | ----------- | ----------------
$for(patch)$
$if(patch.errata_type)$$patch.errata_type$$endif$ | $if(patch.errata_name)$$patch.errata_name$$endif$ | $if(patch.errata_date)$$patch.errata_date$$endif$ | $if(patch.errata_desc)$$patch.errata_desc$$endif$ | $if(patch.errata_reboot)$yes$else$no$endif$
$endfor$

*This report was created automatically by [katprep](https://github.com/stdevel/katprep)*
