##sql functions:

def create_server_connection(host_name, user_name, user_password,database_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=database_name,
            auth_plugin = 'mysql_native_password'
        )
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as err:
        print(f"Error: '{err}'")

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

from flask import request
from flask import redirect
from flask import Flask, render_template, request
import mysql.connector
import datetime
from datetime import date
import time
from mysql.connector import Error
app = Flask(__name__)

connection = create_server_connection("127.0.0.1", "root", "D24HD24H", "countries")

@app.route('/', methods=['GET', 'POST'])
def country_table():
    if request.method == "POST":
        formData = request.values
        value=formData.getlist('country');
        length=len(value);
        
        today = date.today()
        curr_time = time.strftime("%H:%M:%S", time.localtime())

        countries=["NULL"]*5

        for x in range(length):
            countries[x]=formData.getlist('country')[x]


        q1="""INSERT INTO country
                        VALUES
                    ('"""+str(countries[0])+"""',
                    '"""+str(countries[1])+"""',
                    '"""+str(countries[2])+"""',
                    '"""+str(countries[3])+"""',
                    '"""+str(countries[4])+"""',
                    '"""+str(today)+"""',
                    '"""+str(curr_time)+"""',
                    '"""+str(length)+"""');"""

        execute_query(connection, q1)
        return redirect("/plot", code=302)
    else:
        return render_template('index.html')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

mycursor = connection.cursor()
mycursor.execute("select * from country")
result = mycursor.fetchall
 
Names = []
Dates = []
Times = []
data = []
res = []
z=0

for i in mycursor:
    res.append(i[5]+" "+i[6])
    data.append({'time': res[z], 'id': z+1})
    Dates.append(i[5])
    Times.append(i[6])
    for j in range(5):
        Names.append(i[j])
    z=z+1
 
elm_count_0 = Names.count("France")
elm_count_1 = Names.count("Germany")
elm_count_2 = Names.count("Japan")
elm_count_3 = Names.count("Korea")
elm_count_4 = Names.count("Singapore")
elm_count_5 = Names.count("USA")
elm_count_6 = Names.count("Canada")
elm_count_7 = Names.count("Australia")
elm_count_8 = Names.count("UK")
elm_count_9 = Names.count("China")

no_of_vote=int(int(len(Names))/5)

@app.route('/plot')
def plot():

    x = ["France", "Germany", "Japan", "Korea", "Singapore", "USA", "Canada", "Australia", "UK", "China"]
    y = [elm_count_0, elm_count_1, elm_count_2, elm_count_3, elm_count_4, elm_count_5, elm_count_6, elm_count_7, elm_count_8, elm_count_9]

    sorted_data = sorted(zip(y, x), reverse=True)

    top_items = sorted_data[:3]

    top_item_names = [item for _, item in top_items]
    top_item_votes = [vote for vote, _ in top_items]
    
    plt.subplot(211)
    plt.figure(figsize=(10,10))

    plt.bar(top_item_names, top_item_votes)

    plt.ylabel('Vote Counts')
    plt.xlabel('Country')

    plt.title('Total vote: '+str(no_of_vote)+'\n Top 3 Favorite countries')

    plt.savefig('static/fig/country_vote.png',bbox_inches='tight')

    import pandas as pd

    df = pd.DataFrame(list(data))

    df['time'] = pd.to_datetime(df['time'])

    current_time = pd.to_datetime('now')
    start_time = current_time - pd.DateOffset(hours=24)
    filtered_data = df[df['time'] >= start_time]

    interval_data = filtered_data.groupby(pd.Grouper(key='time', freq='H')).size()

    time_intervals = interval_data.index.strftime('%H:%M')
    id_counts = interval_data.values
    
    plt.subplot(212)
    plt.figure(figsize=(10,6))

    plt.plot(time_intervals, id_counts, marker='o')

    plt.xlabel('Time Intervals')
    plt.ylabel('Number of participate')
    plt.title('Last 24-Hour Distribution')

    plt.xticks(rotation=45)


    plt.savefig('static/fig/Timedistribution.png',bbox_inches='tight')

    return render_template('plot.html', url='/static/fig/country_vote.png', trl='/static/fig/Timedistribution.png')

if __name__ == '__main__':
    app.run()
