# N3Robot (Prototype)

Bot by manage notifications from GitLab.

## How to use

- Copy env.example to .env and add your secrets
- Run `make`
- Add your bot to chat
- send command /register

It will be created a document in a collection telegram_chats. After you can send /geturl and will be return URL which you have to paste to part Integration in settings your project.


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
| Push Events                | No     |
| Tag Push Events            | Yes     |
| Wiki Page events           | No      |
