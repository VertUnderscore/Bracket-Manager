timezone_map = { # Thanks ChatGPT!!! I was not about to type this out all by myself.
    # North America (including DST handling)
    "EST": "America/New_York",  # Eastern Standard Time (UTC-5)
    "EDT": "America/New_York",  # Eastern Daylight Time (UTC-4)
    "ET": "America/New_York",   # Eastern Time, auto-switches based on DST
    "CST": "America/Chicago",   # Central Standard Time (UTC-6)
    "CDT": "America/Chicago",   # Central Daylight Time (UTC-5)
    "CT": "America/Chicago",    # Central Time, auto-switches based on DST
    "MST": "America/Denver",    # Mountain Standard Time (UTC-7)
    "MDT": "America/Denver",    # Mountain Daylight Time (UTC-6)
    "MT": "America/Denver",     # Mountain Time, auto-switches based on DST
    "PST": "America/Los_Angeles",  # Pacific Standard Time (UTC-8)
    "PDT": "America/Los_Angeles",  # Pacific Daylight Time (UTC-7)
    "PT": "America/Los_Angeles",   # Pacific Time, auto-switches based on DST
    "AST": "America/Puerto_Rico",  # Atlantic Standard Time (UTC-4)
    "NST": "America/St_Johns",     # Newfoundland Standard Time (UTC-3:30)

    # Europe
    "GMT": "Etc/GMT",            # Greenwich Mean Time (UTC+0)
    "BST": "Europe/London",       # British Summer Time (UTC+1)
    "CET": "Europe/Paris",        # Central European Time (UTC+1)
    "CEST": "Europe/Paris",       # Central European Summer Time (UTC+2)
    "EET": "Europe/Athens",       # Eastern European Time (UTC+2)
    "EEST": "Europe/Athens",      # Eastern European Summer Time (UTC+3)
    "WET": "Europe/Lisbon",       # Western European Time (UTC+0)
    "WEST": "Europe/Lisbon",      # Western European Summer Time (UTC+1)
    "MSK": "Europe/Moscow",       # Moscow Standard Time (UTC+3)

    # Asia
    "IST": "Asia/Kolkata",        # Indian Standard Time (UTC+5:30)
    "PKT": "Asia/Karachi",        # Pakistan Standard Time (UTC+5)
    "ICT": "Asia/Bangkok",        # Indochina Time (UTC+7)
    "WIB": "Asia/Jakarta",        # Western Indonesia Time (UTC+7)
    "WIT": "Asia/Jayapura",       # Eastern Indonesia Time (UTC+9)
    "JST": "Asia/Tokyo",          # Japan Standard Time (UTC+9)
    "KST": "Asia/Seoul",          # Korea Standard Time (UTC+9)
    "CST": "Asia/Shanghai",       # China Standard Time (UTC+8)
    "HKT": "Asia/Hong_Kong",      # Hong Kong Time (UTC+8)
    "SGT": "Asia/Singapore",      # Singapore Time (UTC+8)

    # Australia & Oceania
    "AWST": "Australia/Perth",    # Australian Western Standard Time (UTC+8)
    "ACST": "Australia/Darwin",   # Australian Central Standard Time (UTC+9:30)
    "AEST": "Australia/Sydney",   # Australian Eastern Standard Time (UTC+10)
    "AEDT": "Australia/Sydney",   # Australian Eastern Daylight Time (UTC+11)
    "NZST": "Pacific/Auckland",   # New Zealand Standard Time (UTC+12)
    "NZDT": "Pacific/Auckland",   # New Zealand Daylight Time (UTC+13)
    "FJT": "Pacific/Fiji",        # Fiji Time (UTC+12)
    "HST": "Pacific/Honolulu",    # Hawaii Standard Time (UTC-10)

    # Africa
    "CAT": "Africa/Harare",       # Central Africa Time (UTC+2)
    "EAT": "Africa/Nairobi",      # East Africa Time (UTC+3)
    "SAST": "Africa/Johannesburg",  # South Africa Standard Time (UTC+2)
    "WAT": "Africa/Lagos",        # West Africa Time (UTC+1)

    # Middle East
    "IRST": "Asia/Tehran",        # Iran Standard Time (UTC+3:30)
    "GST": "Asia/Dubai",          # Gulf Standard Time (UTC+4)
    "AST": "Asia/Riyadh",         # Arabian Standard Time (UTC+3)

    # UTC and Offsets
    "UTC": "UTC",
    "UCT": "UTC",
    "Z": "UTC",
}