import discord
import random
import urllib3
import giphy_client
from giphy_client.rest import ApiException
import sqlite3
from sqlite3 import Error
import configparser
#Simple Discord Bot for practice in implementing APIs/creating & implementing database connectivity and management
#Not for public use, not available to add to servers, only exists as a personal exercise
#By Adrian Faircloth (Tomaeto)

'''------INITIALIZING VARIABLES/CONNECTIONS------'''
#Initializing Discord intents and client
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

#ConfigParser for reading data.ini for API keys and filepaths
parser = configparser.ConfigParser()
parser.read('data.ini')

#Initializing Giphy client instance
api_inst = giphy_client.DefaultApi()
giphy_config = {
'token': parser['Api Keys']['giphy_key'], 
'limit': 1,
'rating': 'r'
         }

#Initializing connection to database
conn = sqlite3.connect(parser['Bot Info']['path'])

#Initalizing admin ID for checking in admin-only commands
admin_id=int(parser['Bot Info']['admin_id'])

#Initializing sample embed
embed = discord.Embed(title = "Sample embed", description="This is a sample embed.")

#Initializing list to hold banned terms
banlist = []

'''------FUNCTIONS------'''
#Function for getting list of frog gifs from Giphy
def getFrogs():
    response = api_inst.gifs_search_get(giphy_config['token'], 'frog', limit = 100, rating = 'r')
    return list(response.data)

#Function for choosing a random gif from list of frog gifs
def chooseFrog(froglist):
    gif = random.choices(froglist)
    return gif[0].url

#Function for searching for a gif using Giphy API and returning the first result
def searchGif(term):
    response = api_inst.gifs_search_get(giphy_config['token'], term,  limit = giphy_config['limit'], rating = giphy_config['rating'])
    gif = response.data   
    if not gif:
        return None
    return gif[0].url

#Function for getting a specified user's banned messages
#Returns list of lists containing message date and text
def getUserBanMessages(user_id):
    sql = " SELECT msg_date, msg_text FROM banned_msgs WHERE user_id=?"
    cur = conn.cursor()
    cur.execute(sql, (str(user_id),))
    return cur.fetchall()

#Function for getting the list of banned terms and loading into local array
def getBanlist():
    sql = """ SELECT term FROM banned_terms """
    try:
        cur = conn.cursor()
        cur.execute(sql)
    except Error as e:
        return e;
    for term in cur.fetchall():
        banlist.append(term[0])

#Function for adding a term to the banned terms list
def addBannedTerm(term):
    sql = " INSERT INTO banned_terms(term) VALUES(?)"
    try:
        cur = conn.cursor()
        cur.execute(sql, (term,))
        conn.commit()
    except Error as e:
        return e
    return    

#Function for adding banned message to database and updating member's banned msg count
def addBannedMsg(user_id, message, date):
    sql_insert_msg = " INSERT INTO banned_msgs(user_id, msg_text, msg_date) VALUES(?,?,?);"
    sql_update_member = " UPDATE members SET banned_msg_count = banned_msg_count + 1 WHERE id =?;"
    try:
        cur = conn.cursor()
        cur.execute(sql_insert_msg, (user_id, message, date,))
        cur.execute(sql_update_member, (user_id,))
        conn.commit()
    except Error as e:
        return e
    return

'''------BOT EVENTS------'''
#Printing message when bot is initialized and populating banned term list
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    if (getBanlist() != None):
        print("Error retrieving banlist")
        exit(1)


#Bot actions on message
@client.event
async def on_message(message):        

    #Ignore messages from the bot
    if message.author == client.user:
        return

    #Action for dealing w/ messages containing banned terms
    #When a banned term is found, adds message to database, deletes message and informs user
    if any([term in message.content for term in banlist]):
        user_id = message.author.id
        text = message.content
        date = str(message.created_at)[0:10]

        #If an error is returned, print error
        error = addBannedMsg(user_id, text, date)
        if error:
            print(error)
            return
        
        #If error is None, delete message and inform user of their shameful display
        channel = message.channel
        await message.delete()
        await channel.send(f"<@{user_id}>, your message contained a banned term... shameful")
        return
    
    #Command for purging channel messages
    #Only usable by admin
    if message.content == "!purge":
        #Ignore command if not from admin
        if (message.author.id != admin_id):
            return
        
        await message.channel.purge()
        return
    
    #Command for getting a user's banned messages from the database
    #Currently in testing, only works for user
    if message.content == "!getbans":
        messages = getUserBanMessages(message.author.id)
        for msg in messages:
            await message.channel.send(msg[0] + ": " + msg[1])
        return
    
    
    #Command for getting list of banned terms
    if message.content == "!banlist":
        await message.channel.send("Banned Terms:")
        for term in banlist:
            await message.channel.send(term)
        return
    
    #Command for adding a term to the banned list
    #Called function returns error if term is already in list
    #Sends DM to admin instead of public message for security purposes
    if message.content.startswith("!addterm "):
        #Ignore command if not from admin
        if (message.author.id != admin_id):
            return
        
        term = message.content[9:]
        error = addBannedTerm(term)
        #If error is returned, notify user and print error
        if error:
            await message.author.send("Error adding term to database, check terminal for error.")
            print(error)
            return
        
        #If no error, add term to local array and notify admin of success
        banlist.append(term)
        await message.add_reaction('👍')
        await message.author.send("Successfully added " + term + " to the banlist.")
        return
       
    #Command for sending an embed with your account data (join date, creation date, user ID, and pfp)
    #Will be reworked to allow for sending embed with other user's data
    if message.content == "!profile":
        embed.title = message.author.display_name
        embed.description = message.author.raw_status
        embed.set_image(url=message.author.display_avatar)
        embed.add_field(name="Joined on:", value=str(message.author.joined_at)[0:10], inline=False)
        embed.add_field(name="Created on:", value=str(message.author.created_at)[0:10], inline=False)
        embed.add_field(name="User ID:", value=str(message.author.id))
        await message.channel.send(embed=embed)
        return
    
    #Command for sending a random frog gif
    #Grabs a random frog from list of gifs from Giphy and sends in channel
    if message.content == '!frog':
        try:
            frogif = chooseFrog(froglist)
            await message.channel.send(frogif)

        except ApiException as ex:
           print("Failure :(" ) 
        return

    #Command for searching for a gif and sending result 
    if message.content.lower().startswith('!search '):
        search = message.content[8:]
        gif = searchGif(search)
        if not gif:
            await message.channel.send("No gif found")
            return
        await message.channel.send(gif)
        return

    #Command for sending a specified user's profile picture
    #Takes user ID as argument, user must be member of server
    if message.content.startswith("!getpfp "):

        id = message.content[8:]
        if id.isdigit() != True:
            await message.channel.send("Correct command format is !getpfp <user_id>")
            return

        guild = client.get_guild(message.channel.guild.id)
        members = await guild.fetch_members().flatten()
        for mem in members:
            if mem.id == int(id):
                await message.channel.send(mem.avatar_url)
                return
        
        await message.channel.send('User not found in server')

    #Command for sending a random quote generated from Inspirobot website
    if message.content == "!inspire":
        https = urllib3.PoolManager()
        res = https.request("GET", "https://inspirobot.me/api?generate=true")
        text = str(res.data)
        text = text[2:len(text) - 1]
        await message.channel.send(text)
        return

    #Command for sending a random fact from API Ninjas website
    if message.content == "!fact":
        https = urllib3.PoolManager()
        res = https.request("GET", "https://api.api-ninjas.com/v1/facts?limit=1", headers = {"X-Api-Key": parser['Api Keys']['xapi_key']})
        text = str(res.data)
        text = text[13:len(text) - 4]
        text += '.'
        await message.channel.send(text)
        return

    #Command for sending Rumia gif
    if message.content == '!rumia':
         await message.channel.send('https://i.imgur.com/VtjUMai.gif')
         return
            
    #Command for sending Kyouko image
    if message.content == '!kyouko':
        await message.channel.send('https://i.imgur.com/GmDaXQX.png')
        return

#Setting up gif list and running bot
froglist = getFrogs()
client.run(parser['Api Keys']['discord_key'])