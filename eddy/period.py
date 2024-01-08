import re
import inspect
import pandas as pd
from dateutil import parser

def parse(period=None, mode='both'):
    """
    Parse a period string into datetime object. 
    """
    valid_mode_set = {
        'year',
        'quarter',
        'both',
    }
    valid_period_set = {
        1, '1',
        2, '2',
        3, '3',
        4, '4',
    }

    if not period:
        return None
    
    if mode not in valid_mode_set:
        raise TypeError("{}() got an unexpected keyword argument".format((inspect.currentframe().f_code.co_name)))

    if mode == 'quarter' or mode == 'both':
        # Try to parse any valid DateTime string into the Quarter datetime
        try:
            return pd.PeriodIndex([parser.parse(period)], freq='Q').to_timestamp(how = 'e').normalize().date[0]
        except:
            # If cannot pass, just let it go further where RegEx will try to parse
            pass

    # Define the case-insensitive regular expression pattern with an optional quarter
    pattern = re.compile(r'(?:CY|FY|Y)?(\d{4})?(?:-?Q([1-4])|$)?', re.IGNORECASE)

    # Match the pattern in the input string
    match = pattern.search(str(period))

    if match:
        if mode == 'both':
            if match.group(2):
                return pd.PeriodIndex(

                    year=[int(match.group(1)) if match.group(1) else pd.Timestamp.now().year],
                    quarter=[int(match.group(2))],
                    freq='Q'

                    ).to_timestamp(how = 'e').normalize().date[0]
            else:
                return pd.PeriodIndex( [str(match.group(1))], freq='A' )
        elif mode == 'quarter':
            if match.group(2):
                return pd.PeriodIndex(

                    year=[int(match.group(1)) if match.group(1) else pd.Timestamp.now().year],
                    quarter=[int(match.group(2))],
                    freq='Q'

                    ).to_timestamp(how = 'e').normalize().date[0]
            else:
                return None
        else:
            if match.group(1):
                return pd.PeriodIndex( [str(match.group(1))], freq='A' )
    else:
        return None

def parseQuarter(period=None):
    return parse(period, mode='quarter')

def parseYear(period=None):
    return parse(period, mode='year')