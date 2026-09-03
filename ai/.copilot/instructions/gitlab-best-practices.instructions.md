---
name: "GitLab CI/CD Best Practices"
description: "Standards for creating, editing, reviewing, or refactoring GitLab CI/CD pipelines, templates, and components."
applyTo: "**/.gitlab-ci.yml, **/gitlab-ci*.yml, **/.gitlab/ci/**/*.yml, **/pipeline*.yml, **/.ci-templates/**/*.yml, **/.ci/**/*.yml, **/templates/**/*.yml"
---

# GitLab CI/CD Best Practices

## Pipeline Structure & Versioning

- **Explicit Stages:** Define `stages:` at the top of every pipeline (e.g., `[.pre, lint, build, test, security, package, deploy, .post]`).
- **Modular Layout:** Keep top-level `.gitlab-ci.yml` files lean. Use `include:` to load logical blocks from `.gitlab/ci/`.
- **Pipeline Versioning:** Include the `pipeline-version-component` with an explicit SemVer version.
- **Pre-MR Bump Rule:** Increment SemVer versions and update `CHANGELOG.md` (_Keep a Changelog_ format) at the very end of work—right before submitting the Merge Request / final commit.

## Job Conditions (`rules:`)

- **Always use `rules:`** — never use deprecated `only:` / `except:`.
- Use `workflow:rules:` to control overall pipeline execution (e.g., branch vs. MR pipelines).
- Combine `if:` conditions with `changes:` to avoid running heavy jobs when unrelated files change.

```yaml
rules:
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    changes:
      - "src/**/*"
  - if: $CI_COMMIT_BRANCH ==$CI_DEFAULT_BRANCH
```

## Security & Secrets

- **Zero Hardcoded Secrets:** Use GitLab Masked/Protected variables or Vault/HashiCorp integration.
- **Least Privilege:** Restrict job tokens (`job:secrets`) and runner permissions to minimum required scopes.
- **Security Scanning:** Include official templates for SAST, Dependency Scanning, and Secret Detection:

```yaml
include:
  - project: "ci-templates/common"
    ref: "v2.37"
    file: "security-scans.yml"
```

## Performance & Caching

- **Fastzip:** Set `variables: FF_USE_FASTZIP: "true"` and `GIT_DEPTH: "10"` globally for faster archiving and checkout.
- **Targeted Caching:** Cache dependency paths (e.g., `.venv/`, `node_modules/`) using `key: "$CI_COMMIT_REF_SLUG"`. Use `policy: pull` on consumer jobs.
- **Artifact Scoping:** Limit build artifacts with explicit `paths:`, set `expire_in:` on every artifact (e.g., `1 week`), and use `needs:` to pass artifacts directly between dependent jobs.

```yaml
build-job:
  stage: build
  script: make build
  artifacts:
    paths: [dist/]
    expire_in: 1 week

test-job:
  stage: test
  needs: [build-job]
  script: make test
```

## Job Optimization & Execution Control

- **Job Reuse:** Use `extends:` for job inheritance; use `!reference` tags for script/rule snippets. Avoid raw anchors unless required for simple scalar values.
- **Timeouts & Safety:** Set `timeout:` on long-running jobs. Mark non-deployment jobs `interruptible: true`.
- **Parallel Builds:** Use `parallel:matrix:` for multi-version or fan-out testing matrixes.
- **Deployments:** Set `environment:name` and `environment:url`. Protect production jobs with `when: manual` and `resource_group:` to prevent concurrent deployment races.

## Components & Includes

- Prefer _GitLab CI Components_ over legacy template includes.
- Pin components/includes to a _minor version_ (`~X.Y`) — never use `@latest` or unpinned refs.
- Provide typed `inputs:` with default values in component `spec:` blocks.
