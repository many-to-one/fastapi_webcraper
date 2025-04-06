from fastapi import FastAPI, BackgroundTasks 
import subprocess


app = FastAPI()

@app.get("/scrape/{spider_name}") 
async def run_spider(spider_name: str, background_tasks: BackgroundTasks): 

    SCRAPY_PROJECT_PATH = "./amz"
    print('SCRAPY_PROJECT_PATH', SCRAPY_PROJECT_PATH)

    command = ["scrapy", "crawl", spider_name]
    background_tasks.add_task(subprocess.Popen, command, cwd=SCRAPY_PROJECT_PATH) 
    return {"message": f"Started spider {spider_name}"}


# @app.get('/')
# async def root():
#     return {'message': 'Hello World!'}