from EVE import esisecurity, esiapp, esiclient
from EVE.models import skill, skill_abst

from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def wallet_journal(char):
    journal = None
    current_char = char
    esisecurity.update_token(current_char.get_sso_data())
    tokens = esisecurity.refresh()

    op = esiapp.op['get_characters_character_id_wallet_journal'](
        character_id=current_char.character_id
        )


    journal = esiclient.request(op)

    return journal

def get_logo():
    # get char id
    op = esiapp.op['get_characters_character_id'](
        character_id=96076326
        )
    char_corp = esiclient.request(op).data
    char_corp = char_corp['corporation_id']

    # get corp logo
    op = esiapp.op['get_corporations_corporation_id_icons'](
        corporation_id =char_corp
        )
    logo = esiclient.request(op).data
    # px256x256
    print(logo)



def wallet_balance(char):
    # create the request
    wallet = None

    # if current_user.is_authenticated:
    # give the token data to esisecurity, it will check alone
    # if the access token need some update

    # get current character
    current_char = char
    esisecurity.update_token(current_char.get_sso_data())
    tokens = esisecurity.refresh()
    # print(tokens)

    op = esiapp.op['get_characters_character_id_wallet'](
        character_id=current_char.character_id
        )
    wallet = esiclient.request(op)

    return wallet

def attributes(char):
    attributes = None

    esisecurity.update_token(char.get_sso_data())
    tokens = esisecurity.refresh()

    op = esiapp.op['get_characters_character_id_attributes'](
        character_id = char.character_id
        )
    attributes = esiclient.request(op)

    return attributes

def getskills(char):
    skills = None

    esisecurity.update_token(char.get_sso_data())
    tokens = esisecurity.refresh()

    op = esiapp.op['get_characters_character_id_skills'](
        character_id = char.character_id
        )
    skills = esiclient.request(op)

    return skills
    
def get_mails(char):
    # Token Refresh
    esisecurity.update_token(char.get_sso_data())
    tokens = esisecurity.refresh()

    # Mailing lists
    mailing_lists = None

    op = esiapp.op['get_characters_character_id_mail_lists'](
        character_id = char.character_id
        )
    mailing_lists = esiclient.request(op).data
    mailing_lists_name = []
    for mlist in mailing_lists:
        mln = mlist['name']
        mailing_lists_name.append(mln)

    # Mails 
    mails = None

    op = esiapp.op['get_characters_character_id_mail'](
        character_id = char.character_id
        )
    mails = esiclient.request(op).data

    # put body in json obj
    for mail in mails:
        # request body
        op = esiapp.op['get_characters_character_id_mail_mail_id'](
            character_id = char.character_id,
            mail_id = mail['mail_id']
        )
        res = esiclient.request(op).data
        m = res['body']
        mail['body'] = strip_tags(m)

    # resolve recipients id
    for mail in mails:
        recipients_names = []
        for res in mail['recipients']:
            # distinguish types
            if res['recipient_type'] == 'character':
                op = esiapp.op['get_characters_character_id'](
                    character_id = res['recipient_id'],
                )
                answer = esiclient.request(op).data
                recipients_names.append(answer['name'])
            elif res['recipient_type'] == 'corporation':
                op = esiapp.op['get_corporations_corporation_id'](
                    corporation_id = res['recipient_id'],
                )
                answer = esiclient.request(op).data
                recipients_names.append(answer['name'])
            elif res['recipient_type'] == 'alliance':
                op = esiapp.op['get_alliances_alliance_id'](
                    alliance_id = res['recipient_id'],
                )
                answer = esiclient.request(op).data
                recipients_names.append(answer['name'])                
            elif res['recipient_type'] == 'mailing_list':
                for lis in mailing_lists:
                    if res['recipient_id'] == lis['mailing_list_id']:
                        recipients_names.append(lis['name'])
                        break
        # put in new subsection 
        upd_dic = {'recipients_names':recipients_names}  
        mail['recipients'].append(upd_dic)
        # recipients_names
        # print(mail['recipients'])

    # resolve sender name
    sender_names = []
    for mail in mails:
        op = esiapp.op['get_characters_character_id'](
            character_id = mail['from']
            )
        answer = esiclient.request(op).data
        # print(answer['name'])
        try:
            sender_names.append(answer['name'])
        except:
            sender_names.append("Name not found")
        # print(answer['name']) 
        # mail_name = {'name':answer['name']}       
        # mail.update(mail_name)
        # print(type(mail))
    # print(type(mails))

    return mailing_lists_name, mails, sender_names


def names(skill_id):
    skill_data = None

    op = esiapp.op['post_universe_names'](
        ids = skill_id
        )
    skill_data = esiclient.request(op)

    return skill_data

def get_skills(char):
    # get skills
    s = getskills(char).data
    skills = s['skills']
    # print(skills)

    skill_ids = []
    trained_sl = []
    # get skill ids and trained lvl
    for i in range(len(skills)):
        skill_ids.append(skills[i]['skill_id'])
        trained_sl.append(skills[i]['trained_skill_level'])

    skill_list = []
    counter = 0
    for id in skill_ids:
        sk = skill.query.filter_by(skill_id=id).first()
        # print(sk)
        l = skill_abst(sk.skill_name, sk.skill_category_name, trained_sl[counter])
        skill_list.append(l)
        counter += 1

    return skill_list

def get_quere(char):
    q = None

    esisecurity.update_token(char.get_sso_data())
    tokens = esisecurity.refresh()

    op = esiapp.op['get_characters_character_id_skillqueue'](
        character_id = char.character_id
        )
    q = esiclient.request(op).data

    skill_ids = []
    training_skill_lvl = []
    position = []

    quere = []
    # get skill ids, training lvl and position in quere
    for i in range(len(q)):
        skill_ids.append(q[i]['skill_id'])
        training_skill_lvl.append(q[i]['finished_level'])
        position.append(q[i]['queue_position'])

    skill_names = names(skill_ids).data

    for i in range(len(skill_names)):
        l = [position[i], skill_names[i], training_skill_lvl[i]]
        quere.append(l)

    return quere

def get_status(char):
    location_id = None
    location_name = None
    online = None
    ship_id = None
    ship = None

    esisecurity.update_token(char.get_sso_data())
    tokens = esisecurity.refresh()

    # get char location id
    op = esiapp.op['get_characters_character_id_location'](
        character_id = char.character_id
        )
    location_id = esiclient.request(op).data
    location_id = location_id['solar_system_id']

    # print(location_id)

    # convert location id to string
    op1 = esiapp.op['get_universe_systems_system_id'](
        system_id=location_id
    )

    location_name = esiclient.request(op1).data
    location_name = location_name['name']

    # get online status (last login, last logout, online)
    op2 = esiapp.op['get_characters_character_id_online'](
        character_id = char.character_id)

    online = esiclient.request(op2).data
 
    # get ship_id
    op3 = esiapp.op['get_characters_character_id_ship'](
        character_id = char.character_id)

    ship_id = esiclient.request(op3).data
    ship_id = ship_id['ship_type_id']

    # get ship name
    op4 = esiapp.op['get_universe_types_type_id'](
        type_id=ship_id)

    ship = esiclient.request(op4).data
    ship = ship['name']

    return location_name, online, ship


def get_clones(char):
    clone_data = None

    # refresh access token
    esisecurity.update_token(char.get_sso_data())
    tokens = esisecurity.refresh()

    # request for clone data
    op = esiapp.op['get_characters_character_id_clones'](
        character_id = char.character_id
        )

    clone_data = esiclient.request(op).data

    home_location_id = clone_data['home_location']['location_id']

    # transforming location ids to names
    op1 = esiapp.op['post_universe_names'](
        ids=[home_location_id])

    home_location = esiclient.request(op1).data
    home_location = home_location[0]['name']

    # getting jump clones
    clones = clone_data['jump_clones']

    implants_ids = []
    location_ids = []
    for clone in clones:
        # implants_ids = list of list
        implants_ids.append(clone['implants'])
        location_ids.append(clone['location_id'])

    # getting jump clone locations from ids
    structure_names = []
    structure_solar_id = []
    for loc in location_ids:
        op2 = esiapp.op['get_universe_structures_structure_id'](
            structure_id=loc
        )
        structure = esiclient.request(op2).data
        structure_names.append(structure['name'])
        structure_solar_id.append(structure['solar_system_id'])

    structure_solar_name = []
    for solar_id in structure_solar_id:
        op2 = esiapp.op['get_universe_systems_system_id'](
                system_id=solar_id)
        s = esiclient.request(op2).data
        s = s['name']
        structure_solar_name.append(s)

    # getting names of the imps
    implantss = []
    for implants in implants_ids:
        if implants != []:
            op = esiapp.op['post_universe_names'](
                ids = implants
            )
            imps = esiclient.request(op).data
            i=[]
            for imp in imps:
                i.append(imp['name'])
            implantss.append(i)

        else:
            implantss.append([None])


    # # combine imps with there location
    imps = []
    for i in range(len(structure_names)):
        imp = [structure_names[i], structure_solar_name[i], implantss[i]]
        imps.append(imp)
    
    # print(imps[0][2])

    # get current imps
    op3 = esiapp.op['get_characters_character_id_implants'](
        character_id = char.character_id)

    current_imps_ids = esiclient.request(op3).data

    # get names for current imps
    current_imps = []
    for imp in current_imps_ids:
        op4 = esiapp.op['get_universe_types_type_id'](
            type_id = imp)

        current_imps.append(esiclient.request(op4).data)

    return home_location, imps, current_imps

# getting Bookmark Folders 
def get_bm_folder(char):
    bm_folders = None

    esisecurity.update_token(char.get_sso_data())
    tokens = esisecurity.refresh()

    # get char location id
    op = esiapp.op['get_characters_character_id_bookmarks_folders'](
        character_id = char.character_id
        )

    bm_folders = esiclient.request(op).data
    
    print([bm_folders])

    return bm_folders

# getting Contacts
def get_contacts(char):
    esisecurity.update_token(char.get_sso_data())
    tokens = esisecurity.refresh()

    # get char contacts and standing
    op = esiapp.op['get_characters_character_id_contacts'](
        character_id = char.character_id
        )
    contacts = esiclient.request(op).data

    contact_id = []
    contact_name = []
    contact_type = []
    contact_standing = []
    for c in contacts:
        contact_id.append(c['contact_id'])
        contact_type.append(c['contact_type'])
        contact_standing.append(c['standing'])

    # resolve contact_id to player
    for c in range(len(contact_id)):
        if contact_type[c] == 'character':
            op = esiapp.op['get_characters_character_id'](
                character_id = contact_id[c]
                )
            c_name = esiclient.request(op).data
            # print(c_name)
            c_name = c_name['name']
            contact_name.append(c_name)
        elif contact_type[c] == 'corporation':
            op = esiapp.op['get_corporations_corporation_id'](
                corporation_id = contact_id[c]
                )
            c_name = esiclient.request(op).data
            # print(c_name)
            c_name = c_name['name']
            contact_name.append(c_name)
        elif contact_type[c] == 'alliance':
            op = esiapp.op['get_alliances_alliance_id'](
                alliance_id = contact_id[c]
                )
            c_name = esiclient.request(op).data
            # print(c_name)
            c_name = c_name['name']
            contact_name.append(c_name)
        else:
            contact_name.append("Faction")

    if len(contact_name) == len(contact_type) and len(contact_name) == len(contact_standing):
        contacts = []
        for i in range(len(contact_name)):
            c = [contact_name[i], contact_type[i], contact_standing[i]]
            contacts.append(c)

        # print(contacts)
        return contacts

def get_contracts(char):
    esisecurity.update_token(char.get_sso_data())
    tokens = esisecurity.refresh()

    # get contracts
    op = esiapp.op['get_characters_character_id_contracts'](
        character_id = char.character_id
        )
    contracts_data = esiclient.request(op).data

    assignee_id = []
    for contract in contracts_data:
        assignee_id.append(contract['assignee_id'])

    assignee_name = []
    for assignee in assignee_id:
        op = esiapp.op['get_characters_character_id'](
            character_id = assignee
            )
        name = esiclient.request(op).data

        if not name:
            op = esiapp.op['get_corporations_corporation_id'](
            character_id = assignee
            )
            name = esiclient.request(op).data

        if not name:
            name = None

        assignee_name.append(name)

    return assignee_name, contracts_data


        

    





