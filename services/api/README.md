# Carlos API

## Configuration

The backend is configured via environment variables.
The following sections define those environment variables.
Any entry without a default value is mandatory.

### General

| Environment Variable |              Type               |          Default           | Description                                                                                                                                                                                              |
|:---------------------|:-------------------------------:|:--------------------------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| LOG_LEVEL            |              `int`              |           `info`           | The logging level for the application, the log level is on an integer scale, see https://docs.python.org/3/library/logging.html#levels for details. Passing the level names as strings is also accepted. |

### Security

| Environment Variable |   Type   | Default | Description                     |
|:---------------------|:--------:|:-------:|---------------------------------|
| AUTH0_TENANT_ID      | `string` |         | The Auth0 tenant ID.            |
| AUTH0_REGION         | `string` |         | The Auth0 region.               |
| AUTH0_AUDIENCE       | `string` |         | The Auth0 audience.             |

| Environment Variable |        Type        | Default | Description                                                                                   |
|:---------------------|:------------------:|:-------:|-----------------------------------------------------------------------------------------------|
| BACKEND_CORS_ORIGINS | `List[AnyHttpUrl]` |  `[]`   | A JSON-formatted list of origins. For example: `["http://localhost", "http://localhost:4200"` |


#### ⚠️ Danger Zone ⚠️

The following settings are debugging purposes only. Never use them in production.

| Environment Variable     |  Type  | Default | Description                      |
|:-------------------------|:------:|:-------:|----------------------------------|
| API_DEACTIVATE_USER_AUTH | `bool` | `False` | If set to true                   |
| API_DOCS_ENABLED         | `bool` | `False` | Deactivate admin authentication. |