from fastapi import FastAPI, BackgroundTasks, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from urllib.parse import unquote, quote
import subprocess
import pandas as pd
import plotly.express as px


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request, response=HTMLResponse):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"id": id}
    )

@app.post("/scrape") 
async def run_spider(background_tasks: BackgroundTasks, title: str = Form(...), category: str = Form(...)): 

    decoded_url = f"https://www.amazon.pl/s?k={title}&i={category}"

    # Decode URL from FastAPI path
    # decoded_url = unquote(url)


    print(f"Decoded URL: {decoded_url}")
    spider_name = "amazon"

    SCRAPY_PROJECT_PATH = "./amz"
    print('SCRAPY_PROJECT_PATH', SCRAPY_PROJECT_PATH)

    # command = ["scrapy", "crawl", spider_name]

    # Pass the URL as an argument to the spider
    command = ["scrapy", "crawl", spider_name, "-a", f"url={decoded_url}"]

    background_tasks.add_task(subprocess.Popen, command, cwd=SCRAPY_PROJECT_PATH) 
    return {"message": f"Started spider {spider_name}"}


@app.get('/vis')
async def visualization():

    df = pd.read_excel("amz/scraped_offers.xlsx")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    fig = px.bar(df.nlargest(20, "price"), y="title", x="price", color="price", title="Top 10 Most Expensive Products")
    # fig = px.bar(df.nlargest(10, "price"), 
    #          y="title", x="price", color="rating",
    #          title="Top 10 Most Expensive Products",
    #          category_orders={"title": df.nlargest(10, "price")["title"].tolist()[::-1]})



    content = fig.to_html(full_html=True)

    return HTMLResponse(content=content)