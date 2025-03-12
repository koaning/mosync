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
def _(mo):
    mo.md("""
    ## Enter `mosync` 

    In this notebook we will explore a small utility that could help you run batches of async workfloads. We made this because it felt like a missing cog in a lot of LLM experiments that we do inside of marimo notebooks. Some LLM vendors do not provide a batch endpoint, in which case you are better off just sending batches of requests async. It will also work for many other use-cases, but this is what we had in mind when we made this. 

    So as a base example, lets pretend that we are making HTTP requests. The `delayed_identity` function can mimic this. 
    """)
    return


@app.cell
def _(asyncio):
    async def delayed_double(x):
        await asyncio.sleep(1)
        return x * 2
    return (delayed_double,)


@app.cell
def _(mo):
    mo.md("""
    You can pass this function to `async_map_with_retry` that comes from `mosync`. This function takes care of all the async/error/logging stuff for you and also gives you a pretty widget to look at while you are waiting.
    """)
    return


@app.cell
async def _(async_map_with_retry, delayed_double):
    results = await async_map_with_retry(
        range(200), 
        delayed_double, 
        max_concurrency=10, 
        description="Showing a simple demo"
    )
    return (results,)


@app.cell
def _(mo):
    mo.md("""
    The results are a list of `ProcessResult` objects. We have one for every input and these allow us to also log any errors that might have happened. Pay attention though! We do not guarantee the original order, so the items may have been shuffled around a bit.
    """)
    return


@app.cell
def _(results):
    len(results), results[0], results[1], results[2]
    return


@app.cell
def _(mo):
    mo.md("""Let's do one more demo that shows what errors might look like. There is a retry mechanic in the library that tries to help you out, but it's also good to see what happens when there are just too many bugs.""")
    return


@app.cell
def _(asyncio):
    import random 

    async def maybe_error(x):
        await asyncio.sleep(0.1)
        if random.random() < 0.25:
            raise ValueError("oh noes!")
        return x * 2
    return maybe_error, random


@app.cell
async def _(async_map_with_retry, maybe_error):
    err_results = await async_map_with_retry(
        range(200), 
        maybe_error, 
        max_concurrency=10, 
        max_retries=2,
        description="Showing a simple demo"
    )
    return (err_results,)


@app.cell
def _(mo):
    mo.md("""The retry mechanics can really help, but it's also great to have the errors available as an entry""")
    return


@app.cell
def _(err_results):
    [e for e in err_results if e.error]
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
