import sqlite3 as sl
import cipher


def get_all_patients():
    con = sl.connect("resources/database.db")
    cursor = con.cursor()
    cursor.execute("SELECT * FROM patients")
    encrypted_patients = cursor.fetchall()
    con.close()
    patients = [
        (p[0], cipher.decrypt(p[1]), cipher.decrypt(p[2]), cipher.decrypt(p[3]), p[4], p[5], cipher.decrypt(p[6]), p[7], p[8], p[9], p[10], p[11], p[12], p[13])
        for p in encrypted_patients
    ]
    return patients


def add_patient(surname, name, patronymic, sex, height, weight, date_of_birth, passport, date_of_receipt):
    con = sl.connect("resources/database.db")
    sql = '''
        INSERT INTO patients(surname, name, patronymic, sex, height, weight, date_of_birth, passport, date_of_receipt,  p_id)
        SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT MAX(p_id) + 1 FROM patients), 1);
        '''
    data = (
        cipher.encrypt(surname), cipher.encrypt(name), cipher.encrypt(patronymic), sex, height, weight,
        date_of_birth, cipher.encrypt(passport), date_of_receipt
    )
    con.execute(sql, data)
    con.commit()
    con.close()


def remove_patient(p_id):
    con = sl.connect("resources/database.db")
    sql = 'DELETE FROM patients WHERE p_id = ?'
    data = (p_id,)
    con.execute(sql, data)
    con.commit()
    con.close()


def update_patient(p_id, surname, name, patronymic, sex, date_of_birth, passport, height, weight, complaints, inspection, diagnosis, therapy, date_of_receipt):
    con = sl.connect("resources/database.db")
    sql = '''
    UPDATE patients
    SET surname = ?, name = ?, patronymic = ?, sex = ?, date_of_birth = ?, passport = ?, 
        height = ?, weight = ?, complaints = ?, inspection = ?, diagnosis = ?, therapy = ?, date_of_receipt = ?
    WHERE p_id = ?
    '''
    data = (
        cipher.encrypt(surname), cipher.encrypt(name), cipher.encrypt(patronymic), sex, date_of_birth, cipher.encrypt(passport),
        height, weight, complaints, inspection, diagnosis, therapy, date_of_receipt, p_id
    )
    con.execute(sql, data)
    con.commit()
    con.close()


def find_patient(info):
    con = sl.connect('resources/database.db')
    cursor = con.cursor()
    sql = 'SELECT * FROM patients'
    cursor.execute(sql)
    encrypted_patients = cursor.fetchall()
    con.close()
    patients = [
        (p[0], cipher.decrypt(p[1]), cipher.decrypt(p[2]), cipher.decrypt(p[3]), p[4], p[5], cipher.decrypt(p[6]), p[7], p[8], p[9], p[10], p[11], p[12], p[13])
        for p in encrypted_patients
    ]
    found_patients = [
        p for p in patients if info.lower() in p[1].lower() or info.lower() in p[2].lower()
                               or info.lower() in p[3].lower() or info.lower() in p[6].lower() or info.lower() in p[5].lower()
    ]
    return found_patients


def get_medicines(prefix):
    conn = sl.connect('resources/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT M_TITLE FROM medicines WHERE M_TITLE LIKE ?', ('%' + prefix.lower() + '%',))
    all_medicines = [row[0] for row in cursor.fetchall()]
    conn.close()
    return all_medicines


def get_diseases(prefix):
    conn = sl.connect('resources/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT D_TITLE FROM diseases WHERE D_TITLE LIKE ?', ('%' + prefix.lower() + '%',))
    all_diseases = [row[0] for row in cursor.fetchall()]
    conn.close()
    return all_diseases
