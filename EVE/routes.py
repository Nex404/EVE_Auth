from EVE import app, config, esisecurity, db, esiapp, esiclient
from EVE.models import Character, User
from EVE.forms import CharForm, LoginForm, RegisterForm
from EVE.request_fkt import *
from flask import render_template, redirect, url_for, flash, request, session
from esipy.exceptions import APIException
from sqlalchemy.orm.exc import NoResultFound
from flask_login import login_user, logout_user, login_required
import random
import hashlib
import hmac




@app.route('/')
@app.route('/home')
def home_page():
    get_logo()
    return render_template('home.html')

@app.route('/about')
def about_hmw():
    return render_template('about.html')

@app.route('/api_check')
def api_check_user():
    return render_template('api.html')

def generate_token():
    """Generates a non-guessable OAuth token"""
    chars = ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    rand = random.SystemRandom()
    random_string = ''.join(rand.choice(chars) for _ in range(40))
    return hmac.new(
        config.SECRET_KEY.encode('utf-8'),
        random_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

@app.route('/sso/login')
def login_eve():
    """ this redirects the user to the EVE SSO login """
    token = generate_token()
    session['token'] = token
    return redirect(esisecurity.get_auth_uri(
        state=token,
        scopes=['esi-mail.read_mail.v1',
        'esi-skills.read_skills.v1', 
        'esi-skills.read_skillqueue.v1', 
        'esi-wallet.read_character_wallet.v1', 
        'esi-clones.read_clones.v1', 
        'esi-characters.read_contacts.v1', 
        'esi-bookmarks.read_character_bookmarks.v1', 
        'esi-contracts.read_character_contracts.v1', 
        'esi-clones.read_implants.v1',
        'esi-location.read_location.v1',
        'esi-location.read_ship_type.v1',
        'esi-location.read_online.v1',
        'esi-universe.read_structures.v1']
    ))

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data, 
                              password=form.password1.data)
        
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Erfolgreich Account erstellt und eingeloggt als: {user_to_create.username}", category='succsses')
        
        return redirect(url_for('/home'))
    
    if form.errors != {}: #if there are no errors from validations
        for err_msg in form.errors.values():
            flash(f'there was an error creating a user: {err_msg}', category='danger')
        
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(form.password.data):
            login_user(attempted_user)
            flash(f"Erfolg! Du bist eingeloggt als: {attempted_user.username}", category='succsess')
            return redirect(url_for('api_check'))

        else:
            flash('Username and Password dont match. Please try again', category='danger')
     
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out", category='info')
    return redirect(url_for('home_page'))


@app.route('/danke')
def data():
    return render_template('thankyou.html')

@app.route('/check_user', methods=['GET', 'POST'])
@login_required
def api_check():
    form = CharForm()

    characters = Character.query.all()

    if request.method == "POST":
        char = Character.query.filter_by(character_id=form.char.data).first()
        options = form.options.data
        form = CharForm()
        
        # bunch of if statements for all classes
        if options == "W":
            form = CharForm()
            wallet = wallet_balance(char)
            journal = wallet_journal(char).data
            journal_len = range(len(journal))

            # send to site
            return render_template('test.html', current_char=char, characters=characters, form=form, wallet=wallet, wallet_journal=journal, journal_len=journal_len)

        elif options == "S":
            form = CharForm()
            att = attributes(char).data
            skills = getskills(char).data

            skills_list = get_skills(char)
            skill_len = range(len(skills_list))

            return render_template('test.html', form=form, attributes=att, skills=skills, skills_list=skills_list, skill_len=skill_len)

        elif options == "SQ":
            form = CharForm()
            quere = get_quere(char)
            quere_len = range(len(quere))
            return render_template('test.html', form=form, quere=quere, quere_len=quere_len)
            
        elif options == "M":
            form = CharForm()
            mailing_lists_name, mails, sender_names = get_mails(char)
            mail_len = range(len(mails))
            
            return render_template('test.html', form=form,mail_len=mail_len, mails=mails, mailing_lists_name=mailing_lists_name, sender_names=sender_names)

        elif options == "L":
            form = CharForm()
            location, online, ship = get_status(char)
            
            return render_template('test.html', form=form, char=char, location=location, online=online, ship=ship)
        
        elif options == "CL":
            form = CharForm()
            home_location, imps, current_imps = get_clones(char)
            
            return render_template('test.html', form=form, char=char, home_location=home_location, imps=imps, current_imps=current_imps)
        
        elif options == "BM":
            form = CharForm()
            bm_folders = get_bm_folder(char)
            if not bm_folders:
                dic ={"name":"Keine Bookmark Ordner, bugged zur Zeit."}
                bm_folders.append(dic) 

            return render_template('test.html', form=form, char=char, bm_folders=bm_folders)
        
        elif options == "C":
            contacts = get_contacts(char)
            return render_template('test.html', form=form, contacts=contacts)

        elif options == "CR":
            assignee_name, contracts_data = get_contracts(char)
            length = range(len(contracts_data))
            return render_template('test.html', form=form, contracts_data=contracts_data, assignee_name=assignee_name, length=length)
        else:
            return render_template('test.html', characters=characters, form=form)
        
        
    return render_template('test.html', characters=characters, form=form)


@app.route('/sso/callback')
def callback():
    """ This is where the user comes after he logged in SSO """
    # get the code from the login process
    code = request.args.get('code')
    token = request.args.get('state')

    # compare the state with the saved token for CSRF check
    sess_token = session.pop('token', None)
    if sess_token is None or token is None or token != sess_token:
        return 'Login EVE Online SSO failed: Session Token Mismatch', 403

    # now we try to get tokens
    try:
        auth_response = esisecurity.auth(code)
    except APIException as e:
        return 'Login EVE Online SSO failed: %s' % e, 403

    # we get the character informations
    cdata = esisecurity.verify()

    # if the user is already authed, we log him out
    #############
    # if current_user.is_authenticated:
    #     logout_user()
    #############
    # now we check in database, if the user exists
    # actually we'd have to also check with character_owner_hash, to be
    # sure the owner is still the same, but that's an example only...
    try:
        char = Character.query.filter(
            Character.character_id == cdata['sub'].split(':')[2],
        ).one()

    except NoResultFound:
        char = Character()
        char.character_id = cdata['sub'].split(':')[2]

    char.character_owner_hash = cdata['owner']
    char.character_name = cdata['name']
    char.update_token(auth_response)

    # now the user is ready, so update/create it and log the user
    try:
        db.session.merge(char)
        db.session.commit()

        # login_user(user)
        session.permanent = True

    except:
        # logger.exception("Cannot login the user - uid: %d" % user.character_id)
        db.session.rollback()
        # logout_user()

    return redirect(url_for("data"))