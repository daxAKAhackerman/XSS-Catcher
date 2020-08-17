from flask import jsonify, request
from app import db
from app.models import Settings
from app.api import bp
from flask_login import login_required
from app.validators import check_length, is_email
from app.decorators import permissions


@bp.route('/settings', methods=['GET'])
@login_required
@permissions(all_of=['admin'])
def settings_get():

    settings = Settings.query.first()

    return jsonify(settings.to_dict()), 200


@bp.route('/settings', methods=['POST'])
@login_required
@permissions(all_of=['admin'])
def settings_post():

    data = request.form

    settings = Settings.query.first()

    if 'smtp_host' in data.keys():

        if data['smtp_host'] != '':

            if check_length(data['smtp_host'], 256):
                settings.smtp_host = data['smtp_host']
            else:
                return jsonify({'status': 'error', 'detail': 'Server address too long'}), 400

            if 'smtp_port' in data.keys():

                try:
                    smtp_port = int(data['smtp_port'])
                except ValueError:
                    return jsonify({'status': 'error', 'detail': 'Port is invalid'}), 400

                if smtp_port <= 65535 and smtp_port >= 0:
                    settings.smtp_port = int(data['smtp_port'])
                else:
                    return jsonify({'status': 'error', 'detail': 'Port is invalid'}), 400

            else:
                return jsonify({'status': 'error', 'detail': 'Missing SMTP port'}), 400

            if 'starttls' in data.keys() and 'ssl_tls' in data.keys():
                return jsonify({'status': 'error', 'detail': 'Cannot use STARTTLS and SSL/TLS at the same time'}), 400

            if 'starttls' in data.keys():
                settings.starttls = True

            if 'ssl_tls' in data.keys():
                settings.ssl_tls = True

            if 'starttls' not in data.keys() and 'ssl_tls' not in data.keys():
                settings.starttls = False
                settings.ssl_tls = False

            if 'mail_from' in data.keys():
                if is_email(data['mail_from']) and check_length(data['mail_from'], 256):
                    settings.mail_from = data['mail_from']
                else:
                    return jsonify({'status': 'error', 'detail': 'Email address format is invalid'}), 400

            else:
                return jsonify({'status': 'error', 'detail': 'Missing sender address'}), 400

            if 'smtp_user' in data.keys():

                if check_length(data['smtp_user'], 128):
                    settings.smtp_user = data['smtp_user']
                else:
                    return jsonify({'status': 'error', 'detail': 'SMTP username too long'}), 400

                if 'smtp_pass' in data.keys():
                    if check_length(data['smtp_pass'], 128):
                        settings.smtp_pass = data['smtp_pass']
                    else:
                        return jsonify({'status': 'error', 'detail': 'SMTP password too long'}), 400

            else:
                settings.smtp_user = None
                settings.smtp_pass = None

        else:
            settings.smtp_host = None
            settings.smtp_port = None
            settings.starttls = False
            settings.ssl_tls = False
            settings.mail_from = None
            settings.smtp_user = None
            settings.smtp_pass = None

    else:
        settings.smtp_host = None
        settings.smtp_port = None
        settings.starttls = False
        settings.ssl_tls = False
        settings.mail_from = None
        settings.smtp_user = None
        settings.smtp_pass = None

    db.session.commit()

    return jsonify({'status': 'OK'}), 200
