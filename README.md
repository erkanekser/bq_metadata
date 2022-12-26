# BQ Metadata

BQ Metadata is a project created for the following purposes:
- Keep datasets, tables and views metadata history.
- Create datasets, tables and views from gitlab with config files and trigger the code with CI/CD.
- Manage all of the developments about BQ datasets, tables and views.
 
## How is it work? 

- Project has docker image, it contains miniconda , gcloud to run some google cli commands and our scripts for validation and deployment pipelines.

- We have importer code to import your existing structure. It will create all of the folders for your project. You should run: 

`python importer.py -p your_project_name`

- We add configurations to gitlab-ci.yml. 

- We have 2 variables we defined as a Gitlab CI-CD variable here:
  - SERVICE_ACCOUNT : Google Service Account. Your project will work with using this service acccount.
  - BQMETADATA_RUN_PIPELINE : It should be True if you want the pipeline to be triggered. You can set a different value if you want to disable it.

- We copied SERVICE_ACCOUNT to app/credentials.json in our image. `cat "$SERVICE_ACCOUNT" > /app/credentials.json`
- Activate gcloud with 
````
    - gcloud auth activate-service-account --key-file=/app/credentials.json
    - project_id=($(jq -r '.project_id' /app/credentials.json))
    - gcloud config set project "${project_id[@]}"

````

- Create config file to create dataset/table/view. The folder directory structure sould be like: 

````
bq_metadata
  └───project_1
  │   └───dataset_1
  │   │   │   dataset_1.json
  │   │   └───tables
  │   │       │   table_1.json
  │   │       │   table_2.json
  │   │       │   ...
  │   │   └───views
  │   │       │   view_1.sql
  │   │       │   view_2.sql
  │   │       │   ...
  │   └───dataset_2
  │   |   │   dataset_2.json
  │   │   │   ...
````
:boom:  **When you open Merge Request pipeline will;**

- Run **entry.sh** to deploy your configs. We get files that you created, updated or deleted with :
````
ADDED_FILE_LIST=($(git diff --no-commit-id --name-only --diff-filter=A -M100% HEAD^ HEAD 'bq_metadata/**/*.json' 'bq_metadata/**/*.sql'))
DELETED_FILE_LIST=($(git diff --no-commit-id --name-only --diff-filter=D -M100% HEAD^ HEAD 'bq_metadata/**/*.json' 'bq_metadata/**/*.sql'))
UPDATED_FILE_LIST=($(git diff --no-commit-id --name-only --diff-filter=M HEAD^ HEAD 'bq_metadata/**/*.json' 'bq_metadata/**/*.sql'))
````

In the continuation of the code, we run the code in the following order:

1) Create step
    - Dataset
    - Table
    - View
2) Update step
    - Dataset
    - Table
    - View
3) Delete step
    - View
    - Table
    - Dataset

### Examples 

:one: *Dataset:*

````
bq_metadata
  └───project_1
  │   └───dataset_1
  │   │   │   dataset_1.json
````

````json
{
    "location": "EU",
    "projectId": "project-1",
    "datasetId": "dataset_1",
    "properties": {
        "description": "Test-dataset",
        "default_table_expiration_ms": 86400000,
        "default_partition_expiration_ms": 93600,
        "labels": {
            "type": "test"
        }
    }
}
````

:two: *Tables* 

````
bq_metadata
  └───project-1
  │   └───dataset_1
  │   │   └───tables
  │   │       │   table_1.json
````

````json
{
    "projectId": "project-1",
    "datasetId": "dataset_1",
    "tableId": "table_1",
    "schema": {
        "fields": [
            {
                "description": "Test description",
                "fields": [
                    {
                        "description": "Test nested",
                        "mode": "NULLABLE",
                        "name": "test_nested",
                        "type": "STRING"
                    },
                    {
                        "description": "Test nested2",
                        "fields": [
                            {
                                "description": "Test nested3",
                                "mode": "NULLABLE",
                                "name": "test_nested_3",
                                "type": "FLOAT"
                            }
                        ],
                        "mode": "REPEATED",
                        "name": "test_nested_2",
                        "type": "RECORD"
                    }
                ],
                "mode": "NULLABLE",
                "name": "full_name",
                "type": "RECORD"
            },
            {
                "mode": "REQUIRED",
                "name": "age",
                "type": "INTEGER"
            },
            {
                "mode": "NULLABLE",
                "name": "date_column",
                "type": "TIMESTAMP"
            }
        ]
    },
    "labels": {
        "color": "green",
        "type": "test_label"
    },
    "timePartitioning": {
        "field": "date_column",
        "type": "DAY",
        "expirationDays": 30000
    }
}
````


:three: *Views*

````
bq_metadata
  └───project-1
  │   └───dataset_1
  │   │   └───views
  │   │       │   view_1.sql
````

````sql
create or replace view `project-1.dataset_1.view_1` 
as
select * from `project-1.dataset_1.test_table_1`;
````
