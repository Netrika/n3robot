import mongoengine


class N3TelegramObject(mongoengine.Document):
    meta = {'abstract': True}
    pass


class N3TelegramUser(N3TelegramObject):
    id = mongoengine.IntField(primary_key=True, required=True)
    username = mongoengine.StringField(required=True)
    first_name = mongoengine.StringField()
    last_name = mongoengine.StringField()
    is_bot = mongoengine.BooleanField()
    meta = {
        'allow_inheritance': True,
        'collection': 'telegram_users',
    }


class N3TelegramChat(N3TelegramObject):
    chat_id = mongoengine.StringField(primary_key=True, required=True)
    title = mongoengine.StringField()
    is_active = mongoengine.BooleanField(default=True)
    silent_until = mongoengine.DateTimeField()
    mute_until = mongoengine.DateTimeField()
    members = mongoengine.ListField(mongoengine.ReferenceField(N3TelegramUser))
    projects = mongoengine.ListField(mongoengine.DictField())
    api_id = mongoengine.StringField()

    meta = {
        'allow_inheritance': True,
        'collection': 'telegram_chats',
    }


class N3TelegramMessage:

    def __init__(self, raw_data):
        self.raw_data = raw_data

    def is_skip(self):
        return False

    def get_project(self):
        return {}

    def get_branch(self):
        return


class N3TelegramMessagePipeline(N3TelegramMessage):
    template = 'telegram/pipeline.j2'

    def is_skip(self):
        pipeline = self.raw_data.get('object_attributes')
        if pipeline.get('status') == 'pending' or pipeline.get('status') == 'skipped':
            return True

    def get_project(self):
        gitlab_project = {}
        project = self.raw_data.get('project')

        gitlab_project.update(
            id=project.get('id'),
            name=project.get('name'),
            web_url=project.get('web_url')
        )
        return gitlab_project

    def get_branch(self):
        return self.raw_data.get('object_attributes', {}).get('ref')


class N3TelegramMessageBuild(N3TelegramMessage):
    template = 'telegram/build.j2'

    def is_skip(self):
        build_status = self.raw_data.get('build_status')
        if build_status == 'created' or build_status == 'skipped':
            return True

    def get_project(self):
        gitlab_project = {}
        repository = self.raw_data.get('repository')

        gitlab_project.update(
            id=self.raw_data.get('project_id'),
            name=repository.get('name'),
            web_url=repository.get('homepage')
        )
        return gitlab_project

    def get_branch(self):
        return self.raw_data.get('ref')


class N3TelegramMessagePush(N3TelegramMessage):
    template = 'telegram/push.j2'


class N3TelegramMessageTagPush(N3TelegramMessage):
    template = 'telegram/tag_push.j2'

    def get_project(self):
        gitlab_project = {}
        project = self.raw_data.get('project')

        gitlab_project.update(
            id=project.get('id'),
            name=project.get('name'),
            web_url=project.get('web_url')
        )
        return gitlab_project


class N3TelegramMessageMergeRequestHook(N3TelegramMessage):
    template = 'telegram/merge_request.j2'
