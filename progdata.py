#!/usr/bin/env python

# The following string describes the 52 byte record as a struct of different
# types. H indicates an unsigned short (2 bytes), h indicates a signed short,
# B indicates an unsigned char (1 byte), and finally x is a padding byte (to
# be ignored). The < character notes that the data is little-endian, since
# according to company specification, "Multi-byte binary values are generally
# stored and sent least significant byte first". 
fmtA = '<HHhhhHHHHHhBBBBBBBBHBBBBBBBBBBxBBBBBBBBB'

# All data is stored in raw binary form. This dictionary will map the field
# name to a function with which to format the data. For example, the date is
# converted into the format "d/m/y" instead of an int like 7623. Some fields
# map to a function "nothing" that simply returns its argument. This is because
# it either does not need to be formatted (e.g. avg_wind and hi_wind) or else 
# it is a piece of data my weather system does not record. 
format_map = {
    "date"             : decompress_date, 
    "time"             : decompress_time, 
    "out_temp"         : float_div_ten, 
    "hi_out_temp"      : float_div_ten, 
    "low_out_temp"     : float_div_ten, 
    "rainfall"         : float_div_hundred, # convert to inches (/period)
    "hi_rain_rate"     : float_div_hundred, # convert to inches/hour
    "barometer"        : flaot_div_thousand, 
    "solar_rad"        : nothing, 
    "num_wind_samples" : nothing, 
    "inside_temp"      : float_div_ten, 
    "in_humidity"      : float_div_hundred, 
    "out_humidity"     : float_div_hundred, 
    "avg_wind"         : nothing,
    "hi_wind"          : nothing, 
    "hi_wind_dir"      : eval_wind, 
    "prevailing_dir"   : eval_wind, 
    "avg_UV"           : nothing, 
    "ET"               : nothing, 
    "high_solar_rad"   : nothing, 
    "high_UV"          : nothing, 
    "forecast_rule"    : eval_forecast, 
    "leaf_temp1"       : nothing,
    "leaf_temp2"       : nothing, 
    "leaf_wet1"        : nothing, 
    "leaf_wet2"        : nothing, 
    "soil_temp1"       : nothing, 
    "soil_temp2"       : nothing,
    "soil_temp3"       : nothing, 
    "soil_temp4"       : nothing, 
    "extra_hum1"       : nothing, 
    "exta_hum2"        : nothing, 
    "extra_temp1"      : nothing, 
    "extra_temp2"      : nothing, 
    "extra_temp3"      : nothing, 
    "soil_moist1"      : nothing, 
    "soil_moist2"      : nothing, 
    "soil_moist3"      : nothing, 
    "soil_moist4"      : nothing
}

# A list of all the data fields. In the setup, any fields that the client
# wants to exclude will be turned to empty strings. 
ordFieldsA = [
    "date", "time", "out_temp", "hi_out_temp", "low_out_temp", 
    "rainfall", "hi_rain_rate", "barometer", "solar_rad", 
    "num_wind_samples", "inside_temp", "in_humidity", "out_humidity",
    "avg_wind", "hi_wind", "hi_wind_dir", "prevailing_dir", "avg_UV",
    "ET", "high_solar_rad", "high_UV", "forecast_rule", "leaf_temp1",
    "leaf_temp2", "leaf_wet1", "leaf_wet2", "soil_temp1", "soil_temp2",
    "soil_temp3", "soil_temp4", "extra_hum1", "exta_hum2", 
    "extra_temp1", "extra_temp2", "extra_temp3", "soil_moist1", 
    "soil_moist2", "soil_moist3", "soil_moist4"
]

# Maps an int to a cardinal (wind) direction.
winds = {
    0   : 'N', 
    1   : 'NNE', 
    2   : 'NE', 
    3   : 'ENE', 
    4   : 'E', 
    5   : 'ESE', 
    6   : 'SE',
    7   : 'SSE', 
    8   : 'S', 
    9   : 'SSW', 
    10  : 'SW', 
    11  : 'WSW', 
    12  : 'W', 
    13  : 'WNW',
    14  : 'NW', 
    15  : 'WNW', 
    255 : 'DASH'
}



# This dictionary maps an integer "weather forecast" to the corresponding
# forecast string.  
forecast = {
    0   : "Mostly clear and cooler.",
    1   : "Mostly clear with little temperature change.",
    2   : "Mostly clear for 12 hours with little temperature change.",
    3   : "Mostly clear for 12 to 24 hours and cooler.",
    4   : "Mostly clear with little temperature change.",
    5   : "Partly cloudy and cooler.",
    6   : "Partly cloudy with little temperature change.",
    7   : "Partly cloudy with little temperature change.",
    8   : "Mostly clear and warmer.",
    9   : "Partly cloudy with little temperature change.",
    10  : "Partly cloudy with little temperature change.",
    11  : "Mostly clear with little temperature change.",
    12  : "Increasing clouds and warmer. Precipitation possible within 24 to 48 hours.",
    13  : "Partly cloudy with little temperature change.",
    14  : "Mostly clear with little temperature change.",
    15  : "Increasing clouds with little temperature change. Precipitation possible within 24 hours.",
    16  : "Mostly clear with little temperature change.",
    17  : "Partly cloudy with little temperature change.",
    18  : "Mostly clear with little temperature change.",
    19  : "Increasing clouds with little temperature change. Precipitation possible within 12 hours.",
    20  : "Mostly clear with little temperature change.",
    21  : "Partly cloudy with little temperature change.",
    22  : "Mostly clear with little temperature change.",
    23  : "Increasing clouds and warmer. Precipitation possible within 24 hours.",
    24  : "Mostly clear and warmer. Increasing winds.",
    25  : "Partly cloudy with little temperature change.",
    26  : "Mostly clear with little temperature change.",
    27  : "Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.",
    28  : "Mostly clear and warmer. Increasing winds.",
    29  : "Increasing clouds and warmer.",
    30  : "Partly cloudy with little temperature change.",
    31  : "Mostly clear with little temperature change.",
    32  : "Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.",
    33  : "Mostly clear and warmer. Increasing winds.",
    34  : "Increasing clouds and warmer.",
    35  : "Partly cloudy with little temperature change.",
    36  : "Mostly clear with little temperature change.",
    37  : "Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.",
    38  : "Partly cloudy with little temperature change.",
    39  : "Mostly clear with little temperature change.",
    40  : "Mostly clear and warmer. Precipitation possible within 48 hours.",
    41  : "Mostly clear and warmer.",
    42  : "Partly cloudy with little temperature change.",
    43  : "Mostly clear with little temperature change.",
    44  : "Increasing clouds with little temperature change. Precipitation possible within 24 to 48 hours.",
    45  : "Increasing clouds with little temperature change.",
    46  : "Partly cloudy with little temperature change.",
    47  : "Mostly clear with little temperature change.",
    48  : "Increasing clouds and warmer. Precipitation possible within 12 to 24 hours.",
    49  : "Partly cloudy with little temperature change.",
    50  : "Mostly clear with little temperature change.",
    51  : "Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.",
    52  : "Partly cloudy with little temperature change.",
    53  : "Mostly clear with little temperature change.",
    54  : "Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.",
    55  : "Partly cloudy with little temperature change.",
    56  : "Mostly clear with little temperature change.",
    57  : "Increasing clouds and warmer. Precipitation possible within 6 to 12 hours.",
    58  : "Partly cloudy with little temperature change.",
    59  : "Mostly clear with little temperature change.",
    60  : "Increasing clouds and warmer. Precipitation possible within 6 to 12 hours. Windy.",
    61  : "Partly cloudy with little temperature change.",
    62  : "Mostly clear with little temperature change.",
    63  : "Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.",
    64  : "Partly cloudy with little temperature change.",
    65  : "Mostly clear with little temperature change.",
    66  : "Increasing clouds and warmer. Precipitation possible within 12 hours.",
    67  : "Partly cloudy with little temperature change.",
    68  : "Mostly clear with little temperature change.",
    69  : "Increasing clouds and warmer. Precipitation likley.",
    70  : "Clearing and cooler. Precipitation ending within 6 hours.",
    71  : "Partly cloudy with little temperature change.",
    72  : "Clearing and cooler. Precipitation ending within 6 hours.",
    73  : "Mostly clear with little temperature change.",
    74  : "Clearing and cooler. Precipitation ending within 6 hours.",
    75  : "Partly cloudy and cooler.",
    76  : "Partly cloudy with little temperature change.",
    77  : "Mostly clear and cooler.",
    78  : "Clearing and cooler. Precipitation ending within 6 hours.",
    79  : "Mostly clear with little temperature change.",
    80  : "Clearing and cooler. Precipitation ending within 6 hours.",
    81  : "Mostly clear and cooler.",
    82  : "Partly cloudy with little temperature change.",
    83  : "Mostly clear with little temperature change.",
    84  : "Increasing clouds with little temperature change. Precipitation possible within 24 hours.",
    85  : "Mostly cloudy and cooler. Precipitation continuing.",
    86  : "Partly cloudy with little temperature change.",
    87  : "Mostly clear with little temperature change.",
    88  : "Mostly cloudy and cooler. Precipitation likely.",
    89  : "Mostly cloudy with little temperature change. Precipitation continuing.",
    90  : "Mostly cloudy with little temperature change. Precipitation likely.",
    91  : "Partly cloudy with little temperature change.",
    92  : "Mostly clear with little temperature change.",
    93  : "Increasing clouds and cooler. Precipitation possible and windy within 6 hours.",
    94  : "Increasing clouds with little temperature change. Precipitation possible and windy within 6 hours.",
    95  : "Mostly cloudy and cooler. Precipitation continuing. Increasing winds.",
    96  : "Partly cloudy with little temperature change.",
    97  : "Mostly clear with little temperature change.",
    98  : "Mostly cloudy and cooler. Precipitation likely. Increasing winds.",
    99  : "Mostly cloudy with little temperature change. Precipitation continuing. Increasing winds.",
    100 : "Mostly cloudy with little temperature change. Precipitation likely. Increasing winds.",
    101 : "Partly cloudy with little temperature change.",
    102 : "Mostly clear with little temperature change.",
    103 : "Increasing clouds and cooler. Precipitation possible within 12 to 24 hours possible wind shift to the W NW or N.",
    104 : "Increasing clouds with little temperature change. Precipitation possible within 12 to 24 hours possible wind shift to the W NW or N.",
    105 : "Partly cloudy with little temperature change.",
    106 : "Mostly clear with little temperature change.",
    107 : "Increasing clouds and cooler. Precipitation possible within 6 hours possible wind shift to the W NW or N.",
    108 : "Increasing clouds with little temperature change. Precipitation possible within 6 hours possible wind shift to the W NW or N.",
    109 : "Mostly cloudy and cooler. Precipitation ending within 12 hours possible wind shift to the W NW or N.",
    110 : "Mostly cloudy and cooler. Possible wind shift to the W NW or N.",
    111 : "Mostly cloudy with little temperature change. Precipitation ending within 12 hours possible wind shift to the W NW or N.",
    112 : "Mostly cloudy with little temperature change. Possible wind shift to the WNW or N.",
    113 : "Mostly cloudy and cooler. Precipitation ending within 12 hours possible wind shift to the W NW or N.",
    114 : "Partly cloudy with little temperature change.",
    115 : "Mostly clear with little temperature change.",
    116 : "Mostly cloudy and cooler. Precipitation possible within 24 hours possible wind shift to the W NW or N.",
    117 : "Mostly cloudy with little temperature change. Precipitation ending within 12 hours possible wind shift to the W NW or N.",
    118 : "Mostly cloudy with little temperature change. Precipitation possible within 24 hours possible wind shift to the W NW or N.",
    119 : "Clearing cooler and windy. Precipitation ending within 6 hours.",
    120 : "Clearing cooler and windy.",
    121 : "Mostly cloudy and cooler. Precipitation ending within 6 hours. Windy with possible wind shift to the W NW or N.",
    122 : "Mostly cloudy and cooler. Windy with possible wind shift to the W NW or N.",
    123 : "Clearing cooler and windy.",
    124 : "Partly cloudy with little temperature change.",
    125 : "Mostly clear with little temperature change.",
    126 : "Mostly cloudy with little temperature change. Precipitation possible within 12 hours. Windy.",
    127 : "Partly cloudy with little temperature change.",
    128 : "Mostly clear with little temperature change.",
    129 : "Increasing clouds and cooler. Precipitation possible within 12 hours possibly heavy at times. Windy.",
    130 : "Mostly cloudy and cooler. Precipitation ending within 6 hours. Windy.",
    131 : "Partly cloudy with little temperature change.",
    132 : "Mostly clear with little temperature change.",
    133 : "Mostly cloudy and cooler. Precipitation possible within 12 hours. Windy.",
    134 : "Mostly cloudy and cooler. Precipitation ending in 12 to 24 hours.",
    135 : "Mostly cloudy and cooler.",
    136 : "Mostly cloudy and cooler. Precipitation continuing possible heavy at times. Windy.",
    137 : "Partly cloudy with little temperature change.",
    138 : "Mostly clear with little temperature change.",
    139 : "Mostly cloudy and cooler. Precipitation possible within 6 to 12 hours. Windy.",
    140 : "Mostly cloudy with little temperature change. Precipitation continuing possibly heavy at times. Windy.",
    141 : "Partly cloudy with little temperature change.",
    142 : "Mostly clear with little temperature change.",
    143 : "Mostly cloudy with little temperature change. Precipitation possible within 6 to 12 hours. Windy.",
    144 : "Partly cloudy with little temperature change.",
    145 : "Mostly clear with little temperature change.",
    146 : "Increasing clouds with little temperature change. Precipitation possible within 12 hours possibly heavy at times. Windy.",
    147 : "Mostly cloudy and cooler. Windy.",
    148 : "Mostly cloudy and cooler. Precipitation continuing possibly heavy at times. Windy.",
    149 : "Partly cloudy with little temperature change.",
    150 : "Mostly clear with little temperature change.",
    151 : "Mostly cloudy and cooler. Precipitation likely possibly heavy at times. Windy.",
    152 : "Mostly cloudy with little temperature change. Precipitation continuing possibly heavy at times. Windy.",
    153 : "Mostly cloudy with little temperature change. Precipitation likely possibly heavy at times. Windy.",
    154 : "Partly cloudy with little temperature change.",
    155 : "Mostly clear with little temperature change.",
    156 : "Increasing clouds and cooler. Precipitation possible within 6 hours. Windy.",
    157 : "Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy",
    158 : "Increasing clouds and cooler. Precipitation continuing. Windy with possible wind shift to the W NW or N.",
    159 : "Partly cloudy with little temperature change.",
    160 : "Mostly clear with little temperature change.",
    161 : "Mostly cloudy and cooler. Precipitation likely. Windy with possible wind shift to the W NW or N.",
    162 : "Mostly cloudy with little temperature change. Precipitation continuing. Windy with possible wind shift to the W NW or N.",
    163 : "Mostly cloudy with little temperature change. Precipitation likely. Windy with possible wind shift to the W NW or N.",
    164 : "Increasing clouds and cooler. Precipitation possible within 6 hours. Windy with possible wind shift to the W NW or N.",
    165 : "Partly cloudy with little temperature change.",
    166 : "Mostly clear with little temperature change.",
    167 : "Increasing clouds and cooler. Precipitation possible within 6 hours possible wind shift to the W NW or N.",
    168 : "Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy with possible wind shift to the W NW or N.",
    169 : "Increasing clouds with little temperature change. Precipitation possible within 6 hours possible wind shift to the W NW or N.",
    170 : "Partly cloudy with little temperature change.",
    171 : "Mostly clear with little temperature change.",
    172 : "Increasing clouds and cooler. Precipitation possible within 6 hours. Windy with possible wind shift to the W NW or N.",
    173 : "Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy with possible wind shift to the W NW or N.",
    174 : "Partly cloudy with little temperature change.",
    175 : "Mostly clear with little temperature change.",
    176 : "Increasing clouds and cooler. Precipitation possible within 12 to 24 hours. Windy with possible wind shift to the W NW or N.",
    177 : "Increasing clouds with little temperature change. Precipitation possible within 12 to 24 hours. Windy with possible wind shift to the W NW or N.",
    178 : "Mostly cloudy and cooler. Precipitation possibly heavy at times and ending within 12 hours. Windy with possible wind shift to the W NW or N.",
    179 : "Partly cloudy with little temperature change.",
    180 : "Mostly clear with little temperature change.",
    181 : "Mostly cloudy and cooler. Precipitation possible within 6 to 12 hours possibly heavy at times. Windy with possible wind shift to the W NW or N.",
    182 : "Mostly cloudy with little temperature change. Precipitation ending within 12 hours. Windy with possible wind shift to the W NW or N.",
    183 : "Mostly cloudy with little temperature change. Precipitation possible within 6 to 12 hours possibly heavy at times. Windy with possible wind shift to the W NW or N.",
    184 : "Mostly cloudy and cooler. Precipitation continuing.",
    185 : "Partly cloudy with little temperature change.",
    186 : "Mostly clear with little temperature change.",
    187 : "Mostly cloudy and cooler. Precipitation likely. Windy with possible wind shift to the W NW or N.",
    188 : "Mostly cloudy with little temperature change. Precipitation continuing.",
    189 : "Mostly cloudy with little temperature change. Precipitation likely.",
    190 : "Partly cloudy with little temperature change.",
    191 : "Mostly clear with little temperature change.",
    192 : "Mostly cloudy and cooler. Precipitation possible within 12 hours possibly heavy at times. Windy.",
    193 : "FORECAST REQUIRES 3 HOURS OF RECENT DATA",
    194 : "Mostly clear and cooler.",
    195 : "Mostly clear and cooler.",
    196 : "Mostly clear and cooler.",
    200 : "Unknown forecast rule.",
}
