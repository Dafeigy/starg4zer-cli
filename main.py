from fastapi import FastAPI
import aiohttp, asyncio
import requests
from bs4 import BeautifulSoup
import lxml,json
import os

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

app = FastAPI()
PROXY_ON = False
SAVE_LOCAL_JSON = False
null = None

if PROXY_ON:
    proxy = {"https":"127.0.0.1:7890",'http':"127.0.0.1:7890"}
else:
    proxy = {}

def get_params(GITHUB_USER):
    url = f"https://github.com/{GITHUB_USER}?tab=stars"
    req = requests.get(url, 
                       headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0","content-type": "text/html; charset=utf-8"},
                       proxies=proxy)
    soup=BeautifulSoup(req.text, 'lxml')
    stars_num = soup.find("a", attrs={"aria-current":"page"}).find("span",class_="Counter").get("title").replace(",","")
    user_id = soup.find("a", attrs={"itemprop": "image"}).get("href").replace("https://avatars.githubusercontent.com/u/",'')[:-4]
    return user_id, int(stars_num)//100+1

async def fetch_with_(url, headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()

async def fetch_multiple_urls(github_user, headers):
    user_id, stars_num = get_params(github_user)
    urls = [
    f"https://api.github.com/user/{user_id}/starred?per_page=100&page={i}"
    for i in range(1, stars_num+1)
]
    tasks = [fetch_with_(url, headers) for url in urls]
    return await asyncio.gather(*tasks)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/user/{user_name}")
async def get_info(user_name: str):
    user_id, page_num = get_params(user_name)
    return {
        "user_id": user_id,
        "num_page": page_num
        }
@app.get("/star/{user_name}")
async def get_repos(user_name: str):
    headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": GITHUB_TOKEN,
    "X-GitHub-Api-Version": "2022-11-28",
    }
    ori = await fetch_multiple_urls(user_name, headers)
    results = [subitem for item in ori for subitem in item]
    second_results = [
        {
            'reponame':each['full_name'],
            'clone_url':each['html_url'],
            'update_date':each['updated_at'],
            'avatar_url':each['owner']['avatar_url'],
            'star_count':each['stargazers_count'],
            'fork_count':each['forks'],
            'lang':each['language'],
            'desc':each['description']
         }
         for each in results
        ]
    if SAVE_LOCAL_JSON:
        with open (f'{user_name}.txt','w', encoding='utf-8') as f:
            f.writelines(str(second_results))
    return second_results
    