import requests
import json
try:
    from termcolor import colored
except:
    def colored(x):
        return x
import os
from msvcrt import getch

def getKey():
    firstChar = getch()
    if firstChar == b'\xe0':
        return {b"H": "up", b"P": "down", b"M": "right", b"K": "left"}[getch()]
    if firstChar == b'\x1b':
        return "esc"
    if firstChar == b'\r':
        return "enter"
    else:
        return firstChar

configs = {
    "consoleHeight": 20,
    "header": {'Authorization': 'Bearer YourSessionTokenHere'}
}
mangaFolder = os.path.join(os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__))), "manga_images")

os.system('color')

class MangaPreview:
    def __init__(self, text, id, index, title):
        self.text = text
        self.id = id
        self.index = index
        self.title = title
    def output(self):
        for line in self.text:
            print(line)

class MangaChapter:
    def __init__(self, text, chapter, data, hash, id):
        self.text = text
        self.chapter = chapter
        self.data = data
        self.hash = hash
        self.id = id
mangaResults = []

searchToken = input("Please enter a search token: ")
navigationIndex = 1
total = -1
while True:
    if navigationIndex > len(mangaResults):
        os.system('cls')
        print(colored('Fetching results...', 'cyan'))
        response = requests.get(url="https://api.mangadex.org/manga", headers=configs['header'],
                                params={'title': searchToken,
                                        'offset': navigationIndex-1}) #offset = 0
        dict_formatted = json.loads(response.text)
        mangaIndex = dict_formatted['offset'] + 1 # = 1
        total = dict_formatted['total']
        for result in dict_formatted['results']:
            manga_lines = []
            manga_lines.append(colored(result['data']['attributes']['title']['en'], 'blue', attrs=['bold']))
            manga_lines.append('Created at: ' + colored(result['data']['attributes']['createdAt'], 'green'))
            manga_lines.append('Updated at: ' + colored(result['data']['attributes']['updatedAt'], 'green'))
            manga_lines.append('Latest Chapter: ' + colored(result['data']['attributes']['lastChapter'], 'green'))
            manga_lines.append('Volumes: ' + colored(result['data']['attributes']['lastVolume'], 'green'))
            manga_lines.append('Status: ' + colored(result['data']['attributes']['status'], 'green'))
            manga_lines.append('Year: ' + colored(result['data']['attributes']['year'] or 'N/A', 'green'))
            manga_lines.append('Rating: ' + colored(result['data']['attributes']['year'] or 'N/A', 'cyan'))
            manga_lines.append(
                'Demographic: ' + colored(result['data']['attributes']['publicationDemographic'] or 'N/A', 'green'))
            manga_lines.append('Tags: ' + colored(
                ', '.join([x['attributes']['name']['en'] for x in result['data']['attributes']['tags']]), 'magenta',
                attrs=['dark']))
            manga_lines.append(
                'id: ' + colored(result['data']['id'], 'green')
            )

            mangaResults.append(MangaPreview(manga_lines, result['data']['id'], mangaIndex, result['data']['attributes']['title']['en']))
            mangaIndex += 1
    os.system('cls')
    obj = mangaResults[navigationIndex-1]
    print(colored('Showing result ' + str(obj.index) + " of " + str(total) + " total results.", 'green'))
    obj.output()


    userAction = getKey()
    if (userAction == "up" or userAction == "right") and navigationIndex < total:
        navigationIndex += 1
    elif (userAction == "down" or userAction == "left") and (navigationIndex > 1):
        navigationIndex -= 1
    elif userAction == "enter":
        os.system('cls')
        print(colored('Fetching results...', 'cyan'))
        response = requests.get(url="https://api.mangadex.org/manga/" + obj.id + "/feed",
                                headers=configs['header'],
                                params={
                                    'limit': 500})
        mangaChapters = []
        os.system('cls')
        for chapter in json.loads(response.text)["results"]:
            chNum = chapter["data"]["attributes"]["chapter"]
            volNum = chapter["data"]["attributes"]["volume"]
            title = chapter["data"]["attributes"]["title"]

            if not chNum:
                chNum = 0
            if not volNum:
                volNum = 0
            if not title:
                title = "No Title"
            text = colored("Chapter " + (chNum or "N/A") + ", Volume " + (volNum or "N/A") + ": ", "cyan") + colored((title or "N/A"), "white")
            try:
                mangaChapters.append(MangaChapter(text, float(chNum), chapter["data"]["attributes"]["data"], chapter["data"]["attributes"]["hash"], chapter["data"]["id"]))
            except:
                print(chapter)
                exit()
        mangaChapters = sorted(mangaChapters, key=lambda x: x.chapter)
        chapterNavigationIndex = 0
        while True:
            os.system('cls')
            print(colored('-->' + obj.title + '<--', 'yellow'))
            print('-' * len('-->' + obj.title + '<--'))
            for i in range( configs["consoleHeight"] * (chapterNavigationIndex//configs["consoleHeight"]), min(configs["consoleHeight"] * (chapterNavigationIndex//configs["consoleHeight"] + 1), len(mangaChapters))):
                if i == chapterNavigationIndex:
                    print("> " + mangaChapters[i].text)
                else:
                    print("  " + mangaChapters[i].text)

            userChapterAction = getKey()
            if (userChapterAction == "down") and chapterNavigationIndex < len(mangaChapters)-1:
                chapterNavigationIndex+=1
            elif (userChapterAction == "up") and chapterNavigationIndex > 0:
                chapterNavigationIndex-=1
            elif (userChapterAction == "right") and chapterNavigationIndex + configs["consoleHeight"] < len(mangaChapters):
                chapterNavigationIndex += configs["consoleHeight"]
            elif (userChapterAction == "left") and chapterNavigationIndex - configs["consoleHeight"] >= 0:
                chapterNavigationIndex -= configs["consoleHeight"]
            elif userChapterAction == "enter":
                userConfirm = True
                while True:
                    os.system('cls')
                    print('Are you sure that you want to download ' + mangaChapters[chapterNavigationIndex].text + '?')
                    print()
                    if userConfirm:
                        print(colored("[x] Yes", 'yellow'))
                        print('[ ] No')
                    else:
                        print("[ ] Yes")
                        print(colored("[x] No", 'yellow'))
                    userDlAction = getKey()
                    if userDlAction == 'enter':
                        break
                    elif userDlAction in ['up', 'down', 'left', 'right']:
                        userConfirm = not userConfirm
                if userConfirm:
                    os.system('cls')
                    print(colored('Requesting endpoint...', 'blue'))
                    response = requests.get(url="https://api.mangadex.org/at-home/server/" + mangaChapters[chapterNavigationIndex].id, headers=configs['header'])
                    os.system('cls')
                    baseUrl = json.loads(response.text)['baseUrl']
                    imCtr = 1
                    for imLink in mangaChapters[chapterNavigationIndex].data:
                        os.system('cls')
                        print("[Using endpoint " + baseUrl + "]")
                        print("Fetching image " + str(imCtr) + " of " + str(len(mangaChapters[chapterNavigationIndex].data)))
                        url = baseUrl + "/data/" + mangaChapters[chapterNavigationIndex].hash + "/" + imLink
                        print("Link: " + url)
                        with open(os.path.join(mangaFolder, str(imCtr) + '.jpg'), "wb") as f:

                            response = requests.get(url)
                            f.write(response.content)
                        imCtr += 1
                    os.system('cls')
                    print('[Currently reading ' + mangaChapters[chapterNavigationIndex].text + "]")
                    print()
                    print('Press [esc] to return')
                    while getKey() != "esc":
                        pass

            elif userChapterAction == "esc":
                break
