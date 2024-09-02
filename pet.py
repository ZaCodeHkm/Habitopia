# The current working code is used to create a table to persistently store the time when it is run. To be used to measure time between pet visits
# as a way to simulate the pets getting hungry over time without using an actual server.
    # TO-DO: 
    # DONE 1. Make it so that no new rows of lastvisitTime are created. I want it so that during each successful visit, lastvisitTime will be replaced by the 
    # previous currentTime. 
    # DONE 2. To calculate the difference between the two and store it in a new column.
    # DONE 3. New column or table to be added to make the hunger loss cumulative. Otherwise, people will keep logging in to prevent the hunger loss from 
    # reducing. 
    # DONE 3a.Make the cumulative column only reset when fed.
    # 4. Make redirect to /pet after petfeed
    # WIP 5. Create buttons on pet.html
    # 5a. First one will be a button to select pet. Make it so correct rows (correct pets) are selected based off the button pressed.
    # 6. Food/feeding system and how it connects to the hunger loss mechanic. Resets the hunger bar to a certain level.
    # 7. Make unique pet ID system that will save to a different table or row depending on the pet.
    # 8. Make basic display section in pet.html to show to mr willie.
    # 9. Comm with shawn so that he also includes the pet number as a stat to record for each user. Explanation down below in the DEPENDENCY section.
    # DONE 10. Make currentTime be recorded. It will be the time recorded for every visit except the first.
    # DONE 11. Make the hunger bar.
    # 12. Connect this system to the account system. Basically, need code to read user ID and display the correct pet information. (ex: #of petsOwned, petName, petEvolution, etc.)

import time, sqlite3
#change table to use last fed time instead?
#------ACTUAL CODE------#
petsOwned = 1 #temporary until there is a counter for pets owned for each user.
lastvisitTime = (time.time(),) #apparently, this must be a tuple in order to replace any qmarks in the line below. #also, apparently not.
currentTime = (time.time(),)
#------FUNCTIONS------#
def hungerFunc():
    currentTime = (time.time(),)
    conn_obj = sqlite3.connect('petdata.db', check_same_thread=False)
    curs_obj = conn_obj.cursor()
    curs_obj.execute("UPDATE Time SET (lastvisittime) = (currentTime)")
    curs_obj.execute("UPDATE Time SET (currentTime) = (?)", currentTime)
    curs_obj.execute("UPDATE Time SET (timeDifference) = (currentTime) - (lastvisitTime)")
    curs_obj.execute("UPDATE Time SET (cumulativeDiff) = (cumulativeDiff) + (timeDifference)")
    timeTuple = curs_obj.execute("SELECT cumulativeDiff from Time").fetchone()
    feedTime = timeTuple[0]
    curs_obj.execute("UPDATE Time SET (petHunger) = 100")
    print("Time since last fed: " + str(feedTime))
    if feedTime >= 20 and feedTime < 172800:
        curs_obj.execute("UPDATE Time SET (petHunger) = 67")
    if feedTime >= 172800 and feedTime < 259200:
        curs_obj.execute("UPDATE Time SET (petHunger) = 34")
    if feedTime >= 259200 and feedTime < 345600:  
        curs_obj.execute("UPDATE Time SET (petHunger) = 1")
    if feedTime >= 345600:
        curs_obj.execute("UPDATE Time SET (petHunger) = 0")
        print('petLoss') #temporary to show what happens if the user messes up.
    conn_obj.commit()

def getHunger(): 
    #initially put this in one function (hungerFunc). issue is, trying to get petHunger from it resulted in it 
    # running twice. thanks to a comment by u/GeorgeFranklyMathnet on reddit for this simple solution of splitting it up.
    conn_obj = sqlite3.connect('petdata.db', check_same_thread=False)
    curs_obj = conn_obj.cursor()
    hungerTuple = curs_obj.execute("SELECT petHunger from Time").fetchone()
    pH = hungerTuple[0]
    return pH

# petHunger = str(getHunger()) #leaving this as a reminder. this value is static and only obtained when starting the page. which is
# not good enough for when i need the hunger value to be obtained immediately. solution was to add getHunger() directly in the app.route
# for the feeding system (/petfeed). this way, every time feed button is pressed, flask detects it and runs both getHunger() and feedFunc(),
# updating the meter immediately.

def feedFunc():
    conn_obj = sqlite3.connect('petdata.db', check_same_thread=False)
    curs_obj = conn_obj.cursor()
    curs_obj.execute("UPDATE Time SET (petHunger) = 100")
    curs_obj.execute("UPDATE Time SET (cumulativeDiff) = 0")
    
    conn_obj.commit()

    

    #when certain button is clicked, reset pet hunger to max. (For now)
    #finding out how to connect HTML buttons to this code.s

#def firstPet()
#------END FUNCTIONS------#



#define connection and cursor
conn_obj = sqlite3.connect('petdata.db', check_same_thread=False)
curs_obj = conn_obj.cursor()

#create table to store pet data.
petTable = """CREATE TABLE IF NOT EXISTS
Time (
petID INTEGER PRIMARY KEY,
lastvisitTime INTEGER,
currentTime INTEGER)"""

#inputting and recording the time that the user last visited the pet page (also used for the first time)
curs_obj.execute(petTable)
if petsOwned == 0:  #for first time. the user will be given a free pet. every other visit will not use this code.
    curs_obj.execute("UPDATE Time SET (currentTime) = (?)", (currentTime))
    conn_obj.commit() #to make the change persistent
    petsOwned += 1 #to simulate the user getting their first pet. this will 'disable' this section of code for every visit after. 
else:
    if petsOwned >= 1: # every visit after the 1st will use this function for each pet.
        hungerFunc()
conn_obj.commit()


curs_obj.execute("SELECT lastvisitTime,currentTime FROM Time ORDER BY lastvisitTime DESC LIMIT 1")
print(curs_obj.fetchone()) #temporary, just to show that it still works when coding/testing.
conn_obj.close()

#---DEPENDENCY ON OTHER SYSTEMS---#
# need shawn to create a counter for number of pets owned. if that number is 0 then below pseudocode will display the free pet choice and
# tutorial.
# if petsOwned == 0:
#     popUp freepetchoice.ui
#     print tutorial #have to figure out how to make buttons (to allow the user to choose a free pet)

# also need the account system, or at least the ID part of it done so I have a unique ID to use to pull up the correct pet data 
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

