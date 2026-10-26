#will be used for memory information
def bytes_conversion(value,suffix="B")->str:
    if value is None:
        return "N/A"
    value=float(value)
    for unit in ("","K","M","G","T","P"):
        if abs(value)<1024:
            return f"{value:.2f}{unit}{suffix}"
        value/=1024
    return f"{value:.2f}EB"

#used for any time related information that itself doesn't have a good conversion
def seconds_conversion(seconds)->str:
    if seconds is None or seconds<0:
        return "N/A"
    seconds=int(seconds)
    days,remainder=divmod(seconds,86_400)
    hours,remainder=divmod(remainder,3_600)
    minutes,seconds=divmod(remainder,60)
    parts=[]
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)
