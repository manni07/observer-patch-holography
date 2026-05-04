# Particle Root Integration Gate Packet

## Scope

Integrate returned bundle packets and decide whether live prediction roots may
change.

## Required Result

Return `promote` only if the endpoint, RG/matching, interval, hadronic, and
spectrum-source gates all close. Otherwise return `keep_candidate` and list the
next coupled bundle revision.

Default decision: `keep_candidate`.

## Integration Result

Pending.
