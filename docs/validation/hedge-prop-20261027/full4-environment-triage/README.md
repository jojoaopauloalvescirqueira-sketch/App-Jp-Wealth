# FULL4 — environment triage

The system did Sleep during FULL4. Five independently corroborated Sleep→DarkWake intervals occurred on2026-10-27 local time:

| Sleep | DarkWake | Literal reason | pmset duration |
|---|---|---|---:|
|14:35:05.191|14:35:08.194|Idle Sleep|3s|
|14:35:18.450|14:35:26.012|Maintenance Sleep|8s|
|14:35:35.026|14:44:17.865|Dark Wake Thermal Emergency|522s|
|14:44:33.707|14:45:07.297|Maintenance Sleep|34s|
|14:45:42.658|14:51:55.385|Maintenance Sleep|373s|

FULL4 wall time was3873s; summed check durations2943.44s; gap929.56s. Rounded pmset sleep durations total940s; power-transition brackets total939.721s. Their proximity strongly supports suspension as the explanation for most of the timing gap. Transition brackets include preparation/wake dispatch, so these totals are not an exact measure of excluded CPU time.

No case-level cause is assigned. The FULL4 receipt lacks per-check wall timestamps. Epoch brokerFor ReferenceError and Alladin I4/I5 click timeout remain open; neither is closed or reclassified by this environmental observation. The literal thermal-emergency reason does not establish a measured temperature or hardware fault.

Evidence is confined to27/10 14:11..15:16local. No test/browser execution, repository edits, process control, VM interaction or energy changes. FULL5 evidence was preserved untouched.
