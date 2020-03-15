# django-beanstalk-worker
An app for handling deferred and periodic tasks on beanstalk worker machines

<!-- MarkdownTOC autolink="true" -->

- [Overview](#overview)
- [Installation and Setup](#installation-and-setup)
	- [1: Installed Apps](#1-installed-apps)
	- [2: Environment Variables](#2-environment-variables)
	- [3: Django Settings](#3-django-settings)
	- [4: URLs's](#4-urlss)
	- [5: Beanstalk Worker Configuration](#5-beanstalk-worker-configuration)
- [Use](#use)
	- [Declare a task function](#declare-a-task-function)
	- [Call the task from anywhere in your code](#call-the-task-from-anywhere-in-your-code)
	- [Call the task from CRON](#call-the-task-from-cron)
	- [Call the task from the command line](#call-the-task-from-the-command-line)
- [Development, Testing and the FakeTaskServer](#development-testing-and-the-faketaskserver)
	- [settings.DEBUG](#settingsdebug)
	- [Test support](#test-support)
	- [settings.BEANSTALK_WORKER](#settingsbeanstalk_worker)

<!-- /MarkdownTOC -->


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

This will add the URLS `/tasks/task/` and `/tasks/cron`. You can move the base of these URL's if you do so other instructions on this page will need updating appropriately.

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

```console
./manage.py run_task my_project.my_app.tasks task "['hello world']"
```
`my_project.my_app.tasks my_task` should be replaced with the fully qualified name of your task function, also note the space between module name and function name.


## Development, Testing and the FakeTaskServer

The FakeTaskServer will internally queue tasks but will not run them unless instructed to.

### settings.DEBUG
When `DEBUG = True` is set in the Django settings an additional URL is exposed at `/tasks/run_all/` if you poke this URL the `FakeTaskService` will run all queued tasks. This can be handy for local development.

### Test support
In tests you can acquire the running task service instance with `from beanstalk_worker import task_service`. This class has two helpers `clear` whcih will discard all queued tasks and `run_all` which will immediately run all queued tasks.

### settings.BEANSTALK_WORKER
While running a task the FakeTaskServer will patch `settings.BEANSTALK_WORKER` to `True`. This lets you `assert settings.BEANSTALK_WORKER` in code that should only ever be run on a worker.
