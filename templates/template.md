# System maintenance report $if(params.name)$for $params.name$$endif$

## Meta information

Hostname | Date | Time | Owner
-- | ---- | ---- | -----
$if(hostname)$$hostname$$endif$ | $if(date)$$date$$endif$ | $if(time)$$time$$endif$ | $if(params.katprep_owner)$$params.katprep_owner$$endif$ |

## Task checklist

Task | Status | Description/Notes
---- | ------ | -----------------
Snapshot created | $if(verification.virt_snapshot)$$verification.virt_snapshot$$endif$ | $if(params.system_physical)$physical system$endif$
Monitoring disabled | $if(verification.mon_downtime)$$verification.mon_downtime$$endif$ | $if(params.environment)$$params.environment$ lifecycle$endif$
System rebooted | $if(verification.system_reboot)$$verification.system_reboot$$endif$ | 
Monitoring status | $if(verification.mon_status)$$verification.mon_status$$endif$ | $if(verification.mon_status_detail)$$verification.mon_status_detail$$endif$
Monitoring enabled | $if(verification.mon_cleanup)$$verification.mon_cleanup$$endif$ | $if(params.environment)$$params.environment$ lifecycle$endif$

## patches list

Type | Name | Date | Description | Reboot required?
---- | ---- | ---- | ----------- | ----------------
$for(patches)$
$if(patches.type)$$patches.type$$endif$ | $if(patches.name)$$patches.name$$endif$ | $if(patches.issued_at)$$patches.issued_at$$endif$ | $if(patches.summary)$$patches.summary$$endif$ | $if(patches.reboot_suggested)$$patches.reboot_suggested$$endif$
$endfor$

*This report was created automatically by [katprep](https://github.com/stdevel/katprep)*
