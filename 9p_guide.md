# The Nine Panels Bible 🙏

Notes, coding, style guide, architecture notes.

## Code Styling:

`print()` must not make it to production. search for that in staging before deployment.
`console.log()` must not make it to production. search for that in staging before deployment.

### imports

#### dependency management

Using poetry. It's awesome.

pydeps can be used to visualise imports and help debug any circular imports with `pydeps ninepanels`

#### import order
import order should be:

- full stdlib packages
- site_packages (those installed with poetry) grouped by package
- ninepanels imports

#### import form

imports from ninepanels itself should generally be explicit and in full:

```from . import crud```

not:

``` from .crud import create_user```

This helps see in the code which file is providing the function. Exceptions to this rule for Depends(get_db) etc are ok.

any classes or funcs imported should be one per line only:

```
from sqlalchemy.orm import Column
from sqlalchemy.orm import Integer
```

not:

```
from sqlalchemy.orm import Integer, Column
```

This helps maintain visual clarity and makes and debugging-via-commenting-out much easier!

#### naming

```
from . import sqlmodels as sql
from . import pydmodels as pyd
```

### time data

Use utc times for all system related times such as logs.

```timestamp=datetime.utcnow()
```

## Exception Handling:

All exceptions defined in the code must be of a custom type and inherit from `NinePanelsBaseException`.


`detail` is the human readbale, user friendly error message. `context_msg` provides space for a more technical description. `context_data` kwargs accept key value pairs of data relevant to the error.

At the http layer, all custom errors propgated up must be then wrapped finally in a `fastapi.HTTPException` with the `detail` param passed from the custom exception:

```
try:
    resp = update_foo()
except exceptions.FooNotUpdated as e:
    raise HTTPException(status=400, detail=e.detail)
```

## Asynchronous Event Queue

A single async queue object `.queues.event_queue` and an associated async worker `.queues.event_worker` process events. Events have a defined model `.pydmodels.Event` which accepts a `type` and `payload`.

`type`s are defined as constants in `.event_types` to ensure consistency. A `dispatcher` dict keyed by `.event_types` lists the event handler coroutines to be awaited by the `.queues.event_worker`

The `payload` definition and practice is still WIP. The general notion at the moment is to produce the instance of the object which accompanies the event. Eg: if a `.event_types.NEW_USER_CREATED` event occurs, the common sense payload would be the `.sqlmodels.User` instance related to that new user. Stronger contracts around this will be developed.

### naming and patterns:

An `event_type` must be a verb in the past tense. ie NEW_USER_CREATED

An event handler will be a coroutine and should be called `handle_{event_type}`

## API Design:

### Wrapped Responses

All responses, apart from those listed below, are intercepted by a middleware `ResponseWrapperMiddleware` that wraps the response in a standard object `.pydmodels.WrappedResponse`

Exceptions to wrapped responses:

- /docs
- /openapi.json
- /redoc

The response to `/token` is not wrapped if the calling referer is `/docs` so as to enable Swagger docs to authenticate.

`meta` response information, such as number of records, remaining pages etc, can be extracted from the response object as necessary, and passed into the middelware by setting `request.state.meta = {meta data to be passed}`. When designing the return object to the calling http path operation function, bare this option in mind when desiging the shape of the returned data. An extra 'meta' dict could be returned, then removed from the reponse `data` key and assigned to `meta`


## Logging and Monitoring:

Logging utlises the `.pydmodels.LogMessage` model.

### HTTP Performance

HTTP request response timing is provided by a custom middleware instance called `TimingMiddleware`. This produces an event to the event queue for persitence, analysis and alerting.

## Testing:

## Environment Management:

Three branch strategy: Feature, Staging, Main (production)

`mc.sh` is a set of orchestration and guardrails written in shell (`mc.sh` and it's children) and python (`data_mgmt.py`) to manage data in feature, staging and prod environments.

## Deployment

Keep commits atomic and more better than less, push to production often with small granular changes. Easier to fix forward

**ALWAYS FIX FORWARD if needed**

Do not rollback, revert or otherwise mess with the branch timelines.

Follow the deployment checklist for pushes from staging to prod.

Initial questions to ask:

- does this involve a db schema migration?
- does this involve deploying front and backends in tandem?

**CHECKLIST:**
- update backup table selection across backup.sh if db schema changes
- search for prints and console.logs - verify 0
- check any helpers like temp component log in state for example are reset
- check any new envars are in staging and prod
- review each change before commit
- manual testing of area in feature env
- push to staging and manually test
- local tests pass on feature branch
- PR staging to main and review code changes again in GH
- backup main db full and data only
- merge PR
- manually test in prod



## Documentation:

### API Docs

Published doc style will be redoc.


_______

## Code Notes and patterns

```
executor = ThreadPoolExecutor(thread_name_prefix="timing_")


def long_runner(event: pyd.Event):
    """FOR THE EVENT ROUTE ONLY"""
    import time

    for n in range(5):
        time.sleep(1)
        print(f"long running job 1 in {threading.current_thread().name}")


def another_long_runner(event: pyd.Event):
    """FOR THE EVENT ROUTE ONLY"""
    import time

    for n in range(5):
        time.sleep(1)
        print(f"long running job ANTOEHR in {threading.current_thread().name}")


async def handle_timing_persisted(event: pyd.Event):
    print(f"runing long runner in {threading.current_thread().name}")

    asyncio.gather(
        asyncio.to_thread(long_runner, event),
        asyncio.to_thread(another_long_runner, event),
    )
```