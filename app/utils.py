import asyncio

async def run_with_concurrency_limit(coroutines, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def wrapper(coro):
        async with semaphore:
            return await coro
            
    return await asyncio.gather(
        *(wrapper(coro) for coro in coroutines),
        return_exceptions=True
    )

def validate_config_instances(config: dict, instances: int):
    if len(config.get("instances", [])) < instances or len(config.get("instances", [])) > instances:
        raise ValueError(f"Config requires {instances} instances, but has {len(config.get('instances', []))}")
