import sqlite3 as sq

DB_NAME = "db/materials.db"
TABLE = "materials"
MATERIAL = "Material"
S_HEAT_CAPACITY = "Specific Heat Capacity"
DENSITY = "Material Density"
CONDUCTIVITY = "Thermal Conductivity"
ID = "id"


def use(id):
    conn = sq.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM %s WHERE id = ?" % TABLE, (id,))
    data = cur.fetchall()
    conn.close()
    return data


def viewAll():
    conn = sq.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM %s" % TABLE)
    rows = cur.fetchall()
    conn.close()
    return rows


def search(material=""):
    conn = sq.connect(DB_NAME)
    cur = conn.cursor()
    query = "SELECT * FROM %s WHERE %s LIKE ?" % (TABLE, MATERIAL)
    cur.execute(query, ("%" + material + "%",))
    rows = cur.fetchall()
    conn.close()
    return rows
