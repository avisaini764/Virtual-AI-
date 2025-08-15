import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")



# url = ('https://newsapi.org/v2/top-headlines?'
#        'country=us&'
#        'apiKey=734d256bd433455086c1598666239402')
# response = requests.get(url)
# print (response.json())