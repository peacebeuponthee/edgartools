import re
import pandas as pd

def parse_period(period=None):
    if not period:
        return period
    
    # Define the case-insensitive regular expression pattern with an optional quarter
    pattern = re.compile(r'(?:C|F)?(?:Y|Y)?(\d{2,4})(?:Q(\d))?', re.IGNORECASE)

    # Match the pattern in the input string
    match = pattern.search(str(period))

    if match:
        if match.group(2) is not None and match.group(2) >= '1' and match.group(2) <= '4':
            return pd.PeriodIndex(year=[int(match.group(1))], quarter=[int(match.group(2))], freq='Q' ).to_timestamp(how = 'e').normalize().date[0]
        else:
            return str(pd.PeriodIndex([str(match.group(1))], freq='A' ).to_timestamp(how = 'e').normalize().year[0])