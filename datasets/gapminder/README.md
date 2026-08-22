# Gapminder example workspace

This workspace downloads an immutable snapshot of the Gapminder teaching
table and produces the `gapminder.development` Silver dataset.

The workspace contains configuration only. Runtime data, receipts, manifests,
and projections are created below `data/` and `logs/`; both directories are
ignored by Git so pipeline execution does not make the provenance checkout
dirty.

The Silver contract deliberately performs only transparent transformations:
it gives the six source columns descriptive published names and casts them to
explicit string, integer, and floating-point types.
