# System maintenance report $if(params.name)$for $params.name$$endif$

## Meta information
IP | Date | Time | Owner
-- | ---- | ---- | -----
$if(params.ip)$$params.ip$$endif$ | $if(params.date)$$params.date$$endif$ | $if(params.time)$$params.time$$endif$ | $if(params.owner)$$params.owner$$endif$ |

## Task checklist
Task | Status | Description/Notes
---- | ------ | -----------------
Snapshot created | $if(verification.virt_snapshot)$yes$else$no$endif$ | $if(params.system_physical)$physical system$endif$
Monitoring disabled | $if(verification.mon_downtime)$yes$else$no$endif$ | $if(params.environment)$$params.environment$ lifecycle$endif$
System rebooted | $if(verification.system_reboot)$yes$else$no$endif$ | 
Monitoring status | $if(verification.mon_status)$$verification.mon_status$$endif$ | $if(verification.mon_status_detail)$$verification.mon_status_detail$$endif$
Monitoring enabled | $if(verification.mon_cleanup)$yes$else$no$endif$ | $if(params.environment)$$params.environment$ lifecycle$endif$

## Patch list
Type | Name | Date | Description | Reboot required?
---- | ---- | ---- | ----------- | ----------------
$for(errata)$
$if(errata.type)$$errata.type$$endif$ | $if(errata.summary)$$errata.summary$$endif$ | $if(errata.issued)$$errata.issued$$endif$ | $if(errata.description)$$errata.description$$endif$ | $if(errata.reboot_suggested)$yes$else$no$endif$
$endfor$

*This report was created automatically by [katprep](https://github.com/stdevel/katprep)*
