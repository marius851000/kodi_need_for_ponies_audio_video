# coding=utf-8
from bs4 import BeautifulSoup
import requests
try:
    from urllib import urlopen
except:
    from urllib.request import urlopen

try:
    from urllib.error import HTTPError
    use_httperror = True
except ImportError:
    use_httperror = False

def get_soup(url):
    r = requests.get(url)
    print("needs for ponies: fetching {}".format(url))
    return BeautifulSoup(r.content, "html.parser")

def list_movies():
    movies_url = "https://needforponies.fr/movies/"
    return list_element_unique_list_poster(movies_url)

def list_element_unique_list_poster(url):
    elements = []
    element_list_page = get_soup(url)
    for a_thumbnail in element_list_page.find_all("a", attrs={"class": "thumbnail"}):
        name = a_thumbnail.find("h4").text.strip()
        href = a_thumbnail.get("href")
        poster = "https://needforponies.fr" + a_thumbnail.find("img").get("src")
        element_data = {
            "href": href,
            "poster": poster,
            "name": name
        }
        elements.append(element_data)
    return elements

def list_seasons():
    episodes_url = "https://needforponies.fr/episodes/";
    seasons = list_element_unique_list_poster(episodes_url)
    for season in seasons:
        season["season_id"] = season["href"]

    return seasons

def get_others_episodes(other_season_id):
    url = "https://needforponies.fr/others/{}".format(other_season_id)
    return list_element_episode_page(url)


def list_episodes(season_id):
    url = "https://needforponies.fr/episodes/" + season_id
    episodes = list_element_episode_page(url)
    for episode in episodes:
        episode["episode_id"] = episode["href"].split("/")[-1]
    return episodes

def list_element_episode_page(url):
    episodes = []
    episodes_list_page = get_soup(url)
    for body in episodes_list_page.find_all("div", attrs={"class": "panel-body"}):
        a_english_version = body.find("h4").find_all("a")[0]

        href = a_english_version["href"]
        english_name = a_english_version.text.strip().split("\n")[0]
        if len(english_name) > 2:
            if english_name[-2:] == " )":
                english_name = english_name[:-2]

        resume = body.find("p").text.strip()

        image = "https://needforponies.fr" + body.find("img", attrs={"class": "img-responsive episode-image"})["src"]

        episode_data = {
            "href": href,
            "name": english_name,
            "image": image,
            "resume": resume,
        }
        episodes.append(episode_data)
    return episodes

def get_episode(season_id, episode_id, language): #language: FR, EN
    url = "https://needforponies.fr/episodes/" + season_id + "/" + episode_id
    return parse_video_page(url, language)

def parse_video_page(base_url, language):
    if language == "FR":
        url = base_url + "/VF"
    else:
        url = base_url
    episode = {}
    episode_page_soup = get_soup(url)
    episode["title"] = episode_page_soup.find("h3").text.strip()
    episode["resume"] = episode_page_soup.find("div", attrs={"class": "row episodeDescription"}).text.strip()
    video_url = None
    subtitle_url_fr = None
    subtitle_url_en = None
    for a in episode_page_soup.find_all("a"):
        text = a.text.strip()
        if text == u"Télécharger":
            video_url = a["href"]
        if text == "Sous-titres FR":
            subtitle_url_fr = "https://needforponies.fr" + a["href"]
        if text == "Sous-titres EN":
            subtitle_url_en = "https://needforponies.fr" + a["href"]
    if video_url[0] == "/":
        video_url = "https://needforponies.fr" + video_url
    episode["video_url"] = video_url
    episode["sub_fr"] = subtitle_url_fr
    episode["sub_en"] = subtitle_url_en
    if use_httperror:
        try:
            video_check = urlopen(video_url)
            http_code = video_check.getcode()
        except HTTPError:
            http_code = 404
    else:
        video_check = urlopen(video_url)
        http_code = video_check.getcode()
    if http_code == 404: # it seem the french version doesn't exist
        if language == "EN":
            raise BaseException("the video doesn't exist, but we are in english language...")
        else:
            return parse_video_page(base_url, "EN")
    return episode

def get_movie(movie_id, language):
    url = "https://needforponies.fr/movies/{}".format(movie_id)
    return parse_video_page(url, language)

def get_other_data():
    url = "https://needforponies.fr/others/"
    return parse_page_poster_with_category(url)

def parse_page_poster_with_category(url):
    soup = get_soup(url)

    actual_category = None
    actual_content = []
    results = [] # under the form [("category_name", [{"poster":..., "name": ..., "href": ...}, ...]), ...]
    for div in soup.find_all("div"):
        div_class = div.get("class")
        if div_class == ["col-xs-12"]: #separator
            if len(actual_content) > 0:
                results.append((actual_category, actual_content))
            actual_category = div.text.strip()
            actual_content = []
        elif div_class == ["col-xs-6","col-md-2"]: #content
            actual_content.append({
                "name": div.find("h4").text.strip(),
                "poster": "https://needforponies.fr" + div.find("img")["src"],
                "href": div.find("a")["href"]
            })
    results.append((actual_category, actual_content))

    return results

def get_other_video(other_id, language):
    url = "https://needforponies.fr/others/{}".format(other_id)
    return parse_video_page(url, language)

def list_music_categories():
    url = "https://needforponies.fr/musics/"
    return parse_page_poster_with_category(url)

def get_album_data(album_id):
    url = "https://needforponies.fr/musics/{}".format(album_id)
    soup = get_soup(url)

    result = {}

    for part_soup in soup.find_all("div", attrs={"class": "panel panel-primary"}):
        music_language = part_soup.find("div", attrs={"class": "panel-heading"}).text.strip().split(" ")[-1]
        musics = []
        for music_soup in part_soup.find_all("div", attrs={"class": "col-xs-12 music-item"}):
            music_name = music_soup.find("strong").text.strip()
            music_url = "https://needforponies.fr"+music_soup.find("source")["src"]
            if music_name.endswith(".mp3"):
                music_name = music_name[:-4]
            musics.append((music_name, music_url))
        result[music_language] = musics
    return result

def list_other_shows():
    url = "https://needforponies.fr/other-tv-shows/"
    shows = parse_page_poster_with_category(url)

    for show in shows:
        season["show_id"] = season["href"].split("/")[-1]
    
    return shows