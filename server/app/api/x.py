from flask import jsonify, request
from app import db
from app.models import Client, XSS
from app.api import bp
from flask_login import login_required
from flask_headers import headers

import json

@bp.route('/x/<flavor>/<uid>', methods=['GET', 'POST'])
@headers({'Access-Control-Allow-Origin':'*'})
def catch_xss(flavor, uid):

    client = Client.query.filter_by(uid=uid).first()

    if client == None:
        return jsonify({'status': 'OK'}), 200

    referer = request.referrer
    user_agent = request.user_agent
    if flavor == 'r':
        xss_type = 'reflected'
    else:
        xss_type = 'stored'
    if 'X-Forwarded-For' in request.headers:
        ip_addr = request.headers['X-Forwarded-For'].split(', ')[0]
    else:
        ip_addr = request.remote_addr

    if request.method == 'GET':
        parameters = request.args.to_dict()
    elif request.method == 'POST': 
        parameters = request.form

    other_data = None
    cookies = None
    local_storage = None
    session_storage = None

    for param, value in parameters.items():

        if param == 'cookies':

            if value != '':
                cookies = {}
                print(value)
                cookies_list = value.split('; ')
                print(cookies_list)
                for cookie in cookies_list:
                    cookie_name, cookie_value = cookie.split('=')
                    cookies[cookie_name] = cookie_value
                cookies = json.dumps(cookies)

        elif param == 'local_storage':
            local_storage = value
            if local_storage == '' or local_storage == '{}':
                local_storage = None

        elif param == 'session_storage':
            session_storage = value
            if session_storage == '' or session_storage == '{}':
                session_storage = None

        else:
            if other_data == None:
                other_data = {}
            if param == 'fingerprint':
                value = json.loads(value)
            if param == 'dom':
                value = '<html>\n{}\n</html>'.format(value)
            other_data[param] = value

    if other_data != None: 
        other_data = json.dumps(other_data)

    xss = XSS(referer=referer, user_agent=str(user_agent), ip_addr=ip_addr,
              cookies=cookies, client_id=client.id, xss_type=xss_type, local_storage=local_storage, session_storage=session_storage, other_data=other_data)
    db.session.add(xss)
    db.session.commit()

    return jsonify({'status': 'OK'}), 200
