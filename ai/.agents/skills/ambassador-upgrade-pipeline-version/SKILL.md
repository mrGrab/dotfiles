---
name: ambassador-upgrade-pipeline-version
description: "Upgrade ambassador-blueprint-chart pipeline and Helm dependency versions for ambassador applications"
user-invocable: true
---

# Upgrade Ambassador Pipeline Version

## Outcome

This skill updates version references for the ambassador blueprint pipeline and Helm dependency, then prepares merge requests for `develop`, `release` and `master`.

## Required Input

- `jira`: Jira ticket key, for example `DESP-154758`
- `pipeline`: New pipeline version, must include `v` prefix, for example `v2.8`

## Derived Values

- `helm`: Pipeline version without leading `v` (e.g., `pipeline=v2.10` -> `helm=2.10`).
- `dev_branch`: `task/<jira>-develop`
- `rel_branch`: `task/<jira>-release`
- `master_branch`: `task/<jira>-master`

## File Updates Specification

1. **`.gitlab-ci.yml`:**
   Update the `ref` under the `devops/k8s/charts/ambassador-blueprint-chart` include block to `<pipeline>`:
   ```yaml
   include:
     - project: "devops/k8s/charts/ambassador-blueprint-chart"
       ref: "<pipeline>"
   ```
2. **`.helm/Chart.yaml`:**
   Update the `version` of the `ambassador-blueprint-chart` dependency to `<helm>`:
   ```yaml
   dependencies:
     - name: ambassador-blueprint-chart
       version: "<helm>"
   ```

## Execution Procedure

1. **Synchronize Remote Repositories**

```bash
git fetch origin --prune
git checkout develop && git pull --ff-only origin develop
git checkout release && git pull --ff-only origin release
git checkout master && git pull --ff-only origin master
```

2. **Process Branch & Create MR (Run `develop`, `release` and `master`)**
   For target `develop` (branch: `task/<jira>-develop`):

```bash
git checkout -b task/<jira>-develop origin/develop
# Apply file edits to .gitlab-ci.yml and .helm/Chart.yaml
git add .gitlab-ci.yml .helm/Chart.yaml
git commit -m "Upgrade pipeline version to <pipeline>"

# Push using multiple -o flags for multi-line description without raw %0A bugs
git push -u origin task/<jira>-develop \
  -o merge_request.create \
  -o merge_request.target=develop \
  -o merge_request.title="<jira> | Upgrade pipeline version" \
  -o merge_request.description="Upgrade pipeline version to <pipeline>." \
  -o merge_request.description="" \
  -o merge_request.description="/request_review @sds" \
  -o merge_request.description="" \
  -o merge_request.description="/assign @me"
```

For target `release` (branch: `task/<jira>-release`):

```bash
git checkout -b task/<jira>-release origin/release
# Apply file edits to .gitlab-ci.yml and .helm/Chart.yaml
git add .gitlab-ci.yml .helm/Chart.yaml
git commit -m "Upgrade pipeline version to <pipeline>"

git push -u origin task/<jira>-release \
  -o merge_request.create \
  -o merge_request.target=release \
  -o merge_request.title="<jira> | Upgrade pipeline version" \
  -o merge_request.description="Upgrade pipeline version to <pipeline>." \
  -o merge_request.description="" \
  -o merge_request.description="/request_review @sds" \
  -o merge_request.description="" \
  -o merge_request.description="/assign @me"
```

For target `master` (branch: `task/<jira>-master`):

```bash
git checkout -b task/<jira>-master origin/master
# Apply file edits to .gitlab-ci.yml and .helm/Chart.yaml
git add .gitlab-ci.yml .helm/Chart.yaml
git commit -m "Upgrade pipeline version to <pipeline>"

git push -u origin task/<jira>-master \
  -o merge_request.create \
  -o merge_request.target=master \
  -o merge_request.title="<jira> | Upgrade pipeline version" \
  -o merge_request.description="Upgrade pipeline version to <pipeline>." \
  -o merge_request.description="" \
  -o merge_request.description="/request_review @sds" \
  -o merge_request.description="/assign @me"
```

## Verification & Checklist

- [ ] `.gitlab-ci.yml` `ref` contains leading `v` (`<pipeline>`).
- [ ] `.helm/Chart.yaml` dependency `version` excludes leading `v` (`<helm>`).
- [ ] Three branches (`task/<jira>-develop`, `task/<jira>-release` and `task/<jira>-master`) are pushed to origin.
- [ ] Tree MRs created targeting `develop`, `release` and `master` respectively.
- [ ] MR descriptions contain `/request_review @sds` and `/assign @me` on new lines.
