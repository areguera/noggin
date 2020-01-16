from flask import flash, redirect, url_for, render_template
import python_freeipa

from securitas import app, ipa_admin
from securitas.form.register_user import RegisterUserForm
from securitas.security.ipa import untouched_ipa_client


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        try:
            ipa_admin.user_add(
                username,
                form.firstname.data,
                form.lastname.data,
                f'{form.firstname.data} {form.lastname.data}',  # TODO ???
                user_password=password,
                login_shell='/bin/bash',
            )

            # Now we fake a password change, so that it's not immediately expired.
            # This also logs the user in right away.
            ipa = untouched_ipa_client(app)
            ipa.change_password(username, password, password)
        except python_freeipa.exceptions.FreeIPAError as e:
            app.logger.error(
                f'An unhandled error {e.__class__.__name__} happened while registering user '
                f'{username}: {e.message}'
            )
            form.errors['non_field_errors'] = [
                'An error occurred while creating the account, please try again.'
            ]
        else:
            flash(
                'Congratulations, you now have an account! Go ahead and sign in to proceed.',
                'green',
            )
            return redirect(url_for('root'))

    return render_template('register.html', register_form=form)
