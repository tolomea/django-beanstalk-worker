# django-beanstalk-worker
An app for handling deferred and periodic tasks on beanstalk worker machines

## Overview
The core of this app is the task decorator.

When a decorated task function is called instead of running immediately an SQS message is queued. When unqueued by a worker that message will cause the original function to be called.

The arguments may be any combination of JSON serializable types, datetimes and decimals, including keyword arguments. Any other argument types will cause an error.

Queuing of SQS messages happens in transaction on_commit so if you exception out of a transaction any tasks called in that transaction will not be run.

Task functions can also be invoked by cron or a management command as needed.

## Installation and Setup

### 1: Installed Apps
Add `beanstalk_worker` to `installed_apps`.

### 2: Environment Variables
In the `Software` section of the Beanstalk configuration of your worker environment add the environment variable `WORKER` and set it to `1`

### 3: Django Settings
Add the following settings to your Django settings:
```python
BEANSTALK_WORKER = bool(os.environ.get("WORKER", False))
BEANSTALK_TASK_SERVICE = "beanstalk_worker.services.TaskService"
BEANSTALK_SQS_URL = <SQS queue URL>
BEANSTALK_SQS_REGION = <Amazon region>
```
You can find the SQS queue URL in the `Worker` section of the Beanstalk environment configuration.

For test and development you can omit the SQS settings and should set `BEANSTALK_TASK_SERVICE = "beanstalk_worker.services.FakeTaskService"`

### 4: URLs's
In your top level URL's add
```python
if settings.BEANSTALK_WORKER:
    urlpatterns.append(url(r"^tasks/", include("beanstalk_worker.urls")))
```
DO NOT include these URL's in a production web server, only the worker.

For test and development you won't have seperate web and worker machines so always include the URL's.

### 5: Beanstalk Worker Configuration
In the `Worker` section of the Beanstalk configuration of your worker environment set `HTTP path` to `/tasks/task/` and `MIME type` to `application/json`

## Use

### Declare a task function
```python
from beanstalk_worker import task

@task
def my_task(message="hi"):
    print(message)
```

### Call the task from anywhere in your code
```python
my_task("hello world")
```
This will queue an SQS message instructing a worker to run the actual function.

The arguments may be any combination of JSON serializable types, datetimes and decimals, including keyword arguments

### Call the task from CRON

In [cron.yaml](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features-managing-env-tiers.html#worker-periodictasks) add 
```yaml
- name: "my_project.my_app.tasks.my_task"
  url: "/tasks/cron/"
  schedule: "0 0 * * *"
```
`my_project.my_app.tasks.my_task` should be replaced with the fully qualified name of your task function.

Arguments are not currently supported for cron.

### Call the task from the command line

```
./manage.py run_task my_project.my_app.tasks task ["hello world"]
```
`my_project.my_app.tasks my_task` should be replaced with the fully qualified name of your task function, also note the space between module name and function name.


