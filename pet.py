# The current working code is used to create a table to persistently store the time when it is run. To be used to measure time between pet visits
# as a way to simulate the pets getting hungry over time without using an actual server.
    # TO-DO: 
    # DONE 1. Make it so that no new rows of lastvisitTime are created. I want it so that during each successful visit, lastvisitTime will be replaced by the 
    # previous currentTime. 
    # 2. To calculate the difference between the two and store it in a new column. To make the hunger loss cumulative with each visit.
    # 3. New column or table to be added to make the hunger loss cumulative. Otherwise, people will keep logging in to prevent the hunger loss from 
    # reducing. 
    # 4. Food/feeding system and how it connects to the hunger loss mechanic. Resets the hunger bar to a certain level.
    # 5. Make unique pet ID system that will save to a different table or row depending on the pet.
    # 6. Make basic display section in pet.html to show to mr willie.
    # 7. Comm with shawn so that he also includes the pet number as a stat to record for each user. Explanation down below in the DEPENDENCY section.
    # DONE 8. Make currentTime be recorded. It will be the time recorded for every visit except the first.
    # 9. Make the hunger bar.
    # 

import time, sqlite3

petsOwned = 1 #temporary until there is a counter for pets owned for each user.
lastvisitTime = (time.time(),) #apparently, this must be a tuple in order to replace any qmarks in the line below. #also, apparently not.
currentTime = (time.time(),)
petHunger = 100

#------ACTUAL CODE------#
#define connection and cursor
conn_obj = sqlite3.connect('petdata.db')
curs_obj = conn_obj.cursor()

#create table to store pet data
petTable = """CREATE TABLE IF NOT EXISTS
Time (
petID INTEGER PRIMARY KEY,
lastvisitTime INTEGER,
currentTime INTEGER)"""

#inputting and recording the time that the user last visited the pet page (also used for the first time)
curs_obj.execute(petTable)
while petsOwned == 0:  #for first time. the user will be given a free pet. every other visit will not use this code.
    curs_obj.execute("INSERT INTO Time (currentTime) VALUES (?)", (currentTime))
    conn_obj.commit() #to make the change persistent
    petsOwned += 1 #to simulate the user getting a pet. this will disable this section of code for every visit after.
else:
    if petsOwned >= 1: # every visit after the 1st will use this code.
        curs_obj.execute("UPDATE Time SET (lastvisittime) = (currentTime)")
        curs_obj.execute("UPDATE Time SET (currentTime) = (?)", currentTime)
        conn_obj.commit()


curs_obj.execute("SELECT lastvisitTime,currentTime FROM Time ORDER BY lastvisitTime DESC LIMIT 1")
print(curs_obj.fetchone()) #temporary, just to show that it still works when coding/testing.
print(petHunger)
conn_obj.close()

#---DEPENDENCY ON OTHER SYSTEMS---#
# need shawn to create a counter for number of pets owned. if that number is 0 then below pseudocode will display the free pet choice and
# tutorial.
# if petsOwned == 0:
#     popUp freepetchoice.ui
#     print tutorial #have to figure out how to make popups that are interactive (to allow the user to choose a free pet)
# record lastvisitTime (also used to record time of the first visit. which is planned so that it is replaced with the previous currentTime in every other visit.)

# also need the account system, or at least the ID part of it done so I have a unique ID to use to pull up the correct pet database 
# for each user. (should I make separate database for each user? is that a waste? maybe i have to make the table more detailed.)





#----code i was using to figure out what I wanted)----#
# firsttimepetPage = 0
# accesspetPage = 1 #temporary. to change from 1 to something that detects when the user enters the petpage. probably related to flask.
# if accesspetPage == 1:
#     if firsttimepetPage == 0:
#         firsttimepetPage = 1
#         print("Pet system explanation")
#     timepasscheck = time.time()
#     # print(time.time())

