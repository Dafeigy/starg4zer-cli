from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import aiohttp, asyncio
import requests
from bs4 import BeautifulSoup
import lxml,json
import os

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，可以根据需要进行调整
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有头部信息
)
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
    
@app.get("/test_search")
async def search_results():
    return [{'reponame': 'Zyphra/Zonos', 'clone_url': 'https://github.com/Zyphra/Zonos', 'update_date': '2025-02-19T07:30:46Z', 'avatar_url': 'https://avatars.githubusercontent.com/u/137229384?v=4', 'star_count': 4922, 'fork_count': 458, 'lang': 'Python', 'desc': 'Zonos-v0.1 is a leading open-weight text-to-speech model trained on more than 200k hours of varied multilingual speech, delivering expressiveness and quality on par with—or even surpassing—top TTS providers.'}, {'reponame': 'sdbds/Zonos-for-windows', 'clone_url': 'https://github.com/sdbds/Zonos-for-windows', 'update_date': '2025-02-19T07:18:55Z', 'avatar_url': 'https://avatars.githubusercontent.com/u/8085926?v=4', 'star_count': 262, 'fork_count': 27, 'lang': 'Python', 'desc': None}, {'reponame': 'e-p-armstrong/augmentoolkit', 'clone_url': 'https://github.com/e-p-armstrong/augmentoolkit', 'update_date': '2025-02-19T06:34:21Z', 'avatar_url': 'https://avatars.githubusercontent.com/u/64122766?v=4', 'star_count': 1301, 'fork_count': 174, 'lang': 'Python', 'desc': 'Convert Compute And Books Into Instruct-Tuning Datasets! Makes: QA, RP, Classifiers.'}, {'reponame': 'openai/CLIP', 'clone_url': 'https://github.com/openai/CLIP', 'update_date': '2025-02-19T07:11:55Z', 'avatar_url': 'https://avatars.githubusercontent.com/u/14957082?v=4', 'star_count': 27410, 'fork_count': 3440, 'lang': 'Jupyter Notebook', 'desc': 'CLIP (Contrastive Language-Image Pretraining),  Predict the most relevant text snippet given an image'}, {'reponame': 'openai/tiktoken', 'clone_url': 'https://github.com/openai/tiktoken', 'update_date': '2025-02-19T06:43:54Z', 'avatar_url': 'https://avatars.githubusercontent.com/u/14957082?v=4', 'star_count': 13435, 'fork_count': 944, 'lang': 'Python', 'desc': "tiktoken is a fast BPE tokeniser for use with OpenAI's models."}]