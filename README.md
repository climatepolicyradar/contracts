# contracts

Canonical model definitions for `Document` and `Label`, shared across the stack.

**Pydantic is the source of truth.** An OpenAPI 3.1 doc, TypeScript types, and dbt schema YAML are generated from it — not hand-authored.

```
src/cpr_contracts/models.py     ← edit models here
src/cpr_contracts/registry.py   ← register new models here
        │
        ├── schemas/openapi.yaml          (generated, committed — drives TS + breaking-change checks)
        │       └── typescript/src/index.ts (generated, committed)
        │
        └── dbt/{contract}.yml            (generated, committed — for Snowflake dbt consumers)
```

## Quick start

```bash
just install   # Python venv + npm deps
just generate  # regenerate every artifact after editing models
just test      # run tests (includes openapi sync check)
```

## Consuming in Python

```bash
pip install git+https://github.com/climatepolicyradar/contracts
```

```python
from cpr_contracts import Document, Label

doc = Document(
    id="doc1",
    title="UK Climate Change Act 2008",
    labels=[Label(id="l1", name="Energy", type="sector")],
)
```

## Consuming in TypeScript

```bash
npm install @climatepolicyradar/contracts
```

```typescript
import type { Document, Label } from "@climatepolicyradar/contracts";
```

## Consuming in Snowflake (dbt)

This repo publishes a dbt-format `schema.yml` block per versioned model under `dbt/`:

```
dbt/documents.yml   →  document_v1
```

Each file is a complete dbt schema entry. Versioned filenames (`_v1`, `_v2`, …) let multiple contract versions co-exist if a consumer needs to migrate gradually.

### How dbt picks it up

dbt automatically merges every `*.yml` file under `models/` — there is no `include` directive. Integration is "drop the file in".

### Setup

In the consuming dbt project, add a CI step that fetches the contract from a pinned tag:

```yaml
- name: Sync contracts contract
  run: |
    curl -fsSL \
      -o snowflake_models/models/published/_documents.yml \
      https://raw.githubusercontent.com/climatepolicyradar/contracts/v1.0.0/dbt/documents.yml
    git diff --exit-code
```

Then:

1. Commit `_documents.yml` to the consuming repo. The underscore prefix is a convention to flag generated files — do not edit by hand.
2. Make sure no other `schema.yml` in the same directory defines the same model name (a model can only be declared once).
3. The `git diff --exit-code` step fails CI if the committed file drifts from the pinned tag, surfacing version bumps as visible PRs.

### Enforcement

Provided the consuming dbt project has `enforced: true` on contracts, dbt will fail at deploy time if Snowflake's columns or types don't match the YAML. The generated file becomes the cross-stack guardrail.

### Bumping versions

When a new release is cut here, the consuming project updates the pinned tag in their CI step (`v1.0.0` → `v1.1.0`), reruns, and commits the new file.

## Changing the models

**Editing an existing field** — one file:
1. Edit `src/cpr_contracts/models.py`
2. Commit using a [Conventional Commit](https://www.conventionalcommits.org/) message (`feat:`, `fix:`, `feat!:`)
3. Push

**Adding a new model** — three files:
1. Define the model in `src/cpr_contracts/models.py`
2. Register it in `src/cpr_contracts/registry.py` (add to an existing `Contract` or create a new one)
3. Export it from `src/cpr_contracts/__init__.py`
4. Commit and push

You don't *need* to run `just generate` locally — CI regenerates the schema, dbt YAML, and TypeScript types and **auto-commits the result back to your PR branch** as a follow-up `chore: regenerate artifacts` commit. If you'd rather review the diff before push, run `just generate` locally.

CI auto-commit only works on PRs from this repo. PRs from forks (and direct pushes to `main`, which shouldn't happen) fail the build with instructions to regenerate locally.

## Releases

[release-please](https://github.com/googleapis/release-please) handles versioning. Every push to `main` updates a long-lived "release PR" that bumps the version in `pyproject.toml`, `typescript/package.json`, and `src/cpr_contracts/__init__.py` based on the Conventional Commits since the last release. Merging the release PR cuts a tag and a GitHub Release.

### Merge strategy

The repo is configured for **squash merge only**, with the squash commit message defaulting to the PR title (the body is dropped). That means:

- The PR title — already linted to a Conventional Commit by [lint-pr.yml](.github/workflows/lint-pr.yml) — *is* the commit message on `main`.
- release-please reads commits on `main` directly, so the linted PR title flows straight into version bump decisions and the changelog.
- Bot follow-up commits like `chore: regenerate artifacts` get collapsed into the single squash commit, keeping `main`'s history one-PR-one-commit.

| Commit / PR title prefix | Effect |
|---|---|
| `fix:` | Patch bump |
| `feat:` | Minor bump |
| `feat!:` / `fix!:` (or any `BREAKING CHANGE:` footer) | Major bump |

Only `feat:` and `fix:` are allowed — enforced via the PR-title lint (`amannn/action-semantic-pull-request`). Adding `!` to either flags a breaking change.

Major bumps stay significant — they require explicit `!` syntax or a `BREAKING CHANGE:` footer, and the release PR is reviewed and merged manually.

### Breaking-change validation

On every pull request, [oasdiff](https://github.com/oasdiff/oasdiff) classifies the schema delta as **major / minor / none** by diffing `schemas/openapi.yaml` against the base branch. The `semver-classification` workflow:

1. Posts a sticky PR comment with the detected level and a list of changes (~100 categories: removed fields, type narrowing, required-flips, enum removal, constraint tightening, `additionalProperties` flips, recursive sub-schema changes…)
2. **Fails the build** if oasdiff detects breaking changes *and* none of the commits / PR title signal it (i.e. no `!` on the type and no `BREAKING CHANGE:` footer)

The same signal release-please uses to bump the major version is the one CI checks against, so there's a single source of truth — the commit message. The schema diff catches anything that slips past it.

## Architecture

The pipeline collapses to one intermediate (OpenAPI) plus two terminal artifacts:

```
Pydantic models
    │
    ├── schemas/openapi.yaml ────► typescript/src/index.ts   (quicktype, type aliases)
    │                          └─► oasdiff CI                (breaking-change detection)
    │
    └── dbt/*_v{N}.yml                                       (direct, custom Snowflake-type mapping)
```

OpenAPI 3.1 was chosen because (a) it embeds JSON Schema 2020-12 unchanged in `components.schemas`, so we lose no expressiveness; (b) the OpenAPI ecosystem has the most mature breaking-change tooling (`oasdiff`); and (c) the JSON Schema community itself acknowledges no production-grade breaking-change checker exists yet ([GSoC 2026 proposal](https://github.com/json-schema-org/community/issues/984)). dbt is generated directly from Pydantic because the mapping is tiny and dbt-specific (Snowflake type names, `data_tests`).

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/generate_openapi.py` | Pydantic → OpenAPI 3.1 doc |
| `scripts/generate_dbt_schema.py` | Pydantic → dbt `schema.yml` |
| `scripts/classify_semver.py` | Wraps `oasdiff changelog`; classifies a PR as major/minor/none |
| `typescript/scripts/extract-schema.mjs` | OpenAPI → JSON Schema bundle (piped into quicktype) |
