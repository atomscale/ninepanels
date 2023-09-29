from . import comms
from . import performance
from . import monitoring
from . import logs
from . import event_types

dispatcher = {
    # always ensure a list of funcs, even if only one.
    # asyncio.gather is run across the list
    event_types.NEW_USER_CREATED: [comms.welcome, monitoring.report_info],
    event_types.USER_LOGGED_IN: [logs.log_info, monitoring.report_info],
    event_types.PASSWORD_RESET_REQUESTED: [comms.password_reset, monitoring.report_info],

    event_types.TIMING_COMPLETED: [performance.timing_event_handler],
    event_types.TIMING_PROCESSED: [], # sio and
    event_types.TIMING_ALERT: [logs.log_warn, monitoring.report_exc_warn],

    event_types.EXC_RAISED_ERROR: [logs.log_error, monitoring.report_exc_error],
    event_types.EXC_RAISED_WARN: [logs.log_warn, monitoring.report_exc_warn],
    event_types.EXC_RAISED_INFO: [logs.log_info],
}
