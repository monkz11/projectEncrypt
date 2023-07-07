from encrypt import User, bcrypt

def hash_mrz(mrz):
    return bcrypt.generate_password_hash(mrz).decode('utf-8')

def is_new_user(mrz):
    users = User.query.all()
    for user in users:
        mrz_hash = user.mrz_hash
        print('--- Printing MRZ hash')
        print(mrz_hash)
        print('--- printing mrz')
        print(mrz)
        if (bcrypt.check_password_hash(mrz_hash, mrz)): 
            print('a matching mrz was found')
            return False
    return True