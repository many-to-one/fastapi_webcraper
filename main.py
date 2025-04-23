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
async def run_spider(background_tasks: BackgroundTasks, title: str = Form(...), category: str = Form(...), category_name: str = Form(...)): 

    print(' ******************************* title ******************************* ', title)

    if title == "":
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
    command = ["scrapy", "crawl", spider_name, "-a", f"url={decoded_url}", "-a", f"category_name={category_name}"]

    background_tasks.add_task(subprocess.Popen, command, cwd=SCRAPY_PROJECT_PATH) 
    return {"message": f"Started spider {spider_name}"}


@app.get('/vis')
async def visualization():

    df = pd.read_excel("amz/scraped_offers.xlsx")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["short_title"] = df["title"].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)

    fig = px.bar(
        df, #.nlargest("price"),
        y="short_title", 
        x="price", 
        color="price", 
        hover_data={"short_title": False, "title": True},
        # title="Top 10 Most Expensive Products"
    )

    content = fig.to_html(full_html=True)

    return HTMLResponse(content=content)