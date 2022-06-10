import csv, sqlite3


def getDataAndPrint(cur):
    cur.execute("SELECT * FROM materials")
    data = cur.fetchall()
    print(data)


def createTable(cur, con):

    # Creating table and columns
    cur.execute(
        "CREATE TABLE materials (id INTEGER,Material TEXT,'Thermal Conductivity' REAL,'Thermal Diffusivity' REAL,'Specific Heat Capacity' REAL,'Thermal Effusivity' REAL,'Material Density' REAL);"
    )

    # Converting .csv to .db format
    with open("materials_data.csv", "r") as file:
        # Reading the first line from the file for column headings
        dr = csv.DictReader(file)
        for i in dr:
            to_db = [
                (
                    i["id"],
                    i["Material"],
                    i["Thermal Conductivity"],
                    i["Thermal Diffusivity"],
                    i["Specific Heat Capacity"],
                    i["Thermal Effusivity"],
                    i["Material Density"],
                )
                for i in dr
            ]

    # Inserting data to database
    cur.executemany(
        "INSERT INTO materials (id,Material,'Thermal Conductivity','Thermal Diffusivity','Specific Heat Capacity','Thermal Effusivity','Material Density') VALUES (?, ?, ?, ?, ?, ?, ?);",
        to_db,
    )

    # Commiting changes
    con.commit()


# Connecting into DB
con = sqlite3.connect("materials.db")

# Creating cursor
cur = con.cursor()

# createTable(cur,con)

# getDataAndPrint(cur)
cur.execute("SELECT * FROM materials WHERE Material LIKE '?'", ["iro"])
print(cur.fetchall())
# Closing connection
con.close()
