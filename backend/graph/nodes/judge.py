MAX_RETRIES = 2

def check_loop_limit(loop_count: int) -> bool:
    return loop_count >= MAX_RETRIES
