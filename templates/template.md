# System maintenance report $if(params.name)$for $params.name$$endif$

## Meta information
IP | Date | Time | Owner
-- | ---- | ---- | -----
$if(params.ip)$$params.ip$$endif$ | $if(params.date)$$params.date$$endif$ | $if(params.time)$$params.time$$endif$ | $if(params.owner)$$params.owner$$endif$ |

## Task checklist
Task | Status | Description/Notes
---- | ------ | -----------------
Snapshot created | $if(verification.virt_snapshot)$$verification.virt_snapshot$$endif$ | $if(params.system_physical)$physical system$endif$
Monitoring disabled | $if(verification.mon_downtime)$$verification.mon_downtime$$endif$ | $if(params.environment)$$params.environment$ lifecycle$endif$
System rebooted | $if(verification.system_reboot)$$verification.system_reboot$$endif$ | 
Monitoring status | $if(verification.mon_status)$$verification.mon_status$$endif$ | $if(verification.mon_status_detail)$$verification.mon_status_detail$$endif$
Monitoring enabled | $if(verification.mon_cleanup)$$verification.mon_cleanup$$endif$ | $if(params.environment)$$params.environment$ lifecycle$endif$

## Patch list
Type | Name | Date | Description | Reboot required?
---- | ---- | ---- | ----------- | ----------------
$for(errata)$
$if(errata.type)$$errata.type$$endif$ | $if(errata.errata_id)$$errata.errata_id$$endif$ | $if(errata.issued)$$errata.issued$$endif$ | $if(errata.description)$$errata.description$$endif$ | $if(errata.reboot_suggested)$$errata.reboot_suggested$$endif$
$endfor$

*This report was created automatically by [katprep](https://github.com/stdevel/katprep)*
