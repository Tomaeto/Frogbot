import discord
import random
import urllib3
import giphy_client
from giphy_client.rest import ApiException

#Initializing Discord intents and client
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

#Initializing Giphy client instance
api_inst = giphy_client.DefaultApi()
config = {
'token': 'API-TOKEN', 
'limit': 1,
'rating': 'r'
         }

#Initializing sample embed
embed = discord.Embed(title = "Sample embed", description="This is a sample embed.")

#Function for getting list of frog gifs from Giphy
def getFrogs():
    response = api_inst.gifs_search_get(config['token'], 'frog', limit = 100, rating = 'g')
    return list(response.data)

#Function for choosing a random gif from list of frog gifs
def chooseFrog(froglist):
    gif = random.choices(froglist)
    return gif[0].url

#Function for searching for a gif using Giphy API and returning the first result
def searchGif(term):
    response = api_inst.gifs_search_get(config['token'], term,  limit = config['limit'], rating = config['rating'])
    gif = response.data   
    if not gif:
        return None
    return gif[0].url

#Printing message when bot is initialized
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

#Bot actions on message
@client.event
async def on_message(message):        

    if message.author == client.user:
        return

    #Command for purging channel messages
    if message.content == "!purge":
        await message.channel.purge()
        return
    
    #Command for sending an embed with your account data (join date, creation date, user ID, and pfp)
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
        res = https.request("GET", "https://api.api-ninjas.com/v1/facts?limit=1", headers = {"X-Api-Key": "API-KEY"})
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
client.run('BOT-TOKEN')