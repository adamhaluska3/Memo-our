from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import json
from datetime import date

from .auth import login_required
from .db import get_db


bp = Blueprint("events", __name__)


@bp.route('/')
def index():
    db = get_db()
    today_events = db.execute(
        'SELECT e.id, name, first_name, birth_date, remaining_days,'
        ' age, u.username FROM events_data AS e JOIN user AS u'
        ' ON e.author_id = u.id WHERE remaining_days = 0 ORDER BY age DESC'
    ).fetchall()

    future_events = db.execute(
        'SELECT e.id, name, first_name, birth_date, remaining_days,'
        ' age, u.username FROM events_data AS e JOIN user AS u'
        ' ON e.author_id = u.id WHERE remaining_days > 0 ORDER BY age DESC'
    )

    past_events = db.execute(
        'SELECT e.id, name, first_name, birth_date, remaining_days, age, u.username,'
        ' strftime("%j", "now") - date(strftime("%Y", "now") + 1, strftime("%m", "now"), strftime("%d", "now")) AS future_remaining_days'
        ' FROM events_data AS e JOIN user AS u'
        ' ON e.author_id = u.id WHERE remaining_days < 0 ORDER BY future_remaining_days ASC'
    ).fetchall()

    nameday_names = get_nameday_names()

    nameday_events = db.execute(
        f'''SELECT id, name, first_name, age FROM events_data WHERE
           first_name IN ({', '.join(f"'{name}'" for name in nameday_names)})
           ORDER BY age DESC'''
           ).fetchall()

    return render_template(
        'events/index.html',
        today_events=today_events, future_events=future_events,
        past_events=past_events,
        nameday=nameday_names, nameday_events=nameday_events
        )


def get_nameday_names():
    nameday_names = []
    today = date.today().strftime("%m-%d")

    nameday_db = open("memo-our/nameday_data/SK.json")

    loaded_nameday_db = json.load(nameday_db)
    today_entries = loaded_nameday_db['namedays']['SK']['days'][today]

    for entry in today_entries:
        nameday_names.append(entry['name'])

    return nameday_names


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        error = None
        name = request.form['name']
        first_name = request.form['first_name']
        birth_date = request.form['birth_date']
        note = request.form['note']

        if (not name) or (not first_name) or (not birth_date):
            error = 'Some info is missing.'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'INSERT INTO events (author_id, name, first_name, birth_date,'
                ' note) VALUES (?, ?, ?, ?, ?)',
                (g.user['id'], name, first_name, birth_date, note)
            )
            db.commit()
            return redirect(url_for('events.index'))

    return render_template('events/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    event = get_event(id)

    if request.method == 'POST':
        name = request.form['name']
        first_name = request.form['first_name']
        birth_date = request.form['birth_date']
        note = request.form['note']

        db = get_db()
        db.execute(
            'UPDATE events SET name = ?, first_name = ?, birth_date = ?,'
            ' note = ? WHERE id = ?',
            (name, first_name, birth_date, note, id)
        )
        db.commit()
        return redirect(url_for('events.index'))

    return render_template('events/update.html', event=event)


def get_event(id, check_author=True):
    event = get_db().execute(
        'SELECT e.id, name, first_name, birth_date, remaining_days, note, age,'
        ' author_id, username FROM events_data AS e JOIN user AS u'
        ' ON e.author_id = u.id WHERE e.id = ?',
        (id,)
    ).fetchone()

    if event is None:
        abort(404, f"Event id {id} doesn't exist.")

    if check_author and (g.user is None or event['author_id'] != g.user['id']):
        abort(403)

    return event


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_event(id)
    db = get_db()
    db.execute('DELETE FROM events WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for("events.index"))
