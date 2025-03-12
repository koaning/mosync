import marimo

__generated_with = "0.11.17"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import asyncio
    from mosync import async_map_with_retry
    return async_map_with_retry, asyncio, mo


@app.cell
def _(asyncio):
    async def delayed_identity(x):
        await asyncio.sleep(1)
        return x
    return (delayed_identity,)


@app.cell
async def _(async_map_with_retry, delayed_identity):
    results = await async_map_with_retry(
        range(200), 
        delayed_identity, 
        max_concurrency=10, 
        description="Showing a simple demo"
    )
    return (results,)


@app.cell
def _(results):
    len(results)
    return


@app.cell
def _(results):
    results[0]
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
