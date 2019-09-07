import mysql.connector
import subprocess

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='makerecipesgreatagain',
)

mycursor = mydb.cursor()

mycursor.execute('DROP DATABASE RECIPE')
mydb.commit()

mycursor.execute('CREATE DATABASE RECIPE')
mydb.commit()

sqlfile = open('./initsql.sql', 'r')
sqlconfig = sqlfile.read().split('\n')
for line in sqlconfig:
    mycursor.execute(line)
    mydb.commit()

mycursor.execute('USE RECIPE')
mydb.commit()

tablefile = open('./recipe.csv', 'r')
tablestring = tablefile.read().replace(',\"\"\",\"\"\"', '\"\"\",\"\"\"').replace('\\', '').split('\n')[:-2]
for line in tablestring:
    temp = line.split(',')[0]

    mycursor.execute('CREATE TABLE ' + temp + '(\n\tid\tINT unsigned NOT NULL AUTO_INCREMENT,'
                                              '\n\tingredients\tLONGTEXT NOT NULL,\n\tPRIMARY KEY(id)\n);')
    mydb.commit()
    values = ''
    for index in line.split(',\"\"'):
        tempIndex = index[:-2]
        tempIndex = tempIndex.replace('\"\"', '')
        if tempIndex != temp[:-2]:
            values += '\t(' + tempIndex + '),\n'
    values = (values[:-2] + ';').replace('\'', '').replace('\"', '\'')
    if values is not ';':
        print('INSERT INTO ' + temp + ' ( ingredients) VALUES\n' + values)
        mycursor.execute('INSERT INTO ' + temp + ' ( ingredients) VALUES\n' + values)
        mydb.commit()
        subprocess.call(["clear"])
print('done')
