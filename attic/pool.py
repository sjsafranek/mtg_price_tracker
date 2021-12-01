
from concurrent.futures import ProcessPoolExecutor as PoolExecutor

def execute(clbk, jobs=[], workers=4):
    with PoolExecutor(max_workers=4) as executor:
        for result in executor.map(clbk, jobs):
            yield result
