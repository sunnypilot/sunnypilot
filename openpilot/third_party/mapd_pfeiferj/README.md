# MAPD implementation by pfeiferj
https://github.com/pfeiferj/openpilot-mapd/releases/

## Auto SET producer patch (proposal)

The bundled binary uses upstream v1.12.0, commit
`46cd71ade6f630f1564c83bf1763f9d949a9ff30`, plus `auto_set.patch`.
The patch adds `MapSpeedLimitEvidence` v1 in shared-memory params. It preserves
the input position's monotonic `logMonoTime` and atomically publishes the
current matched speed limit. Valid evidence describes provenance/freshness,
not the correctness of a road match or the posted limit.

Reproduce with **Go 1.27.1**, on an isolated source checkout:

```sh
git clone https://github.com/pfeiferj/openpilot-mapd.git
cd openpilot-mapd
git checkout 46cd71ade6f630f1564c83bf1763f9d949a9ff30
git apply /path/to/auto_set.patch
go test -count=1 -v -run TestEvidence ./...
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -trimpath -buildvcs=false \
  -ldflags="-extldflags=-static -s -w" -o mapd .
sha256sum mapd
```

Expected SHA-256:
`335c589bd9c4600728e9de71ccc4532b9c7c88a18d0c58fa1d1cf49278189a7f`.
The repository's `sunnypilot/mapd/tests/mapd_hash` pins this same binary.
Upstream source remains under its MIT license; obtain LICENSE from the fixed
upstream checkout. The patch does not change dependency locks or map matching.

On Windows/amd64 with Go 1.27.1, all five evidence tests pass. Full `go test`
fails `TestVector` and `TestBearing` due to tiny floating-point snapshot
differences; the pristine upstream commit fails the same two tests on this
host. Linux directory fsync, a concurrent Linux reader, and an on-device
producer/consumer run have not been validated here. Full Linux tests remain
required; do not update numerical snapshots to hide these failures.
