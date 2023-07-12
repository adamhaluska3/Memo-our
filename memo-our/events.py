from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db


bp = Blueprint("events", __name__)


@bp.route('/')
def index():
    db = get_db()
    events = db.execute(
        'SELECT e.id, name, birth_date, event_type, remaining_days'
        ' remaining_days FROM events_data AS e JOIN user AS u'
        ' ON e.author_id = u.id ORDER BY remaining_days'
    ).fetchall()

    return render_template('events/index.html', events=events)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        error = None
        name = request.form['name']
        birth_date = request.form['birth_date']

        try:
            event_type = request.form['event_type']
        except KeyError:
            error = 'Some info is missing.'

        if (not name) or (not birth_date):
            error = 'Some info is missing.'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'INSERT INTO events (author_id, name, birth_date,'
                ' event_type) VALUES (?, ?, ?, ?)',
                (g.user['id'], name, birth_date, event_type)
            )
            db.commit()
            return redirect(url_for('events.index'))

    return render_template('events/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    event = get_event(id)

    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birth_date']
        event_type = request.form['event_type']

        db = get_db()
        db.execute(
            'UPDATE events SET name = ?, birth_date = ?, event_type = ?'
            ' WHERE id = ?',
            (name, birth_date, event_type, id)
        )
        db.commit()
        return redirect(url_for('events.index'))

    return render_template('events/update.html', event=event)


def get_event(id, check_author=True):
    event = get_db().execute(
        'SELECT e.id, name, birth_date, event_type, remaining_days,'
        ' author_id, username FROM events_data AS e JOIN user AS u'
        ' ON e.author_id = u.id WHERE e.id = ?',
        (id,)
    ).fetchone()

    if event is None:
        abort(40, f"Event id {id} doesn't exist.")

    if check_author and event['author_id'] != g.user['id']:
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
