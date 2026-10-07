# Pipeline Operations

> **Opt-in toolset**: Enable with `USE_PIPELINE=true` or `GITLAB_TOOLSETS=pipelines`

## List & Inspect

```
list_pipelines             -> list pipelines with filters (status, ref, source)
get_pipeline               -> pipeline details (status, duration, coverage)
get_pipeline_variables     -> variables configured on a pipeline
get_pipeline_test_report   -> full unit test report
get_pipeline_test_report_summary -> summarized unit test report
update_pipeline_metadata   -> rename a pipeline
delete_pipeline            -> permanently delete a pipeline and related data
list_pipeline_jobs         -> all jobs in a pipeline
list_pipeline_trigger_jobs -> trigger/bridge jobs (downstream pipelines)
get_pipeline_job           -> single job details
get_pipeline_job_output    -> job log output (supports pagination for large logs)
```

Read tools use `project_id` and `pipeline_id`. Variable and test report tools also accept `page` and `per_page`. Updating pipeline metadata requires permission to administer pipelines. Deleting a pipeline requires the project Owner role. This permanently deletes the pipeline, jobs, logs, artifacts, and triggers. It does not delete child pipelines.

## Create & Control

```
create_pipeline            -> trigger new pipeline for a branch/tag
  project_id: "my-group/my-project"
  ref: "main"
  variables: [{ key: "DEPLOY_ENV", value: "staging" }]
```

```
retry_pipeline             -> retry all failed jobs in a pipeline
cancel_pipeline            -> cancel running pipeline
play_pipeline_job          -> run a manual job
play_pipeline_jobs         -> run multiple manual jobs sequentially
retry_pipeline_job         -> retry a single failed job
cancel_pipeline_job        -> cancel a single running job
erase_pipeline_job         -> erase a job log and artifacts
wait_for_pipeline          -> poll until a pipeline reaches a terminal status
wait_for_job               -> poll until a job reaches a terminal status
```

`play_pipeline_job` and `retry_pipeline_job` accept `job_inputs` for typed manual-job inputs.

## Artifacts

```
list_job_artifacts         -> list files in a job's artifact archive
get_job_artifact_file      -> get content of a single artifact file
download_job_artifacts     -> download full artifact archive (zip) to local_path
```

## Deployments & Environments

```
list_deployments           -> list deployments with filters
get_deployment             -> deployment details
create_deployment          -> create a deployment record
update_deployment          -> update deployment status
delete_deployment          -> delete a deployment
list_deployment_merge_requests -> list merge requests shipped in a deployment
approve_deployment         -> approve or reject a protected deployment
list_environments          -> list project environments
get_environment            -> environment details
update_environment         -> update environment settings
delete_environment         -> delete a stopped environment
stop_environment           -> stop one environment
stop_stale_environments    -> stop environments older than a cutoff
delete_review_app_environments -> schedule deletion of stopped review apps
```

`stop_stale_environments` does not stop protected environments and does not delete environments. `delete_review_app_environments` schedules deletion one week later and uses `dry_run: true` by default.

## Pipeline Triggers

Use `list_pipeline_triggers`, `get_pipeline_trigger`, `create_pipeline_trigger`, `update_pipeline_trigger`, or `delete_pipeline_trigger` to manage project trigger tokens. Use `trigger_pipeline` to start a pipeline with a trigger token.

## Clean up review environments

`stop_stale_environments` stops eligible stale environments. It excludes protected environments and does not delete them.

`delete_review_app_environments` schedules deletion of stopped review apps one week later. It defaults to `dry_run: true`. Set `dry_run: false` only after you verify the scope.

## Common Patterns

### Check why a pipeline failed

1. `list_pipelines` with `status: "failed"` -> get pipeline ID
2. `list_pipeline_jobs` -> find failed job(s)
3. `get_pipeline_job_output` -> read error logs

### Retry failed pipeline

1. `retry_pipeline` -> retries all failed jobs
   OR
2. `retry_pipeline_job` -> retry specific job only

### Download test results

1. `list_job_artifacts` -> find the test report file path
2. `get_job_artifact_file` -> read the report content
