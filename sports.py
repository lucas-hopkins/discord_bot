from discord import embeds, team
from prettytable import PrettyTable
from discord.ext import commands
from dateutil import parser
from datetime import datetime
from dateutil import tz
import requests
import discord
import json
from errors import TeamNotFoundException

#Base Team Url - To Build Team Embed
ncaa_team_url = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/{id}"
nfl_team_url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{id}"
mlb_team_url = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/{id}"

#Statistics Urls - To Pull various items for the Team Embed
nfl_team_stats_url = "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2021/types/2/teams/{id}/statistics"

# Ranking Urls
ncaa_ranking_url = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/rankings"
nfl_ranking_url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/rankings"
mlb_ranking_url = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/rankings"

class RankingObject(object):
  current_rank = None
  previous_rank = None
  location =""
  team_name = ""
  headline = ""

  def __init__(self, current_rank, previous_rank, location, team_name, headline):
    self.current_rank = current_rank
    self.previous_rank = previous_rank
    self.location  = location
    self.team_name = team_name
    self.headline  = headline

class NFLTeamStatsObject(object):
  passing_yards = ""
  rushing_yards = ""
  fumbles = ""
  ints = ""

  def __init__(self, passing_yards, rushing_yards, fumbles, ints):
    self.passing_yards = passing_yards
    self.rushing_yards = rushing_yards
    self.fumbles = fumbles
    self.ints = ints

class ScoresObject(object):
  dt = ""
  score = ""
  shortName = ""
  longName = ""
  home_schedule_url = ""
  away_schedule_url = ""

  def __init__(self, dt, score, short_name, long_name, home_schedule_url, away_schedule_url):
    self.dt = dt
    self.score = score
    self.short_name = short_name
    self.long_name = long_name
    self.home_schedule_url = home_schedule_url
    self.away_schedule_url = away_schedule_url

class TeamObject(NFLTeamStatsObject, object):
  display_name = ""
  logo = ""
  stats = {}
  record = ""

  def __init__(self, display_name, logo, stats, record):
    self.display_name = display_name
    self.logo = logo
    self.stats = stats
    self.record = record

def make_ranking_object(current_rank, previous_rank, location, team_name, headline):
  rO = RankingObject(current_rank, previous_rank, location, team_name, headline)
  return rO

def make_team_object(display_name, logo, stats, record):
  tO = TeamObject(display_name, logo, stats, record)
  return tO


def make_team_stats_object(passing_yards, rushing_yards, fumbles, ints):
  tSO = NFLTeamStatsObject(passing_yards, rushing_yards, fumbles, ints)
  return tSO


def make_scoreObject(dt, score, short_name, long_name, home_schedule_url, away_schedule_url):
  sO = ScoresObject(dt, score, short_name, long_name,
                    home_schedule_url, away_schedule_url)
  return sO


class Sports(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def games(self, ctx, arg1):

    # Converts API"s UTC format to Local Time
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    #Current week Upcoming
    api = "http://site.api.espn.com/apis/site/v2/sports/"
    nfl_scores = "football/nfl/scoreboard"
    mlb_scores = "baseball/mlb/scoreboard"
    ncaa_scores = "football/college-football/scoreboard"

    if arg1 == "mlb":
      response = requests.get(api + mlb_scores).json()
      season = response["season"]["year"]
      events = response["events"]

    elif arg1 == "cfl":
      response = requests.get(api + ncaa_scores).json()

    elif arg1 == "nfl":
      response = requests.get(api + nfl_scores).json()
      events = response["events"]
      week = response["week"]["number"]

    # Extract data from API and create list of Objects to later use to build the embed
    list_of_events = []
    for event in events:
      sN = event["shortName"]  # Abbreviated Team Name
      lN = event["name"]      # Full team names
      dt = parser.parse(event["date"][0:16])  # UTC Datetime
      utc = dt.replace(tzinfo=from_zone)
      dt = utc.astimezone(to_zone)
      date_time = datetime.strftime(dt, "%m-%d-%Y %I:%M")  # 09-27-2021 12:00

      #get home away team urls
      # is competitor[0] always home and [1] always away
      home_schedule_url = event["competitions"][0]["competitors"][0]["team"]["links"][3]["href"]
      #home_logo_url = event["competitions"][0]["competitors"][0]["team"]["logo"]
      away_schedule_url = event["competitions"][0]["competitors"][1]["team"]["links"][3]["href"]
      #away_logo_url = event["competitions"][0]["competitors"][1]["team"]["logo"]
      score = event["competitions"][0]["competitors"][0]["score"] + \
          "-" + event["competitions"][0]["competitors"][1]["score"]
      sO = make_scoreObject(date_time, score, sN, lN,
                            home_schedule_url, away_schedule_url)
      list_of_events.append(sO)

    # def chunks(lst, n):  # yields n sized iterables
    #   for i in range(0, len(lst), n):
    #     yield lst[i:i + n]

    table = PrettyTable()
    if arg1 == "nfl":
      table.title = f"NFL Games: Week: {week}"
      table.field_names = ["Team", "Date/Time", "Score"]
    if arg1 == "mlb":
      table.title = "MLB Games"
      table.field_names = ["Team", "Date/Time", "Score"]
    for sportsObject in list_of_events:
      table.add_row([f"{sportsObject.short_name}",
                    f"{sportsObject.dt}", f"{sportsObject.score}"])
    await ctx.send(f"```{table}```")

    # Consider swithcing to embed_from_dict

  @commands.command()
  async def teams(self, ctx, arg1, arg2):
    if arg2 == "dolphins":
      await ctx.send(file= discord.File("saban.jpg"))
    if arg1 == "nfl":
      f = open("nfl_teams.json")
      list_of_teams = json.load(f)
      for team in list_of_teams["teams"]:
        if arg2 in team:
          team_id = team[arg2]
          res = requests.get(nfl_team_url.format(id=team_id)).json()
          stats_res = requests.get(nfl_team_stats_url.format(id=team_id)).json()

          stats_object = make_team_stats_object(passing_yards=stats_res["splits"]["categories"][1]["stats"][8]["value"],
                                                rushing_yards=stats_res["splits"]["categories"][2]["stats"][6]["value"],
                                                fumbles=stats_res["splits"]["categories"][0]["stats"][0]["value"],
                                                ints=stats_res["splits"]["categories"][1]["stats"][5]["value"]
                                                )

          team_object = make_team_object(display_name=res["team"]["displayName"],
                                        logo=res["team"]["logos"][1]["href"],
                                        stats=stats_object,
                                        record=res["team"]["record"]["items"][0]["summary"]
                                        )

          e = discord.Embed()
          e.title = team_object.display_name
          e.set_thumbnail(url=team_object.logo)
          e.add_field(name="Passing Yards",
                      value=team_object.stats.passing_yards)
          e.add_field(name="Rushing Yards",
                      value=team_object.stats.rushing_yards)
          e.add_field(name="Fumbles", value=team_object.stats.fumbles)
          e.add_field(name="Ints", value=team_object.stats.ints)
          e.add_field(name="Current Record", value=team_object.record)
          await ctx.send(embed=e)

  @commands.command()
  async def ranking(self, ctx, arg1):
    if arg1 == "nfl":
      pass
    if arg1 == "ncaa":
      res = requests.get(ncaa_ranking_url).json()
    
      headlines = res["rankings"][1]["shortHeadline"]
      list_of_team_rankings = res["rankings"][0]["ranks"]
      for team in list_of_team_rankings:
        ranking_object = make_ranking_object(current_rank=team["current"],
                                 previous_rank=team["previous"],
                                 team_name=team["team"]["name"],
                                 location=team["team"]["location"],
                                 headline=headlines)
    
      e = discord.Embed()
      e.title = ranking_object.headline
      e.add_field(name="Location",
                  value=ranking_object.location)
      e.add_field(name="Team",
                  value=ranking_object.team_name)
      e.add_field(name="Current Rank", value=ranking_object.current_rank)
      e.add_field(name="Previous Rank", value=ranking_object.previous_rank)
      await ctx.send(embed=e)
    if arg1 == "mlb":
      pass
