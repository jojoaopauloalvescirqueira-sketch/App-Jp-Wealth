# FULL6 — final bounded environment receipt

Full window inspected:28/10/2026 10:21:39..11:15:25local. No matching powerd/pmset Sleep/Wake events and no Chrome-relevant Quit/force-quit markers. All diagnostic commands exited0.

Guard84806 was confirmed active in the earlier11:11:42 live reading and in historical assertions at10:22,10:37,10:52 and11:07. At11:15:24, pmset records ClientDied releasing both PreventUserIdleSystemSleep and PreventUserIdleDisplaySleep, age53m45s. This matches root-reported supervisor/gate completion. At11:17:53 ps finds no supervisor84802, guard84806 or gate84808; pmset no longer lists84806. The sequence corroborates the expected automatic release at supervisor completion.

The observed protection consisted of temporary process-owned assertions. No permanent energy change was performed by this investigation; persistent settings were not separately audited before/after. Other processes still held a global idle-system assertion afterward, which does not mean84806 remained alive.

Root reports FULL6 exit0/116PASS at11:15:24. The approximately320s Download latency remains without an identified cause. Earlier latency triage is preserved unchanged; PASS does not establish its cause.

Only this scratch directory written. No tests, browser, protocol calls, process signals/control, repository edits, VM interaction or power modification.
