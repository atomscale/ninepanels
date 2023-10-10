from .. import logs


from . import event_types

from .handlers import user_comms
from .handlers import monitoring
from .handlers import performance

dispatcher = {
    # always ensure a list of funcs, even if only one.
    # asyncio.gather is run across the list

    'route_timing_created': [performance.handle_route_timing_created],
    'route_timings_persisted': [performance.handle_route_timings_persisted],


    'new_user_created': [user_comms.handle_new_user_created, monitoring.report_info],
    'user_logged_in': [logs.log_info, monitoring.report_info],
    'password_reset_requested': [user_comms.password_reset, monitoring.report_info],


    # event_types.TIMING_STATS_PERSISTED: [],
    # event_types.TIMING_ALERT: [],

    event_types.EXC_RAISED_ERROR: [logs.log_error, monitoring.report_exc_error],
    event_types.EXC_RAISED_WARN: [logs.log_warn, monitoring.report_exc_warn],
    event_types.EXC_RAISED_INFO: [logs.log_info],
}

