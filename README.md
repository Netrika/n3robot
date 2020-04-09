# N3Robot

Bot by manage notifications from GitLab.

## Run

You can run `make` for launch docker-compose.

## Bot commands

| Command     | Description                                      |
| ----------- | ------------------------------------------------ |
| /register   | Activates sending messages to chat.              |
| /unregister | Stop sending message.                            |
| /mute       | Stop sending messages until the date.            |
| /silent     | Stop sending sound notifications until the date. |
| /geturl     | Generates URL for send notification from GitLab. |
| /projects   | Return list projects for this chat.              |
| /getgid     | Returns ID of the group this bot is added to.    |

## GitLab WebHook

| X-Gitlab-Event             | Support |
| -------------------------- | ------- |
| Comments                   | Yes     |
| Confidential Comments      | No      |
| Confidential Issues events | No      |
| Issues Events              | No      |
| Job Events                 | Yes     |
| Merge request events       | No      |
| Pipeline Events            | Yes     |
| Push Events                | Yes     |
| Tag Push Events            | Yes     |
| Wiki Page events           | No      |


## How to use

Add your bot to chat and send command /register. It will be created a document in a collection telegram_chats. After you can send /geturl and will be return URL which you have to paste to part Integration in settings your project.
After the first sending, you don't get a message because project didn't exist.
