import time
from datetime import datetime, timedelta
from fastapi import FastAPI, BackgroundTasks, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from urllib.parse import unquote, quote
import subprocess, os
import pandas as pd
import plotly.express as px

from scrapy.crawler import CrawlerProcess
from amz.amz.spiders.whole_spider import WholeSpider


app = FastAPI()

DATA_DIR = "amz/products"

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/scr")
async def root(request: Request, response=HTMLResponse):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"id": id}
    )


@app.get('/')
async def visualization(request: Request,):

    # filename = 'amz/Zabawki elektroniczne.xlsx'
    category = "Zabawki elektroniczne"
    base_path = f"amz/amz/products/{category}/"
    # Get all date folders
    date_folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    valid_dates = [d for d in date_folders if d.count("-") == 2]
    latest_date = max(valid_dates, key=lambda x: datetime.strptime(x, "%Y-%m-%d"))

    DATA_DIR = f"amz/amz/products/{category}/{latest_date}"
    
    filename = f"{category}.xlsx"
    file_path = os.path.join(DATA_DIR, filename)

    df = pd.read_excel(file_path)
    df = df.head(100)

    df["index"] = range(len(df))

    # Ensure price is numeric
    # df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Ensure review is numeric
    # df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce")

    df["price"] = df["price"].astype(str).str.replace(r"\D", "", regex=True)  # Remove non-numeric characters
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

    # Ensure review is numeric
    # df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0)
    df["reviews"] = df["reviews"].astype(str).str.replace(r"\D", "", regex=True)  # Remove non-numeric characters
    df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0)

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


@app.get('/visualization/{category}')
async def visualization(
    request: Request, 
    category: str, 
    search: str = Query(None), 
    filter_by: str = Query(None), 
    ):

    # print(' ********************* DATE ******************** ', date)
    print(' ********************* category ******************** ', category)

    if category:
        base_path = f"amz/amz/products/{category}/"
        # Get all date folders
        date_folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        valid_dates = [d for d in date_folders if d.count("-") == 2]

        latest_date = max(valid_dates, key=lambda x: datetime.strptime(x, "%Y-%m-%d"))
        print(' ********************* latest_date ******************** ', latest_date)
    else:
        print(' ********************* no category ******************** ')

    DATA_DIR = f"amz/amz/products/{category}/{latest_date}"
    
    filename = f"{category}.xlsx"
    file_path = os.path.join(DATA_DIR, filename)
    print(' ******************** DATA_DIR ****************** ', file_path)

    if not os.path.exists(file_path):
        return HTMLResponse(content=f"<h1>File not found: {filename}</h1>", status_code=404)

    df = pd.read_excel(file_path)

    df["index"] = range(len(df))

    # Ensure price is numeric
    df["price"] = df["price"].astype(str).str.replace(r"\D", "", regex=True)  # Remove non-numeric characters
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

    # Ensure review is numeric
    df["reviews"] = df["reviews"].astype(str).str.replace(r"\D", "", regex=True)  # Remove non-numeric characters
    df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0)

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)

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
    df["short_title"] = df["title"].apply(lambda x: str(x)[:20] + "..." if isinstance(x, str) and len(x) > 20 else str(x))

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
        y=f"{filter_by}",
        color=f"{filter_by}",
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
            "category": category,
            "filename": filename.rstrip(".xlsx"),
        })



@app.get('/visualization-test/{category}')
async def visualization(
    request: Request, 
    category: str, 
    search: str = Query(None), 
    filter_by: str = Query(None), 
    date: str = Query(None), 
    ):

    print(' ********************* DATE ******************** ', date)
    print(' ********************* category ******************** ', category)

    date_ = None
    if date == "one" :
        date_ = time.strftime("%Y-%m-%d")

    if category:
        base_path = f"amz/amz/products/{category}/"
        # Get all date folders
        date_folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        valid_dates = [d for d in date_folders if d.count("-") == 2]

        latest_date = max(valid_dates, key=lambda x: datetime.strptime(x, "%Y-%m-%d"))
        print(' ********************* latest_date ******************** ', latest_date)
    else:
        print(' ********************* no category ******************** ')

    DATA_DIR = f"amz/amz/products/{category}/{latest_date}"
    
    filename = f"{category}.xlsx"
    file_path = os.path.join(DATA_DIR, filename)
    print(' ******************** DATA_DIR ****************** ', file_path)

    if not os.path.exists(file_path):
        return HTMLResponse(content=f"<h1>File not found: {filename}</h1>", status_code=404)

    df = pd.read_excel(file_path)

    df["index"] = range(len(df))

    # Ensure price is numeric
    df["price"] = df["price"].astype(str).str.replace(r"\D", "", regex=True)  # Remove non-numeric characters
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

    # Ensure review is numeric
    df["reviews"] = df["reviews"].astype(str).str.replace(r"\D", "", regex=True)  # Remove non-numeric characters
    df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0)

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)

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
    df["short_title"] = df["title"].apply(lambda x: str(x)[:20] + "..." if isinstance(x, str) and len(x) > 20 else str(x))

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
        y=f"{filter_by}",
        color=f"{filter_by}",
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
            "category": category,
            "filename": filename.rstrip(".xlsx"),
        })



"""
Create a strategy to call this function after end of scraping
to get date/category.xlsx file and extract all urls to scrape
the first_date_avaliability and record this date to the 
first_date_avaliability field.
"""
@app.get("/whole-amz-scraping/{category}")
async def start_scraping(
    request: Request, 
    category: str,
):

    if category:
        base_path = f"amz/amz/products/{category}/"
        # Get all date folders
        date_folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        valid_dates = [d for d in date_folders if d.count("-") == 2]

        latest_date = max(valid_dates, key=lambda x: datetime.strptime(x, "%Y-%m-%d"))
        print(' ********************* latest_date ******************** ', latest_date)
    else:
        print(' ********************* no category ******************** ')

    DATA_DIR = f"amz/amz/products/{category}/{latest_date}"
    
    filename = f"{category}.xlsx"
    file_path = os.path.join(DATA_DIR, filename)
    print(' ******************** DATA_DIR ****************** ', file_path)

    df = pd.read_excel(file_path)

    process = CrawlerProcess()

    df = pd.read_excel(file_path)
    urls = df["url"].dropna().tolist()

    if not urls:
        return {"error": "No URLs found in Excel."}

    batches = [urls]  # one batch with all URLs

    for batch in batches:
        process.crawl(WholeSpider, start_urls=batch, file_path=file_path)

    # batch_url = "https://www.amazon.pl/s?i="

    # start_urls_batch_1 = [f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={i}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank' for i in range(1, 31)]
    # start_urls_batch_2 = [f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={i}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank' for i in range(1, 31)]


    # # Launch 2 different crawls with different start URLs
    # process.crawl(WholeSpider, start_urls=start_urls_batch_1)
    # process.crawl(WholeSpider, start_urls=start_urls_batch_2)

    process.start()

    return {"status": "Scraping started"}