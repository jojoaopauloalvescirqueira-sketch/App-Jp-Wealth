# Chrome closure triage — FULL3

Observed cause: macOS Dock sent a Quit AppleEvent to Chrome at14:02:25.433 local. Chrome received it at.434, handled and approved quit at.440; the first browser TargetClosedError finished at.475887. Further Dock Quit requests followed at14:02:29.730,35.750 and43.518. Chrome exit handler ran at14:02:50.385.

The trace supports an externally requested orderly browser shutdown. The human or automation that triggered Dock is unknown. No matching Chrome/chromium/memory/jetsam DiagnosticReports were found for today. The current memory snapshot is after the event and cannot prove or exclude prior pressure.

FULL2 and FULL3 checker receipts use the same153-entry source hash map, the same checker SHA, and browser156.0.8078.48. FULL2 has413 PASS cases; FULL3 stopped after48 recorded cases. The same month-context case passed in FULL2. Earlier PASS does not replace the red receipt.

Current Chrome62605 is PPID1 with only the executable in its command, consistent with regular UI rather than the expected headless/debug flags. Dashboard child62603 and Playwright driver62604 remain separately controlled by the active FULL. No intervention performed. Bundle directory/plist timestamps changed around14:02:05, but identical browser version and timestamps alone do not establish an update.

Raw relevant OS metadata: `os-quit-events.txt`, `os-chrome-start.txt`. Receipt excerpts, comparison, limits and next safe verification: `triage.json`.

Only this scratch directory was written. No browser launch, test, generator, Git mutation, process kill, application/test edit, browser profile/history read or VM interaction was performed.

Coordination update from root: user confirmed Chrome closure/restart around14:02. Root reports preserving incomplete FULL3 exit-2, stopping only owned test processes, and obtaining authorization for a fresh quiet focal/FULL4 run without app/checker edits. These coordination actions are root-reported, not executed or independently reverified by this subagent.
