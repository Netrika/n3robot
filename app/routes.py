from flask import (request, jsonify, render_template, abort, g)

from app import app, gitlab_hook_map, emoji_map, tasks


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.route('/gitlab/<project_api_id>', methods=['POST'])
def gitlab(project_api_id):
    gitlab_event = request.headers.get('X-Gitlab-Event')
    if not gitlab_event:
        return jsonify(abort(404, description='Header X-Gitlab-Event not found'))

    context = request.get_json()
    message_class = gitlab_hook_map.get(gitlab_event, {})
    if not message_class:
        return jsonify(abort(404, description='Unknown type X-Gitlab-Event'))

    message = message_class(raw_data=context)
    if message.is_skip():
        return 'A message was skipped', 200
    gitlab_project = message.get_project()
    message_text = render_template(message.template, **context, **emoji_map)

    tasks.update_projects_chat(project_api_id, gitlab_project)
    tasks.send_message(api_id=project_api_id,
                       message=message_text,
                       branch=message.get_branch(),
                       gitlab_project=gitlab_project)

    return 'ok', 201
