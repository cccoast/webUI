from pandas import to_datetime

error_code = ['create_shm_config','create_shm','create_backtest_config','run_backtest','generate_pta','upload_result']
error_code_dict = dict(zip(range(len(error_code)),error_code))
error_code_dict[-1] = 'cpp_server_closed'
error_code_dict[100] = 'backtest_time_limit_exceed'

def diff_seconds(now, last):
    #     print now,last
    if last[0] == -1 or last[1] == -1:
        return 24 * 3600
    now_day, last_day = to_datetime(str(now[0])), to_datetime(str(last[0]))
    diff_date_seconds = (now_day - last_day).days * 24 * 60 * 60
    diff_tstamp_seconds = (int(now[1]/10000) - int(last[1]/10000)) * 3600 + \
                            ( int( (now[1]%10000)/100 ) - int( (last[1]%10000)/100 ) ) * 60 + \
                              ((now[1]%100) - (last[1]%100))
    gap_seconds = diff_date_seconds + diff_tstamp_seconds
    return gap_seconds
