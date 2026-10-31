# Planned adapter conformance

The common suite will test claim/resource substitution, episode replay, handoff
invalidation, neighboring-content injection, and unsupported guarantee promotion.
Required negative cases include identity -> location, freshness -> proximity,
and contact report -> consent. Current files specify requirements; no executable
security conformance suite exists yet. Workspace integrity is checked separately
by `scripts/check_workspace.py`.
