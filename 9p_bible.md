# The Nine Panels Bible 🙏

Notes, coding, style guide, architecture notes.

### Code Styling:

### Exception Handling:

All exceptions defined in the code must be of a custom type and inherit from `NinePanelsBaseException`.

`NinePanelsBaseException` handles all error logging, and ensures all errors contain a `detail` property.

`detail` is the human readbale, user friendly error message. `context_msg` provides space for a more technical description. `context_data` kwargs accept key value pairs of data relevant to the error.

At the main.py api level, all customer errors propgated up must be then wrapped finally in a `fastapi.HTTPException` with the `detail` param passed from the custom exception:

```
try:
    resp = update_foo()
except errors.FooNotUpdated as e:
    raise HTTPException(status=400, detail=e.detail)
```

### API Design:

#### Wrapped Responses

All responses, apart from those listed below, are intercepted by a middleware `ResponseWrapperMiddleware` that wraps the response in a standard object `.pydmodels.WrappedResponse`

Exceptions to wrapped responses:

- /docs
- /openapi.json
- /redoc
- /token

`/token` is not wrapped so as to enable swagger docs to authenticate.

### Logging and Monitoring:

Log messages are of a standard schema defined in `.pydmodels.LogMessage`. All calls to `logging` shoudl utilise the LogMessage schema.

### Testing:

### Documentation:

#### API Docs

Published doc style will be redoc.