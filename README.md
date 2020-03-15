# django-beanstalk-worker
An app for handling deferred and periodic tasks on beanstalk worker machines

## Overview
The core of this app is the task decorator.

When a decorated task function is called instead of running immediately an SQS message is queued. When unqueued by a worker that message will cause the original function to be called. Primitive, datetime and decimal arguments (and any combination of those) will be preserved any other argument types will cause an error.

Task functions can also be invoked by cron or a management command as needed.

## Installation and Setup

### 1: Installed Apps
Add `beanstalk_worker` to `installed_apps`.

### 2: Environment Variables
In the `Software` section of the Beanstalk configuration of your worker environment add the environment variable `WORKER` and set it to `1`

### 3: Django Settings
Add the following settings to your Django settings:
```
BEANSTALK_WORKER = bool(os.environ.get("WORKER", False))
BEANSTALK_TASK_SERVICE = "beanstalk_worker.services.TaskService"
BEANSTALK_SQS_URL = <SQS queue URL>
BEANSTALK_SQS_REGION = <Amazon region>
```
You can find the SQS queue URL in the `Worker` section of the Beanstalk environment configuration.

For test and development you can omit the SQS settings and should set `BEANSTALK_TASK_SERVICE = "beanstalk_worker.services.FakeTaskService"`

### 4: URLs's
In your top level URL's add
```
if settings.BEANSTALK_WORKER:
    urlpatterns.append(url(r"^tasks/", include("beanstalk_worker.urls")))
```
DO NOT include these URL's in a production web server, only the worker.

For test and development you won't have seperate web and worker machines so always include the URL's.

### 5: Beanstalk Worker Configuration
In the `Worker` section of the Beanstalk configuration of your worker environment set `HTTP path` to `/tasks/task/` and `MIME type` to `application/json`
