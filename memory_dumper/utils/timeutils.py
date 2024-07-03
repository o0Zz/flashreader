import monotonic

def TIME_MS():
	return int(round(monotonic.time.time() * 1000))
	
def TIMER_START_MS():
	return TIME_MS()

def TIMER_ELAPSED_MS(aTime):
	return (TIME_MS() - aTime)