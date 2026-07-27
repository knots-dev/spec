# Case study: a dev-testing LTS process for Bitcoin Knots 29.x

This documents a working prototype of an LTS maintenance process for Knots,
run in the [knots-dev](https://github.com/knots-dev/bitcoin) org. It is
**not** an official LTS release. The goals:

1. Demonstrate what a good LTS candidate release looks like: baseline,
   inclusion criteria, verification, provenance.
2. Give other devs a stable, fixes-only build to run before changes ship
   upstream.
3. Feed everything learned (including bugs caught) back into the real Knots
   release process.

## The baseline

[`29.x-knots-lts`](https://github.com/knots-dev/bitcoin/tree/29.x-knots-lts)
starts at the `v29.3.knots20260508` release commit
([`f41f01e1e6d`](https://github.com/knots-dev/bitcoin/commit/f41f01e1e6de7025d52a865bef97f2a67277f0f3)),
bit-identical, zero deviation. Tagged
[`v29.3.knots20260508.lts`](https://github.com/knots-dev/bitcoin/releases/tag/v29.3.knots20260508.lts).

## Relationship to 29.4

This is a working preview of the upcoming fixes-only release,
`29.4.knots20260508`. The `knots<YYYYMMDD>` datestamp is pinned to the feature
collection, so a fixes-only release keeps `20260508` and bumps the minor
(`.3` -> `.4`) to signal that fixes have accumulated on the same features.
Under that convention this preview corresponds to `29.4.knots20260508`; the
prototype's build-dated `.knots20260717.lts` tag is a stand-in until 29.4
formally lands, at which point the LTS baseline moves to it and keeps
accumulating fixes.

## Inclusion criteria

All fixes, not just critical ones: upstream Core bugfix backports and
Knots-specific fixes. No features. Default-policy updates are in scope per dev
consensus (spam-filter defaults are volatile), pending a firm ruling. The
inclusion list defers to the maintainer's curated fixes collection, the `29.4`
milestone, rather than our own critical/not-critical judgment. Each fix still
carries review provenance (maintainer, dev team, or tested ACK) with no
unresolved findings; bot approvals do not count. The queue lives in
[`knots-lts-29.spec`](https://github.com/knots-dev/spec/blob/knots-spec/knots-lts-29.spec)
with the provenance recorded as a comment on each line.

This prototype run assembled six fixes to prove the pipeline; under the
all-fixes rule the queue expands to the full `29.4` milestone (currently 10
open PRs, four of which are already in the six below).

First prototype build,
[`v29.3.knots20260717.lts`](https://github.com/knots-dev/bitcoin/releases/tag/v29.3.knots20260717.lts)
(six fixes):

| PR | Fix | Review basis |
|----|-----|--------------|
| [knots#309](https://github.com/bitcoinknots/bitcoin/pull/309) | ARM crypto extensions build detection | tACK x2 (tested) + ACK |
| [knots#298](https://github.com/bitcoinknots/bitcoin/pull/298) | Bounds checks for bytespersigop/maxscriptsize/limit*size | maintainer-authored + crACK |
| [knots#330](https://github.com/bitcoinknots/bitcoin/pull/330) | GUI/NetWatch heap corruption | tACK (tested) |
| [knots#331](https://github.com/bitcoinknots/bitcoin/pull/331) | RPC console wallet selector sync | ACK |
| [knots#329](https://github.com/bitcoinknots/bitcoin/pull/329) | gen-bitcoin-conf.sh datadir | ACK |
| [knots#328](https://github.com/bitcoinknots/bitcoin/pull/328) | CI GUI deps for test-each-commit | ACK |

Every merged head was verified byte-identical to the commit hash that was
ACK'd on the PR.

## Two assembly paths, one tree

The release was produced two independent ways:

1. **Branch way**: fixes merged onto the previous release tag in spec order,
   signed merge commits, version bump last. Published as
   [`29.x-knots-lts`](https://github.com/knots-dev/bitcoin/tree/29.x-knots-lts)
   (head [`c9c7b75b7e7`](https://github.com/knots-dev/bitcoin/commit/c9c7b75b7e75747188918451de216deab3cb1059)).
2. **Spec way**:
   [`knots-29.3.knots20260717.lts.spec`](https://github.com/knots-dev/spec/blob/knots-spec/knots-29.3.knots20260717.lts.spec)
   (same grammar and naming as
   [`knots-29.3.knots20260508.spec`](https://github.com/luke-jr/tmp/blob/knots-spec/knots-29.3.knots20260508.spec))
   run through unmodified `assemble-knots.pl`
   ([bitcoinknots/assemble-deriv @ 892ab94](https://github.com/bitcoinknots/assemble-deriv/tree/892ab94e9ca71d11af07155daf43a398720ce43e)).
   Zero conflicts, zero autoresolvers. Published as
   [`29.x-knots-lts.spec-assembled`](https://github.com/knots-dev/bitcoin/tree/29.x-knots-lts.spec-assembled)
   (head [`ec1b21b81c`](https://github.com/knots-dev/bitcoin/commit/ec1b21b81c94314c75427b29788ac4c27c693253)).

Both produce **tree `670aca2d74f`**, identical to the byte. The spec file
with the tool-recorded applied hashes lives in the spec repo
(knots-dev/spec).

## Verification

- Full build, GCC 13 and clang 18, GUI and tests on (`-DRDTS_CONSENT=IMPLICIT`)
- `test_bitcoin`: no errors; `test_bitcoin-qt`: all pass
- Functional: mempool_limit, feature_config_args, mempool_packages, rpc_help
- Direct behavioral checks on the bounds fix: negative and beyond-int64/multiplier
  values for bytespersigop, maxscriptsize, limitancestorsize,
  limitdescendantsize all produce clean startup errors
- Full [CI matrix](https://github.com/knots-dev/bitcoin/actions) on the
  published branch
- Guix reproducible builds of the tag for x86_64, aarch64, and riscv64
  (all Linux), covered by a single GPG-signed `SHA256SUMS.asc`. Attestation
  collected in
  [knots-dev/guix.sigs](https://github.com/knots-dev/guix.sigs/tree/knots/29.3.knots20260717.lts)
  (fork of bitcoinknots/guix.sigs). The x86_64 build has a second independent
  attestation (pdath) reaching the same hash, so that arch is multi-party
  reproducible; aarch64/riscv64 await a second builder.

## What the process caught on day one

The first CI run failed on both macOS jobs:
[knots#298](https://github.com/bitcoinknots/bitcoin/pull/298) uses a bare
braced-init-list as a non-type template argument, which GCC and clang 18
accept but clang 16 (the documented minimum supported clang, and what Apple
clang ships) rejects, verified directly on clang 16.0.0. The same jobs, plus
"No wallet, libbitcoinkernel" (which pins clang-16), were already red on the
upstream PR, but the logs had expired and the failure was undiagnosed.

The LTS process reproduced it with fresh logs, diagnosed it, fixed it
downstream
([`param_bounds_checks_202604+appleclang`](https://github.com/knots-dev/bitcoin/tree/param_bounds_checks_202604%2Bappleclang),
carried as a "PR + local fix" branch exactly as the spec grammar supports),
verified the bounds behavior still holds, and
[reported the diagnosis and fix upstream](https://github.com/bitcoinknots/bitcoin/pull/298#issuecomment-4998447487)
on knots#298. That is the intended loop: catch, fix, verify, feed upstream.

## Running it on StartOS (Start9)

Sideloadable StartOS packages are attached to the release for x86_64, aarch64,
and riscv64 (see Downloads). Each package's Docker build downloads the
guix-attested LTS release tarball for its arch, verifies the signed
`SHA256SUMS.asc` against the pinned guix key, checks the tarball hash, and ships
that exact binary, so the package runs the same reproducible build this case
study describes. Source:
[knots-dev/bitcoin-knots-startos @ `lts`](https://github.com/knots-dev/bitcoin-knots-startos/tree/lts).
It installs as its own `#knotslts` flavor, so it will not disturb an existing
Knots install. aarch64 covers typical arm64 Start9 boxes. Dev-testing only.

To package a StartOS build yourself, you can follow step 5 of
[this reproduce-and-build-your-own-Knots guide](https://github.com/chrisguida/knots-assembly/pull/2).

## Downloads

Release: <https://github.com/knots-dev/bitcoin/releases/tag/v29.3.knots20260717.lts>

| Artifact | sha256 |
|----------|--------|
| [bitcoin-29.3.knots20260717.lts-x86_64-linux-gnu.tar.gz](https://github.com/knots-dev/bitcoin/releases/download/v29.3.knots20260717.lts/bitcoin-29.3.knots20260717.lts-x86_64-linux-gnu.tar.gz) (guix binary) | `0625e7346b87f7c64d90a2c6f3a5c3be618db488cacaaf8b94c13a2a9291d986` |
| [bitcoin-29.3.knots20260717.lts.tar.gz](https://github.com/knots-dev/bitcoin/releases/download/v29.3.knots20260717.lts/bitcoin-29.3.knots20260717.lts.tar.gz) (source) | `c188018f8f998c5e554d26244948f2a0b58945bd5ed229fcc696db37f834ae02` |
| [bitcoin-29.3.knots20260717.lts-aarch64-linux-gnu.tar.gz](https://github.com/knots-dev/bitcoin/releases/download/v29.3.knots20260717.lts/bitcoin-29.3.knots20260717.lts-aarch64-linux-gnu.tar.gz) (guix binary) | `a282dd7a6774e07166c246c0ad90d632e9c3f4ddfc9a158f40c75c9138dd6fd9` |
| [bitcoin-29.3.knots20260717.lts-riscv64-linux-gnu.tar.gz](https://github.com/knots-dev/bitcoin/releases/download/v29.3.knots20260717.lts/bitcoin-29.3.knots20260717.lts-riscv64-linux-gnu.tar.gz) (guix binary) | `083a2011e443ed4afa878840d1459d5e23500eeeb77ebd7ba03eb78ee56c3687` |
| [bitcoind_x86_64.s9pk](https://github.com/knots-dev/bitcoin/releases/download/v29.3.knots20260717.lts/bitcoind_x86_64.s9pk) (StartOS) | `107c8efae418e605abbb2393d123b5064f20b62d4afb133c2e8081fd564c37e9` |
| [bitcoind_aarch64.s9pk](https://github.com/knots-dev/bitcoin/releases/download/v29.3.knots20260717.lts/bitcoind_aarch64.s9pk) (StartOS) | `6a878b9cc6159400921cd508f94d4edd3a25a418864d7f285887b386d7edff7a` |
| [bitcoind_riscv64.s9pk](https://github.com/knots-dev/bitcoin/releases/download/v29.3.knots20260717.lts/bitcoind_riscv64.s9pk) (StartOS) | `f986920e7a1743dbc8a9925f7c3204f22d0dd40ee14fb18a186a2a7a049a4bf0` |
| [SHA256SUMS](https://github.com/knots-dev/bitcoin/releases/download/v29.3.knots20260717.lts/SHA256SUMS) / [SHA256SUMS.asc](https://github.com/knots-dev/bitcoin/releases/download/v29.3.knots20260717.lts/SHA256SUMS.asc) | guix attestation (key `A47D99B6...A7E24E38`) |

## Known gaps (deliberate, documented)

- knots#298 ships with a 6-line downstream fix the maintainer has not yet
  reviewed (reported upstream; will be swapped for the upstream version when
  the PR updates).
- The s9pk Dockerfile verifies the release `SHA256SUMS.asc` against the single
  release-signer key (quorum 1) as a download-integrity check, not as the
  reproducibility proof. Multi-party reproducibility lives in guix.sigs (where
  independent builders attest), by design; the package would only need a
  higher quorum if we wanted it to enforce N-of-M signatures at install time,
  which would require attaching a multi-signed SHA256SUMS to the release.
- Guix builds cover x86_64/aarch64/riscv64 Linux. x86_64 has two independent
  attestations (kwsantiago + pdath) reaching the same hash; aarch64 and riscv64
  are still single-signer until a second builder reproduces them. Binaries are
  for dev testing only.
- The six prototype fixes were hand-picked to exercise the pipeline; the real
  line's scope is the maintainer's `29.4` milestone, so inclusion judgment
  moves off us and onto Luke's curated list.

## Replicating

### Reproduce the guix binaries

```
git clone https://github.com/knots-dev/bitcoin
cd bitcoin && git checkout v29.3.knots20260717.lts
HOSTS="x86_64-linux-gnu aarch64-linux-gnu riscv64-linux-gnu" ./contrib/guix/guix-build

# release tarballs only (the *gnu.tar.gz glob excludes the -debug ones)
sha256sum guix-build-*/output/*/*gnu.tar.gz
```

Expected: `0625e73...` (x86_64), `a282dd7a...` (aarch64), `083a2011...` (riscv64),
matching the release `SHA256SUMS`. To contribute an attestation, run
`contrib/guix/guix-attest` and send the resulting
`noncodesigned.SHA256SUMS{,.asc}` for inclusion in
[knots-dev/guix.sigs](https://github.com/knots-dev/guix.sigs).

### Reproduce the assembly

The assembler resolves every branch, PR head, and the base release tag by name,
and it does not fetch anything unless given `-f`, so all refs must exist first.

```
git clone --recurse-submodules https://github.com/knots-dev/spec   # assemble-knots.pl + specs
git clone https://github.com/knots-dev/bitcoin
cd bitcoin

# forks the spec merges from, plus bitcoinknots (base release tag) and Core (master)
for r in pdath luke-jr privkeyio knots-dev bitcoinknots; do
  git remote add $r https://github.com/$r/bitcoin
done
git remote add core https://github.com/bitcoin/bitcoin

# PR heads: each k<N> line is checked against origin-pull-k/<N>/head
git remote add origin-pull-k https://github.com/bitcoinknots/bitcoin
git config remote.origin-pull-k.fetch '+refs/pull/*/head:refs/remotes/origin-pull-k/*/head'

git fetch --all --tags              # branches, PR heads, and the base release tag
git branch -f master core/master    # the poison check needs a local Core master

../spec/assemble-knots/assemble-knots.pl -b -o out.spec \
    ../spec/knots-29.3.knots20260717.lts.spec
git rev-parse NEW_29.x-knots-lts^{tree}   # 670aca2d74f
```

Verified from a clean clone: `COMPLETE`, no conflicts, no autoresolvers.
