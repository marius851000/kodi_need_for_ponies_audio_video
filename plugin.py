import sys
try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode

try:
    from urlparse import parse_qsl
except:
    from urllib.parse import parse_qsl

import plugin_param

import xbmcgui
import xbmcplugin

import needforponies

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

languages = [ "FR" "EN" ]
language = "FR" #TODO: settings

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def select_category():
    season_item = xbmcgui.ListItem(label = "episodes")
    xbmcplugin.addDirectoryItem(_handle, get_url(action="list_season"), season_item, True)
    film_item = xbmcgui.ListItem(label = "films")
    xbmcplugin.addDirectoryItem(_handle, get_url(action="list_movies"), film_item, True)
    other_item = xbmcgui.ListItem(label = "autres")
    xbmcplugin.addDirectoryItem(_handle, get_url(action="list_others_category"), other_item, True)
    #music_item = xbmcgui.ListItem(label = "musiques")
    #xbmcplugin.addDirectoryItem(_handle, get_url(action="list_music_categories"), music_item, True)
    xbmcplugin.endOfDirectory(_handle)

def select_season():
    seasons = needforponies.list_seasons()

    for season in seasons:
        season_item = xbmcgui.ListItem(label = season["name"])
        season_item.setArt({"poster": season["poster"], "thumb": season["poster"]})
        xbmcplugin.addDirectoryItem(_handle, get_url(action="list_episodes", season_id=season["season_id"]), season_item, True)

    xbmcplugin.endOfDirectory(_handle)

def select_episodes(season_id):
    episodes = needforponies.list_episodes(season_id)
    season_nb = int(season_id.split("-")[-1])

    for episode in episodes:
        episode_nb = int(episode["episode_id"].split("-")[-1])
        episode_item = xbmcgui.ListItem(label = "S{}E{}: {}".format(season_nb, episode_nb, episode["name"]))
        episode_item.setArt({"thumb": episode["image"]})

        episode_item.setInfo("video", {
            "genre": "Animation",
            "season": season_nb,
            "episode": episode_nb, #TODO: rather scrape that from the page
            "plot": episode["resume"],
            "name": episode["name"],
            "mediatype": "video",
        })
        episode_item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(_handle, get_url(action="play_episode", season_id=season_id, episode_id=episode["episode_id"]), episode_item, False)

    xbmcplugin.endOfDirectory(_handle)

def play_episode(season_id, episode_id):
    episode = needforponies.get_episode(season_id, episode_id, language)
    play_video(episode)

def play_video(video):
    video_item = xbmcgui.ListItem(label = video["title"], path = video["video_url"])
    video_item.setSubtitles([video["sub_fr"], video["sub_en"]])
    xbmcplugin.setResolvedUrl(_handle, True, listitem=video_item)

def select_movie():
    movies = needforponies.list_movies()
    for movie in movies:
        movie_item = xbmcgui.ListItem(label = movie["name"])
        movie_item.setArt({"poster": movie["poster"], "thumb": movie["poster"]})
        movie_item.setInfo("video", {
            "mediatype": "video",
            "name": movie["name"]
        })
        movie_item.setProperty("IsPlayable", "true")
        xbmcplugin.addDirectoryItem(_handle, get_url(action="play_movie", movie_id=movie["href"]), movie_item, False)

    xbmcplugin.endOfDirectory(_handle)

def play_movie(movie_id):
    movie = needforponies.get_movie(movie_id, language)
    play_video(movie)

def select_other_category():
    others = needforponies.get_other_data()
    for category in others:
        category_item = xbmcgui.ListItem(label = category[0])
        xbmcplugin.addDirectoryItem(_handle, get_url(action="select_other_subcontent", category=category[0]), category_item, True)
    xbmcplugin.endOfDirectory(_handle)

def select_other_subcontent(selected_category):
    others = needforponies.get_other_data()
    for category in others:
        if category[0] == selected_category:
            # the good category
            for subcontent in category[1]:
                sub_item = xbmcgui.ListItem(label = subcontent["name"])
                sub_item.setArt({"poster": subcontent["poster"]})
                if len(subcontent["href"].split("/")) == 2:
                    sub_item.setInfo("video", {
                        "mediatype": "video",
                        "name": subcontent["name"],
                    })
                    sub_item.setProperty("IsPlayable", "true")
                    xbmcplugin.addDirectoryItem(_handle, get_url(action="play_other", other_id=subcontent["href"]), sub_item, False)
                else:
                    xbmcplugin.addDirectoryItem(_handle, get_url(action="select_other_subcontent_episode", other_season_id=subcontent["href"]), sub_item, True)
    xbmcplugin.endOfDirectory(_handle)

def play_other(other_id):
    video = needforponies.get_other_video(other_id, language)
    play_video(video)

def select_other_subcontent_episode(other_season_id):
    episodes = needforponies.get_others_episodes(other_season_id)
    for episode in episodes:
        if episode["href"] == "#":
            continue
        episode_nb = int(episode["href"].split("-")[-1])
        episode_item = xbmcgui.ListItem(label = "E{}: {}".format(episode_nb, episode["name"]))
        episode_item.setArt({"thumb": episode["image"]})
        episode_item.setInfo("video", {
            "season": 0,
            "episode": episode_nb,
            "plot": episode["resume"],
            "name": episode["name"],
            "mediatype": "video",
        })
        episode_item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(_handle, get_url(action="play_other", other_id=episode["href"]), episode_item, False)

    xbmcplugin.endOfDirectory(_handle)

def select_music_categories():
    musics = needforponies.list_music_categories()
    for music in musics:
        music_item = xbmcgui.ListItem(label = "Musiques - {}".format(music[0]))
        xbmcplugin.addDirectoryItem(_handle, get_url(action="list_music_sub_category", music_category=music[0]), music_item, True)

    xbmcplugin.endOfDirectory(_handle)

def select_music_sub_category(selected_category):
    musics = needforponies.list_music_categories()
    for category in musics:
        if category[0] == selected_category:
            for album in category[1]:
                album_item = xbmcgui.ListItem(label = album["name"])
                album_item.setArt({"thumb": album["poster"]})
                xbmcplugin.addDirectoryItem(_handle, get_url(action="select_in_album", music_language="None", album_id=album["href"]), album_item, True)
    xbmcplugin.endOfDirectory(_handle)

def select_in_album(album_id, music_language):
    album = needforponies.get_album_data(album_id)
    if len(album) == 1 or (music_language in album):
        if len(album) == 1:
            for unique_name in album.keys(): # for python 3
                music_language = unique_name
        selected_album = album[music_language]
        music_id = 0
        for music in selected_album:
            music_item = xbmcgui.ListItem(label = music[0])
            music_item.setProperty("IsPlayable", "true")
            tracknumber_str = music[0].split(" ")[0]
            music_item.setInfo("music", {
                "title": music[0][5:],
                "tracknumber": int(tracknumber_str),
                "discnumber": 0,
                "count": int(tracknumber_str)
            })
            music_item.setPath(music[1])
            xbmcplugin.addDirectoryItem(_handle, get_url(action="play_music", album_id=album_id, music_language=music_language, music_id=str(music_id)), music_item, False)
            music_id += 1
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_TRACKNUM)
        xbmcplugin.endOfDirectory(_handle)
    else:
        for language in [("FR", "VF"), ("EN", "VO")]:
            language_item = xbmcgui.ListItem(label =  language[0])
            xbmcplugin.addDirectoryItem(_handle, get_url(action="select_in_album", album_id=album_id, music_language=language[1]), language_item, True)
        xbmcplugin.endOfDirectory(_handle)

def play_music(album_id, music_language, music_id):
    album = needforponies.get_album_data(album_id)
    selected_album = album[music_language]
    music = selected_album[int(music_id)]
    music_item = xbmcgui.ListItem(label = music[0], path=music[1])
    xbmcplugin.setResolvedUrl(_handle, True, listitem=music_item)

def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        action = params["action"]
        if action == 'list_season':
            select_season()
        elif action == "list_episodes":
            select_episodes(params["season_id"])
        elif action == "play_episode":
            play_episode(params["season_id"], params["episode_id"])
        elif action == "list_movies":
            select_movie()
        elif action == "play_movie":
            play_movie(params["movie_id"])
        elif action == "list_others_category":
            select_other_category()
        elif action == "select_other_subcontent":
            select_other_subcontent(params["category"])
        elif action == "play_other":
            play_other(params["other_id"])
        elif action == "select_other_subcontent_episode":
            select_other_subcontent_episode(params["other_season_id"])
        elif action == "list_music_categories":
            select_music_categories()
        elif action == "list_music_sub_category":
            select_music_sub_category(params["music_category"])
        elif action == "select_in_album":
            select_in_album(params["album_id"], params["music_language"])
        elif action == "play_music":
            play_music(params["album_id"], params["music_language"], params["music_id"])
        else:
            raise ValueError('Invalid paramstring: {0}'.format(paramstring))
    else:
        if plugin_param.CATEGORY == "video":
            select_category()
        else:
            select_music_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
