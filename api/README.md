# How to get Spotify API

- First go to [developer.spotify.com](https://developer.spotify.com/)'s dashboard
- Get Client ID and Client Secret from a page
- Then put `https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&scope=user-read-currently-playing&redirect_uri=http://localhost/callback/` on the browser, you will get URL like follow `http://localhost/callback/?code={CODE}`
- Then we can grab Base64 encode of `{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}` and `{CODE}` to request refresh token using below request:

```sh
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Authorization: Basic {ENCODE}" -d "grant_type=authorization_code&redirect_uri=http://localhost/callback/&code={CODE}" https://accounts.spotify.com/api/token
```

- Now, we can put

```sh
SPOTIFY_CLIENT_ID='____'
SPOTIFY_SECRET_ID='____'
SPOTIFY_REFRESH_TOKEN='____'
```

into `.env` file and run `python spotify-playing.py` to serve via `localhost:5000`
