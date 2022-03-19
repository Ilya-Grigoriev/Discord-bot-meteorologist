import asyncio
from discord.ext import commands
import discord
import requests
from datetime import datetime

TOKEN = "TOKEN_BOT"


class Meteorologist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pos = None
        self.lat = None
        self.lon = None

    @commands.command(name='help_bot')
    async def help_bot(self, ctx):
        await ctx.send(
            '#!place - setting a place\n#!current - getting weather information\n#!forecast {days} - getting weather ' +
            'forecast for several days (no more than 7)')

    @commands.command(name='place')
    async def place(self, ctx, pos):
        self.pos = pos
        geocoder_request = f'http://geocode-maps.yandex.ru/1.x/?apikey=API-KEYb&geocode="{self.place}"&format=json'
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()
            pos = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point']['pos']
            self.lon, self.lat = pos.split()
        else:
            print("Request execution error:")
            print(geocoder_request)
            print("Http status:", response.status_code, "(", response.reason, ")")
        await ctx.send('The new place has been successfully set')

    @commands.command(name='current')
    async def current(self, ctx):
        headers = {'lat': self.lat, 'lon': self.lon, 'lang': 'ru_RU',
                   'X-Yandex-API-Key': 'API-KEY'}
        response = requests.get('https://api.weather.yandex.ru/v2/forecast?', headers=headers).json()
        ts = int(response['now'])
        date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
        temp = response['fact']['temp']
        pressure = response['fact']['pressure_mm']
        humidity = response['fact']['humidity']
        condition = response['fact']['condition']
        wind_dir = response['fact']['wind_dir']
        wind_speed = response['fact']['wind_speed']
        await ctx.send(f'Weather forecast in {self.pos.capitalize()} for {date}:')
        await ctx.send(f'Temperature: {temp},')
        await ctx.send(f'Pressure: {pressure} mm,')
        await ctx.send(f'Humidity: {humidity}%,\n{condition},')
        await ctx.send(f'Wind {wind_dir}, {wind_speed} m/s.')

    @commands.command(name='forecast')
    async def forecast(self, ctx, days):
        if int(days) < 8:
            headers = {'lat': self.lat, 'lon': self.lon, 'lang': 'ru_RU',
                       'X-Yandex-API-Key': 'API-KEY',
                       'limit': days}
            response = requests.get('https://api.weather.yandex.ru/v2/forecast?', headers=headers).json()
            for i in response['forecasts'][:int(days)]:
                temp = i['parts']['day_short']['temp']
                prec_mm = i['parts']['day_short']['prec_mm']
                await ctx.send(f'Weather forecast in {self.pos.capitalize()} for {i["date"]}:')
                await ctx.send(f'Temperature: {temp},')
                await ctx.send(f'Precipitation amount: {prec_mm} mm')
                await ctx.send('-------------------------------------------------------------')
        else:
            await ctx.send('The number of days should not exceed 7')


bot = commands.Bot(command_prefix='#!')
bot.add_cog(Meteorologist(bot))
bot.run(TOKEN)
