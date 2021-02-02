#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 01:00:02 2020

@author: hariniram
"""

# step 1: log into youtube
# step 2: grab music folder
# step 3: create new playlist
# step 4: search for song
# step 5: add to playlist


import json
import requests
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl
from secret import spotify_user_id, spotify_token


class CreatePlaylist:
    
    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}
    
    # step 1: log into youtube
    def get_youtube_client(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        
        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"
        
        # get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_clinet_secrets_file(client_secrets_file, scopes)
        credentials = flow.run_console()
        
        # from youtube data api
        youtube_client = googleapiclient.discovery.build(api_service_name, api_version, credentials)
        
        return youtube_client
    
    # step 2: grab music folder
    def get_music_videos(self):
        request = self.yputube_client.videos().list(
            part = "snippet,contentDetails,statistics",
            myRating = "like"
        )
        response = request.execute()
        
        # collect each video and get important information
        for item in response["item"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(item["id"])
            
            # use youtube_dl to collect the song name and artist name
            video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
            song_name = video["track"]
            artist = video["artist"]
            
            # save all important info
            self.all_song_info[video_title]={
                "youtube_url": youtube_url,
                "song_name": song_name,
                "artist": artist,
                
                # add the uri, easy to get song to put into playlist
                "spotify_uri": self.get_spotify_uri(song_name, artist)
            }
    
    # step 3: create new playlist
    def create_playlist(self):
        request_body = json.dumps({
            "name": "Youtube Music Videos",
            "description": "All Like Music Videos",
            "public": True
        })
        
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data = request_body,
            headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(spotify_token)
            }
        )
        # playlist id
        response_json = response.json()
        
        return response_json["id"]
    
    # step 4: search for song
    def get_spotify_uri(self, song_name, artist):
        query = "https://api.spotify.com/v1/search".format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        
        # only uses the first song
        uri = songs[0]["uri"]
        
        return uri
        
        
    
   # step 5: add to playlist
    def add_song_to_playlist(self):
        # populate our songs dictionary
        self.get_music_videos()
        
        # collect all of uri
        uris = []
        for song ,info in self.all_song_info.items():
            uris.append(info["spotify_uri"])
        
        # create a new playlist
        playlist_id = self.create_playlist()
        
        # add all songs into new playlist
        request_data = json.dumps(uris)
        
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data = request_data,
            headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        return response_json

