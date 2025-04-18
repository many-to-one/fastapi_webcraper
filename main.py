from fastapi import FastAPI, BackgroundTasks 
from fastapi.responses import HTMLResponse
import subprocess
import pandas as pd
import plotly.express as px


app = FastAPI()

@app.get("/scrape/{spider_name}") 
async def run_spider(spider_name: str, background_tasks: BackgroundTasks): 

    SCRAPY_PROJECT_PATH = "./amz"
    print('SCRAPY_PROJECT_PATH', SCRAPY_PROJECT_PATH)

    command = ["scrapy", "crawl", spider_name]
    background_tasks.add_task(subprocess.Popen, command, cwd=SCRAPY_PROJECT_PATH) 
    return {"message": f"Started spider {spider_name}"}


@app.get('/')
async def root():

    df = pd.read_excel("templates/products.xlsx")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    fig = px.bar(df.nlargest(10, "price"), x="title", y="price", color="rating", title="Top 10 Most Expensive Products")

    content = fig.to_html(full_html=True)

    return HTMLResponse(content=content)