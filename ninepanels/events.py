from . import comms
from . import performance
from . import monitoring
from . import logs

NEW_USER_CREATED = "new_user_created"
USER_LOGGED_IN = "user_logged_in"
PASSWORD_RESET_REQUESTED = "password_reset_requested"

TIMING_COMPLETED = "timer_completed"

EXC_RAISED_ERROR = "exc_raised_error"
EXC_RAISED_WARN = "exc_raised_warn"
EXC_RAISED_INFO = "exc_raised_info"


dispatcher = {
    # always ensure a list of funcs, even if only one.
    # asyncio.gather is run across the list
    NEW_USER_CREATED: [comms.welcome, monitoring.report_info],
    USER_LOGGED_IN: [logs.log_info, monitoring.report_info],
    PASSWORD_RESET_REQUESTED: [comms.password_reset, monitoring.report_info],

    TIMING_COMPLETED: [performance.process_timing_events],


    EXC_RAISED_ERROR: [logs.log_error, monitoring.report_exc_error],
    EXC_RAISED_WARN: [logs.log_warn, monitoring.report_exc_warn],
    EXC_RAISED_INFO: [logs.log_info],
}
