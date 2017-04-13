
# VidMe API

This is an entry-level extracted API for VidMe. Right now it can just upload videos but I plan on adding more in the future.

## Installation

This package needs the following pips:

* `pip install requests`

Please see `requirements.txt` for an up-to-date list.

## Settings

In order to set up your account, just copy and paste 'settings.json.example' to 'settings.json' and add your username and password. If you would rather not, if you do not add a username or password, it will prompt you for the ones you didn't add when you run it. Please be aware it is stored in plain text.

Example:

```
{"username": "AwesomeFred", "password": "chivermetimbers"}
```

## Upload

To upload a video, just do `python main.py upload "c:/dir/dir/myvideo.mp4" "title"`.

If you do not give it a title, the name of the video will be used.

## Usage

### General Functions

General functions. Does not required to be logged in, etc. or settings.

Order options: `video_id`, `view_count`, `date_completed`, `score`

Direction options: `ASC` or `DESC`

#### get_featured

Options:

* offset (int)
* limit (int)
* marker (string)
* order (string)

Examples:

```
print [video.get_title() for video in vidme.get_featured()]
```

#### get_hot

Options:

* subindex (int)
* offset (int)
* limit (int)

Examples:

```
print [video.get_title() for video in vidme.get_hot(offset=10)]
```

#### get_new

Options:

* nsfw (1 for true, 0 for false)

Examples:

```
print [video.get_title() for video in vidme.get_new(nwfw=0)]
```

#### get_trending

Options:

* offset (int)
* limit (int)

Examples:

```
print [video.get_title() for video in vidme.get_trending()]
```

#### get_search(query)

Options:

* nsfw (1 for true, 0 for false)
* order (string :: 'likes_count', 'hot_score', 'date_completed')
* user (string)

Examples:

```
print [video.get_title() for video in vidme.get_search('#keyboard', user="kingfredrickvi")]
```

### Sessions

This stores the Vid.Me token that is returned when it attempts to log in. This is used to tell the server you really are who you say you are when you try to do things like edit a video's title.

Example:

```
settings = get_settings('settings')

session = vidme.Session(settings)
```

### Videos

To get a new video object, any of the three following will work:

```
video = vidme.Video(url = "https://vid.me/Z47b")

video = vidme.Video(video_id = 14854593)

video = vidme.Video(code = "Z47b")
```

Using a getter:

```
print video.get_title()
```

Gettings:

* `get_video_id()`
* `get_comments()`
* `get_url()`
* `get_full_url()`
* `get_embed_url()`
* `get_complete()`
* `get_complete_url()`
* `get_state()`
* `get_title()`
* `get_description()`
* `get_duration()`
* `get_height()`
* `get_width()`
* `get_date_created()`
* `get_date_stored()`
* `get_date_completed()`
* `get_comment_count()`
* `get_view_count()`
* `get_version()`
* `get_nsfw()`
* `get_thumbnail()`
* `get_thumbnail_url()`
* `get_score()`
* `get_private()`
* `get_total_watchers()`
* `get_watcher_countries()`
* `get_uri()` - Location of file on your disk. Only set if you set it.

Setters:

* `set_title(session, title)` - `title`: new title of video.
* `set_description(session, description)` - `desc`: new description of video.
* `set_source(session, source)` - Yeah idk either.
* `set_private(session)` - Sets video to private.
* `set_public(session)` - Sets video to public.
* `set_latitude(session, latitude)` - `latitude`: lat coords I guess?
* `set_longitude(session, longitude)` - `longitude`: long coords I guess?
* `set_place_id(session, place_id)` - `place_id`: the place_id from foursquare.
* `set_place_name(session, place_name)` - `place_name`: The place name from foursquare.
* `set_nsfw(session)` - Once set, you cannot undo.
* `flag(session, flag = 1)` - Flag the video. 1 to flag. 0 to unflag I guess.
* `vote(session, vote = True, time = 0.0)` - `vote`: upvote if True, take away upvote if false, `time`: Time in the video at which you decided to upvote.
* `delete(session)` - Deletes the video.

### Users

To get a new user object, any of the three following will work:

```
user = vidme.User('kingfredrickvi')
user = vidme.User(username='kingfredrickvi')
user = vidme.User(user_id=15864858)
```

Using a getter:

```
print user.get_username()
```

Getters:

* `get_user_id()`
* `get_username()`
* `get_full_url()`
* `get_avatar()`
* `get_avatar_url()`
* `get_cover()`
* `get_cover_url()`
* `get_video_views()`
* `get_likes_count()`
* `is_following(other_username)` - `other_username`: user to follow. Is a class User.
* `is_blocked(other_username)` - `other_username`: user to follow. Is a class User.
* `get_videos(sort="recent", private=0, session=None, offset=0)`
* `get_followers(offset = 0, hard = False)` - `offset`: offset of list, `hard`: use cached followers list or use list that has already been grabbed.
* `get_following(offset = 0, hard = False)` - `offset`: offset of list, `hard`: use cached following list or use list that has already been grabbed.

Sort Values:

`"recent"`, `"older"`, `"popular"`, `"lesswatched"`

Setters:

* `set_username(session, username)` - `username`: The new username.
* `set_password(session, password, passwordCurrent)` - `password`: new password, `passwordCurrent`: current password.
* `set_bio(session, bio)` - `bio`: New biography for user profile.
* `set_displayname(session, displayname)` - `displayname`: new display name.
* `set_email(session, email)` - `email`: new email address.

Operations:

* `follow_user(session, user)` - `user`: user to follow. Is a class User.
* `unfollow_user(session, user)` - `user`: user to unfollow. Is a class User.
* `unsubscribe_user(session, user)` - `user`: user to unsubscribe. Is a class User.

### Comments

To get the comments for a video, do the following:

```
video = vidme.Video(video_id = 14854593)

comments = video.get_comments()
```

Getters:

* `get_comment_id()`
* `get_video_id()`
* `get_user_id()`
* `get_parent_comment_id()`
* `get_full_url()`
* `get_body()`
* `get_date_created()`
* `get_made_at_date()`
* `get_score()`
* `get_comment_count()`
* `get_user()`
* `get_viewerVote()`
* `get_comments()` - Returns an array of Comment objects.

Setters:

* `vote(session, vote = True)` - `vote`: upvote if True, take away upvote if false
* `delete(session)` - Deletes the comment.
