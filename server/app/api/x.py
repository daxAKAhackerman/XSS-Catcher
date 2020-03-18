from flask import jsonify, request
from app import db
from app.models import Client, XSS
from app.api import bp
from flask_login import login_required


@bp.route('/x/<flavor>/<uid>', methods=['GET'])
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
    parameters = request.args.to_dict()

    other_data = ''
    cookies = ''
    local_storage = ''
    session_storage = ''

    for param, value in parameters.items():

        if param == 'cookies':
            cookies = value
            if cookies == '':
                cookies = None

        elif param == 'local_storage':
            local_storage = value
            if local_storage == '' or local_storage == '{}':
                local_storage = None

        elif param == 'session_storage':
            session_storage = value
            if session_storage == '' or session_storage == '{}':
                session_storage = None

        else:
            other_data += '{}={};'.format(param, value)
            if other_data == '':
                other_data = None

    xss = XSS(referer=referer, user_agent=str(user_agent), ip_addr=ip_addr,
              cookies=cookies, client_id=client.id, xss_type=xss_type, local_storage=local_storage, session_storage=session_storage, other_data=other_data)
    db.session.add(xss)
    db.session.commit()

    return jsonify({'status': 'OK'}), 200
