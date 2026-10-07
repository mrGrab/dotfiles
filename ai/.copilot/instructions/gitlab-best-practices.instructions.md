---
name: "GitLab CI/CD Best Practices"
description: "Rules for creating, changing, reviewing, and refactoring GitLab CI/CD pipelines, templates, and components."
applyTo: "**/.gitlab-ci.yml, **/gitlab-ci*.yml, **/.gitlab/ci/**/*.yml, **/pipeline*.yml, **/.ci-templates/**/*.yml, **/.ci/**/*.yml, **/templates/**/*.yml"
---

# GitLab CI/CD Best Practices

## Pipeline structure and versioning

- **Define stages:** Add `stages:` near the top of each pipeline. For example: `[.pre, lint, build, test, security, package, deploy, .post]`.
- **Use modules:** Keep the root `.gitlab-ci.yml` short. Use `include:` to load related configuration from `.gitlab/ci/`.
- **Version the pipeline:** Include `pipeline-version-component` and set an explicit Semantic Versioning (SemVer) version.
- **Update the version before submission:** At the end of the work, just before you submit the merge request or make the final commit, increment the SemVer version and update `CHANGELOG.md` in _Keep a Changelog_ format.

## Job rules

- Always use `rules:`. Do not use the deprecated `only:` or `except:` keywords.
- Use `workflow:rules:` to control when a pipeline runs, such as for branch or merge request pipelines.
- Combine `if:` and `changes:` to skip resource-intensive jobs when unrelated files change.

```yaml
rules:
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    changes:
      - "src/**/*"
  - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Security and secrets

- **Do not hardcode secrets:** Use GitLab masked and protected variables, or a Vault/HashiCorp integration.
- **Use least privilege:** Give job tokens, secrets, and runners only the permissions they need.
- **Run security scans:** Include official templates for SAST, dependency scanning, and secret detection. For example:

```yaml
include:
  - project: "ci-templates/common"
    ref: "v2.37"
    file: "security-scans.yml"
```

## Performance and caching

- **Enable Fastzip:** Set `FF_USE_FASTZIP: "true"` and `GIT_DEPTH: "10"` in the global `variables:` section to speed up archiving and checkout.
- **Cache dependencies:** Cache only the paths the jobs need, such as `.venv/` or `node_modules/`. Use `key: "$CI_COMMIT_REF_SLUG"` and set `policy: pull` for jobs that only use the cache.
- **Limit artifacts:** Set explicit `paths:` and `expire_in:` values for every artifact. For example, set `expire_in: 1 week`. Use `needs:` to pass artifacts directly to dependent jobs.

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

## Job reuse and execution control

- **Reuse job configuration:** Use `extends:` to inherit job settings and `!reference` to reuse script or rule sections. Avoid YAML anchors unless you need them for simple scalar values.
- **Set job limits:** Set `timeout:` for long-running jobs. Set `interruptible: true` for jobs that do not deploy.
- **Run jobs in parallel:** Use `parallel:matrix:` to test multiple versions or configurations.

## Components and includes

- Prefer _GitLab CI Components_ to older template includes.
- Pin components and includes to a _minor version_ (`~X.Y`). Do not use `@latest` or an unpinned reference.
- Define typed `inputs:` with default values in component `spec:` blocks.
