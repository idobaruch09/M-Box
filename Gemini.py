from google import genai
import time

key=""
with open("key.txt","r") as f:
    key=f.readlines()[0]

def user_request(request):
    try:
        client = genai.Client(api_key=key)
        request += ".\nDont make the answer too long."
        response = client.models.generate_content(model="gemini-2.5-flash", contents=request)
        print(response.text)
        return 0, response.text
    except Exception as e:
        print(e)
        if "RESOURCE_EXHAUSTED" in e:
            return 1, "App reached limit, try again later."

def search_links(txt):
    try:
        client = genai.Client(api_key=key)
        request = "\"" + txt + "\"\n\nSearch for real links, answer in the format of:\nlink1,link2,link3...\n dont add links that dont appear, even if there is just one. make sure all chars are actually related. think, make sure that you are right, and just then answer."
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=request)
        print(response.text)
        return response.text
    except Exception as e:
        print(e)
        if "RESOURCE_EXHAUSTED" in str(e):
            time.sleep(60)
            return search_links(txt)

#search_links("hihttps://il.linkedin.com/company/links-artificial-intelligencewhatsuphttp://httpforever.com/?yesssssshttps://holeio.com/ssshttps://he.wikipedia.org/wiki/%D7%99%D7%95%D7%98%D7%99%D7%95%D7%91s")


