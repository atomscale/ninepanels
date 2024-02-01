

from .consumers import user_comms
from .consumers import monitoring
from .consumers import performance
from .consumers import logs

dispatcher = {
    # always ensure a list of funcs, even if only one.
    # asyncio.gather is run across the list

    'route_timing_created': [performance.handle_route_timing_created],
    'route_timings_persisted': [performance.handle_route_timings_persisted],
    'new_user_created': [user_comms.handle_new_user_created, monitoring.report_info],
    'user_logged_in': [logs.log_info, monitoring.report_info, monitoring.update_user_login],
    'user_activity': [monitoring.update_user_activity],
    'password_reset_requested': [user_comms.password_reset, monitoring.report_info],
    'exc_raised_info': [logs.log_info],
    'exc_raised_warn': [logs.log_warn, monitoring.report_exc_warn],
    'exc_raised_error': [logs.log_error, monitoring.report_exc_error],
}

