
# VidMe API

This is an entry-level extracted API for VidMe. Right now it can just upload videos but I plan on adding more in the future.

## Settings

In order to set up your account, rename 'settings.json.example' to 'settings.json' and add your username and password. If you would rather not, if you do not add a username or password, it will prompt you for it when you run it. Please be aware it is stored in plain text.

Example:

```
{"username": "AwesomeFred", "password": "chivermetimbers"}
```

## Upload

To upload a video, just do `python main.py "c:/dir/dir/myvideo.mp4"`.

You could also just set the varible in `main.py`:

```
video_filename = "C:/somedir/another/myvideo.mp4"
```
