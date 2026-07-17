timestamp 2026-07-17 03:30:00
#lastapply no-merge

# Bitcoin Knots 29.3.knots20260717.lts assembly spec
# Assembles the 29.x LTS point release from the previous release tag, using
#   only fixes queued in knots-lts-29.spec (which carries review provenance).
# Companion to knots-lts-29.spec: that file is the full living recipe for the
#   29.x LTS line; this file is the per-release delta, in the style of
#   knots-29.3.knots20260508.spec.
# Assembled with bitcoinknots/assemble-deriv @ 892ab94:
#   assemble-knots.pl -b -o knots-29.3.knots20260717.lts.spec.out \
#     knots-29.3.knots20260717.lts.spec

checkout v29.3.knots20260508
@29.x-knots-lts
# BUILD BUGS:
	k309  pdath/fix-arm-crypto-feature			last=8c7a2f70d33 pdath/fix-arm-crypto-feature
# TESTS:
	k328  privkeyio/ci-test-each-commit-gui-deps			last=c198e9b3586 privkeyio/ci-test-each-commit-gui-deps
# FIXES:
	k298  knots-dev/param_bounds_checks_202604+appleclang			last=a560eda4b06 luke-jr/param_bounds_checks_202604
		# + Apple clang NTTP fix (bare braced-init-list in template args);
		# reported upstream on knots#298
	k330  privkeyio/fix-netwatch-gui-thread-race			last=191d0fdc9e2 privkeyio/fix-netwatch-gui-thread-race
	k331  privkeyio/fix-rpcconsole-wallet-selector-sync			last=accba6a6f88 privkeyio/fix-rpcconsole-wallet-selector-sync
	k329  privkeyio/fix-gen-bitcoin-conf-datadir			last=49db8d133cf privkeyio/fix-gen-bitcoin-conf-datadir
	n/a  (bump_version=knots20260717.lts)
