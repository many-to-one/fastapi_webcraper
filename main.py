from fastapi import FastAPI, BackgroundTasks, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from urllib.parse import unquote, quote
import subprocess, os
import pandas as pd
import plotly.express as px


app = FastAPI()

DATA_DIR = "amz"

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/scr")
async def root(request: Request, response=HTMLResponse):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"id": id}
    )


# @app.get("/")
# async def root(request: Request, response=HTMLResponse):
#     return templates.TemplateResponse(
#         request=request, name="bar.html"
#     )


@app.get('/')
async def visualization(request: Request,):

    filename = 'amz/Zabawki elektroniczne.xlsx'

    df = pd.read_excel(filename)
    df = df.head(100)

    df["index"] = range(len(df))

    # Ensure price is numeric
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Ensure review is numeric
    df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce")

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    df = df.sort_values(by="price", ascending=False)


    if df.empty:
        return templates.TemplateResponse("visualization.html", {
            "request": request,
            "plot": None,
            "items": "<h3>No data found.</h3>",
        })

    # Truncate long titles
    df["short_title"] = df["title"].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)

    # Scatter
    fig = px.scatter(
        df,
        x="price",
        y="short_title",
        color="index",
        hover_data={"title": True, "price": True, "short_title": False, "index": False, },
        size_max=50,
        labels={
            "short_title": "Tytuł",
            # "reviews": "Popularność",
            # "rating": "Ocena",
        },
        height=600
    )


    plot_html = fig.to_html(full_html=True)
    # table_html = df.to_html(classes="table table-striped", index=False, escape=False)
    items = df.to_dict(orient="records")

    return templates.TemplateResponse("visualization.html", {
            "request": request,
            "plot": plot_html,
            "items": items,
        })


@app.get("/scrape/{category}") 
async def run_spider(
    request: Request, 
    background_tasks: BackgroundTasks, 
    category: str,
    title: str = Query(None),
    category_name: str = Query(None),
    filter_by: str = Query(None),
    # title: str = Form(...), 
    # category: str = Form(...), 
    # category_name: str = Form(...),
    # filter_by: str = Form(...),
    ): 

    print(' ******************************* category ******************************* ', category)
    print(' ******************************* title ******************************* ', title)
    print(' ******************************* category_name ******************************* ', category_name)
    print(' ******************************* filter_by ******************************* ', filter_by)

    if title == None:
        decoded_url = f"https://www.amazon.pl/s?i={category}"
    else:
        decoded_url = f"https://www.amazon.pl/s?k={title}&i={category}"

    # Decode URL from FastAPI path
    # decoded_url = unquote(url)


    print(f"Decoded URL: {decoded_url}")
    spider_name = "amazon"

    SCRAPY_PROJECT_PATH = "./amz"
    print('SCRAPY_PROJECT_PATH', SCRAPY_PROJECT_PATH)

    # command = ["scrapy", "crawl", spider_name]

    # Pass the URL as an argument to the spider
    command = [
        "scrapy", "crawl", 
        spider_name,
        "-a", f"url={decoded_url}", 
        "-a", f"category_name={category_name}",
        "-a", f"filter_by={filter_by}",
        ]

    background_tasks.add_task(subprocess.Popen, command, cwd=SCRAPY_PROJECT_PATH) 
    return {"message": f"Started spider {spider_name}"}


@app.get('/visualization/{filename}')
async def visualization(request: Request, filename: str, search: str = Query(None), filter_by: str = Query(None)):

    file_path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(file_path):
        return HTMLResponse(content=f"<h1>File not found: {filename}</h1>", status_code=404)

    df = pd.read_excel(file_path)

    df["index"] = range(len(df))

    # Ensure price is numeric
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Ensure review is numeric
    df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce")

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # Sort by reviews in descending order (most reviewed first)
    # df = df.dropna(subset=["reviews"]).sort_values(by="reviews", ascending=False)
    df = df.sort_values(by=filter_by, ascending=False)



    # Filter by search keywords if provided
    if search:
        keywords = search.lower().split()
        df = df[df["title"].str.lower().apply(lambda title: any(word in title for word in keywords))]

    if df.empty:
        return templates.TemplateResponse("visualization.html", {
            "request": request,
            "plot": None,
            "items": "<h3>No data found.</h3>",
        })

    # Truncate long titles
    df["short_title"] = df["title"].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)

    # # Create chart
    # fig = px.bar(
    #     df,
    #     y="short_title", 
    #     x="price", 
    #     color="price", 
    #     hover_data={"short_title": False, "title": True},
    # )

    # Scatter
    fig = px.scatter(
        df,
        x="index",
        # y="short_title",
        y="reviews",
        color="reviews",
        hover_data={"title": True, "rating": True, "short_title": False, "index": False, },
        size_max=50,
        labels={
            "short_title": "Tytuł",
            "reviews": "Popularność",
            "rating": "Ocena",
        },
        height=600
    )


    plot_html = fig.to_html(full_html=True)
    # .xlsx table to html table:
    # table_html = df.to_html(classes="table table-striped", index=False, escape=False)
    items = df.to_dict(orient="records")

    return templates.TemplateResponse("visualization.html", {
            "request": request,
            "plot": plot_html,
            "items": items,
            # "filter_by": option,
            "filename": filename.rstrip(".xlsx"),
        })