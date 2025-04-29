import time
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


@app.get('/visualization/{category}')
async def visualization(request: Request, category: str, search: str = Query(None), filter_by: str = Query(None), date: str = Query(None)):

    date_ = None
    if date == 'one':
        date_ = time.strftime('%Y-%m-%d')
    DATA_DIR = f"amz/amz/products/{category}/{date_}"
    
    filename = f"{category}.xlsx"
    file_path = os.path.join(DATA_DIR, filename)
    print(' ******************** DATA_DIR ****************** ', file_path)

    if not os.path.exists(file_path):
        return HTMLResponse(content=f"<h1>File not found: {filename}</h1>", status_code=404)

    df = pd.read_excel(file_path)

    df["index"] = range(len(df))

    # Ensure price is numeric
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)

    # Ensure review is numeric
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
    # df["short_title"] = df["title"].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
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



@app.get("/whole-amz-scraping")
async def start_scraping():
    process = CrawlerProcess()

    batch_url = "https://www.amazon.pl/s?i="

    start_urls_batch_1 = [f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={i}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank' for i in range(1, 31)]
    start_urls_batch_2 = [f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={i}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank' for i in range(1, 31)]
    
    # start_urls_batch_1 = [
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={1}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={2}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={3}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={4}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={5}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={6}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={7}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={8}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={9}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={10}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={11}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={12}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={13}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={14}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={15}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={16}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={17}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={18}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={19}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861477031&page={20}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    # #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861477031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861473031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861471031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861480031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861468031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861472031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861464031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861467031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861465031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861476031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861469031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861475031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861474031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861479031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861478031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861470031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861466031",
    #     "https://www.amazon.pl/s?i=toys&rh=n%3A20659660031%2Cn%3A20861484031",
    #     "https://www.amazon.pl/s?i=fashion&rh=n%3A20849017031",
    #     "https://www.amazon.pl/s?i=baby&rh=n%3A20806748031",
    #     "https://www.amazon.pl/s?i=baby&rh=n%3A20806764031",
    #     "https://www.amazon.pl/s?i=baby&rh=n%3A20806749031",
    #     "https://www.amazon.pl/s?i=baby&rh=n%3A20806743031",
    #     "https://www.amazon.pl/s?i=baby&rh=n%3A20806747031",
    #     "https://www.amazon.pl/s?i=baby&rh=n%3A20806745031",
    #     "https://www.amazon.pl/s?i=baby&rh=n%3A20806740031",
    # ]

    # start_urls_batch_2 = [
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={1}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={2}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={3}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={4}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={5}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={6}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={7}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={8}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={9}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={10}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={11}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={12}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={13}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={14}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={15}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={16}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={17}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={18}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={19}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',
    #     f'{batch_url}toys&rh=n%3A20659660031%2Cn%3A20861473031&page={20}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank',

    #     "https://www.amazon.pl/s?i=home&rh=n%3A20853159031",
    #     "https://www.amazon.pl/s?i=home&rh=n%3A20853010031",
    #     "https://www.amazon.pl/s?i=home&rh=n%3A20853014031",
    #     "https://www.amazon.pl/s?i=home&rh=n%3A20852960031",
    #     "https://www.amazon.pl/s?i=home&rh=n%3A20852956031",
    #     "https://www.amazon.pl/s?i=home&rh=n%3A20852961031",
    #     "https://www.amazon.pl/s?i=home&rh=n%3A20852957031",
    #     "https://www.amazon.pl/s?i=home&rh=n%3A20852964031",
    #     "https://www.amazon.pl/s?i=home&rh=n%3A20852963031",
    #     "https://www.amazon.pl/s?i=home&rh=n%3A20852962031",
    #     "https://www.amazon.pl/s?i=home-improvement&rh=n%3A20784174031",
    #     "https://www.amazon.pl/s?i=home-improvement&rh=n%3A20784170031",
    #     "https://www.amazon.pl/s?i=home-improvement&rh=n%3A20784171031",
    #     "https://www.amazon.pl/s?i=home-improvement&rh=n%3A20784162031",
    #     "https://www.amazon.pl/s?i=home-improvement&rh=n%3A20784164031",
    #     "https://www.amazon.pl/s?i=home-improvement&rh=n%3A20784169031",
    #     "https://www.amazon.pl/s?i=garden&rh=n%3A20855078031",
    #     "https://www.amazon.pl/s?i=garden&rh=n%3A20855086031",
    #     "https://www.amazon.pl/s?i=garden&rh=n%3A20855088031",
    #     "https://www.amazon.pl/s?i=garden&rh=n%3A20855076031",

    # ]


    # Launch 2 different crawls with different start URLs
    process.crawl(WholeSpider, start_urls=start_urls_batch_1)
    process.crawl(WholeSpider, start_urls=start_urls_batch_2)

    # # You can dynamically generate batches like:
    # urls = get_urls_from_excel("offers.xlsx")
    # batches = [urls[i:i + 10] for i in range(0, len(urls), 10)]

    # for batch in batches:
    #     process.crawl(MySpider, start_urls=batch)

    process.start()

    return {"status": "Scraping started"}