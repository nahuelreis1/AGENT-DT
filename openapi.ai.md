# API-FOOTBALL v3.9.3 — Reference for AI

_Generated: 2026-07-10 13:22_
_Source: openapi.yaml_

**Base URL:**
```
https://v3.football.api-sports.io
```

## Authentication

We uses API keys to allow access to the API. You can register a new API key in our [dashboard](https://dashboard.api-football.com/register).

**API-SPORTS** : https://v3.football.api-sports.io/


Our API expects for the API key to be included in all API requests to the server in a header that looks like the following:

> Make sure to replace `XxXxXxXxXxXxXxXxXxXxXxXx` with your API key.

**REQUESTS HEADERS & CORS**

The API is configured to work only with **GET** requests and allows only the headers listed below:
* `x-apisports-key`

If you make non-GET requests or add headers that are not in the list, you will receive an error from the API.

Some frameworks *(especially in JS, nodeJS..)* automatically add extra headers, you have to make sure to remove them in order to get a response from the API.

## API-SPORTS Account

If you decided to subscribe directly on our site, you have a dashboard at your disposal at the following url: [dashboard](https://dashboard.api-football.com/register)


It allows you to:

* To follow your consumption in real time
* Manage your subscription and change it if necessary
* Check the status of our servers
* Test all endpoints without writing a line of code.

You can also consult all this information directly through the API by calling the endpoint `status`.

> This call does not count against the daily quota.

```json
get("https://v3.football.api-sports.io/status");

// response
{
    "get": "status",
    "parameters": [],
    "errors": [],
    "results": 1,
    "response": {
        "account": {
            "firstname": "xxxx",
            "lastname": "XXXXXX",
            "email": "xxx@xxx.com"
        },
        "subscription": {
            "plan": "Free",
            "end": "2020-04-10T23:24:27+00:00",
            "active": true
        },
        "requests": {
            "current": 12,
            "limit_day": 100
        }
    }
}
```

### Headers sent as response

When consuming our API, you will always receive the following headers appended to the response:

* `x-ratelimit-requests-limit`: The number of requests allocated per day according to your subscription.
* `x-ratelimit-requests-remaining`: The number of remaining requests per day according to your subscription.
* `X-RateLimit-Limit`: Maximum number of API calls per minute.
* `X-RateLimit-Remaining`: Number of API calls remaining before reaching the limit per minute.

### Rate Limiting Policy
If you exceed your allowed request rate per minute, either through continuous excessive usage or by generating abnormal traffic spikes, your access may be temporarily or permanently blocked by our firewall without prior notice. This ensures service stability and fair usage for all customers.

### Dashboard
![dashboard](https://www.api-football.com/public/img/news/baseball-dashboard.png)

### Requests
![requests](https://www.api-football.com/public/img/news/baseball-requests.png)

### Live tester
![requests](https://www.api-football.com/public/img/news/baseball-live.png)

### Response headers (always present)

| Header | Meaning |
|---|---|
| `x-ratelimit-requests-limit` | Requests per day for your plan |
| `x-ratelimit-requests-remaining` | Requests remaining today |
| `X-RateLimit-Limit` | Max calls per minute |
| `X-RateLimit-Remaining` | Calls remaining this minute |

### Response envelope

All responses share the same envelope:
- `get` (string): endpoint name
- `parameters` (array): echoed query params
- `errors` (array|object): validation errors, or 0-item object on success
- `results` (integer): number of items in `response`
- `paging` (object): `{ current, total }` pagination cursors
- `response` (array): the actual data

## Table of Contents

### Coachs

- [`GET /coachs`](#coachs) — Coachs

### Countries

- [`GET /countries`](#countries) — Countries

### Fixtures

- [`GET /fixtures/rounds`](#fixtures-rounds) — Rounds
- [`GET /fixtures`](#fixtures) — Fixtures
- [`GET /fixtures/headtohead`](#fixtures-headtohead) — Head To Head
- [`GET /fixtures/statistics`](#fixtures-statistics) — Statistics
- [`GET /fixtures/events`](#fixtures-events) — Events
- [`GET /fixtures/lineups`](#fixtures-lineups) — Lineups
- [`GET /fixtures/players`](#fixtures-players) — Players statistics

### Injuries

- [`GET /injuries`](#injuries) — Injuries

### Leagues

- [`GET /leagues`](#leagues) — Leagues
- [`GET /leagues/seasons`](#leagues-seasons) — Seasons

### Odds (In-Play)

- [`GET /odds/live`](#odds-live) — odds/live
- [`GET /odds/live/bets`](#odds-live-bets) — odds/live/bets

### Odds (Pre-Match)

- [`GET /odds`](#odds) — Odds
- [`GET /odds/mapping`](#odds-mapping) — Mapping
- [`GET /odds/bookmakers`](#odds-bookmakers) — Bookmakers
- [`GET /odds/bets`](#odds-bets) — Bets

### Players

- [`GET /players/seasons`](#players-seasons) — Seasons
- [`GET /players/profiles`](#players-profiles) — Profiles
- [`GET /players`](#players) — Statistics
- [`GET /players/squads`](#players-squads) — Squads
- [`GET /players/teams`](#players-teams) — Teams
- [`GET /players/topscorers`](#players-topscorers) — Top Scorers
- [`GET /players/topassists`](#players-topassists) — Top Assists
- [`GET /players/topyellowcards`](#players-topyellowcards) — Top Yellow Cards
- [`GET /players/topredcards`](#players-topredcards) — Top Red Cards

### Predictions

- [`GET /predictions`](#predictions) — Predictions

### Sidelined

- [`GET /sidelined`](#sidelined) — Sidelined

### Standings

- [`GET /standings`](#standings) — Standings

### Teams

- [`GET /teams`](#teams) — Teams information
- [`GET /teams/statistics`](#teams-statistics) — Teams statistics
- [`GET /teams/seasons`](#teams-seasons) — Teams seasons
- [`GET /teams/countries`](#teams-countries) — Teams countries

### Timezone

- [`GET /timezone`](#timezone) — Timezone

### Transfers

- [`GET /transfers`](#transfers) — Transfers

### Trophies

- [`GET /trophies`](#trophies) — Trophies

### Venues

- [`GET /venues`](#venues) — Venues

---

## `GET /timezone` — Timezone

**Tags:** Timezone
**Operation ID:** `get-timezone`

Get the list of available timezone to be used in the fixtures endpoint.

> This endpoint does not require any parameters.

**Update Frequency** : This endpoint contains all the existing timezone, it is not updated.

**Recommended Calls** : 1 call when you need.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<string>
}
```

**Example** (`All`):
```json
get: timezone
parameters: []
errors: []
results: 425
paging:
  current: 1
  total: 1
response:
- Africa/Abidjan
- Africa/Accra
- Africa/Addis_Ababa
- Africa/Algiers
- Africa/Asmara
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: timezone parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   bu...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/timezone"
params = {}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/timezone", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /countries` — Countries

**Tags:** Countries
**Operation ID:** `get-countries`

Get the list of available countries for the `leagues` endpoint.

The `name` and `code` fields can be used in other endpoints as filters.

To get the flag of a country you have to call the following url: `https://media.api-sports.io/flags/{country_code}.svg`


All the parameters of this endpoint can be used together.

**Update Frequency** : This endpoint is updated each time a new league from a country not covered by the API is added.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `name` | query | string | no | The name of the country |
| `code` | query | string pattern: FR, GB-ENG, IT…  minLength: 2 maxLength: 6 | no | The Alpha code of the country |
| `search` | query | string minLength: 3 maxLength: 3 | no | The name of the country |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<  object {
      name: string
      code: string
      flag: string
    }>
}
```

**Example** (`All`):
```json
get: countries
parameters:
  name: england
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- name: England
  code: GB
  flag: https://media.api-sports.io/flags/gb.svg
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: countries parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   b...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/countries"
params = {
    "name": '<name>',  # The name of the country
    "code": '<code>',  # The Alpha code of the country
    "search": '<search>',  # The name of the country
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/countries", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /leagues` — Leagues

**Tags:** Leagues
**Operation ID:** `get-leagues`

Get the list of available leagues and cups.

The league `id` are **unique** in the API and leagues keep it across all `seasons`

To get the logo of a competition you have to call the following url: `https://media.api-sports.io/football/leagues/{league_id}.png`

This endpoint also returns the `coverage` of each competition, which makes it possible to know what is available for that league or cup.

The values returned by the coverage indicate the **data available at the moment** you call the API, so for a competition that has not yet started, it is normal to have all the features set to `False`. This will be updated once the competition has started.

> You can find all the leagues ids on our [Dashboard](https://dashboard.api-football.com/soccer/ids).

**Example :**
```
"coverage": {
  "fixtures": {
      "events": true,
      "lineups": true,
      "statistics_fixtures": false,
      "statistics_players": false
  },
  "standings": true,
  "players": true,
  "top_scorers": true,
  "top_assists": true,
  "top_cards": true,
  "injuries": true,
  "predictions": true,
  "odds": false
}

```
In this example we can deduce that the competition does not have the following features: `statistics_fixtures`, `statistics_players`, `odds` because it is set to `False`.

The coverage of a competition can vary from season to season and values set to `True` do not guarantee 100% data availability.

Some competitions, such as the `friendlies`, are exceptions to the coverage indicated in the `leagues` endpoint, and the data available may differ depending on the match, including livescore, events, lineups, statistics and players.

Competitions are automatically renewed by the API when a new season is available. There may be a delay between the announcement of the official calendar and the availability of data in the API.

For `Cup` competitions, fixtures are automatically added when the two participating teams are known. For example if the current phase is the 8th final, the quarter final will be added once the teams playing this phase are known.


> Most of the parameters of this endpoint can be used together.

**Update Frequency** : This endpoint is updated several times a day.

**Recommended Calls** : 1 call per hour.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `id` | query | integer | no | The id of the league |
| `name` | query | string | no | The name of the league |
| `country` | query | string | no | The country name of the league |
| `code` | query | string pattern: FR, GB-ENG, IT…  minLength: 2 maxLength: 6 | no | The Alpha code of the country |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | no | The season of the league |
| `team` | query | integer | no | The id of the team |
| `type` | query | string enum: league \| cup | no | The type of the league  |
| `current` | query | string enum: true \| false pattern:  Return the list of active seasons or the last one of each competition | no | The state of the league |
| `search` | query | string minLength: 3 | no | The name or the country of the league |
| `last` | query | integer maxLength: 2 | no | The X last leagues/cups added in the API |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<  object {
      league:     object {
            id: integer
            name: string
            type: string
            logo: string
          }
      country:     object {
            name: string
            code: string
            flag: string
          }
      seasons: array<    object {
            year: integer
            start: string
            end: string
            current: boolean
            coverage:       object {
                    fixtures:         object {
                              events: boolean
                              lineups: boolean
                              statistics_fixtures: boolean
                              statistics_players: boolean
                            }
                    standings: boolean
                    players: boolean
                    top_scorers: boolean
                    predictions: boolean
                    odds: boolean
                  }
          }>
    }>
}
```

**Example** (`All`):
```json
get: leagues
parameters:
  id: '39'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- league:
    id: 39
    name: Premier League
    type: League
    logo: https://media.api-sports.io/football/leagues/2.png
  country:
    name: England
    code: GB
    flag: https://media.api-sports.io/flags/gb.svg
  seasons:
  - year: 2010
    start: '2010-08-14'
    end: '2011-05-17'
    current: false
    coverage:
      fixtures:
        events: true
        lineups: true
        statistics_fixtures: false
        statistics_players: false
      standings: true
      players: true
      top_scorers: true
      top_assists: true
      top_cards: true
      injuries: true
      predictions: true
      odds: false
  - year: 2011
    start: '2011-08-13'
    end: '2012-05-13'
    current: false
    coverage:
      fixtures:
        events: true
        lineups: true
        statistics_fixtures: false
        statistics_players: false
      standings: true
      players: true
      top_scorers: true
      top_assists: true
      top_cards: true
      injuries: true
      predictions: true
      odds: false
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: leagues parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   bug...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/leagues"
params = {
    "id": '<id>',  # The id of the league
    "name": '<name>',  # The name of the league
    "country": '<country>',  # The country name of the league
    "code": '<code>',  # The Alpha code of the country
    "season": '<season>',  # The season of the league
    "team": '<team>',  # The id of the team
    "type": '<type>',  # The type of the league
    "current": '<current>',  # The state of the league
    "search": '<search>',  # The name or the country of the league
    "last": '<last>',  # The X last leagues/cups added in the API
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/leagues", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /leagues/seasons` — Seasons

**Tags:** Leagues
**Operation ID:** `get-seasons`

Get the list of available seasons.

All seasons are only **4-digit keys**, so for a league whose season is `2018-2019` like the English Premier League (EPL), the `2018-2019` season in the API will be `2018`.

All `seasons` can be used in other endpoints as filters.

> This endpoint does not require any parameters.

**Update Frequency** : This endpoint is updated each time a new league is added.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |

### Response 200 — OK

**Schema:**
```
object {
  response: array<string>
  results: integer
  errors: array<  object {
      field: string
    }>
  parameters: array<  object {
      field: string
    }>
  get: string
}
```

**Example** (`All`):
```json
get: leagues/seasons
parameters: []
errors: []
results: 12
paging:
  current: 1
  total: 1
response:
- 2008
- 2010
- 2011
- 2012
- 2013
- 2014
- 2015
- 2016
- 2017
- 2018
- 2019
- 2020
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: leagues/seasons parameters: [] errors:   time: '2019-11-26T00:00:00+00:0...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/leagues/seasons"
params = {}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/leagues/seasons", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /teams` — Teams information

**Tags:** Teams
**Operation ID:** `get-teams`

Get the list of available teams.

The team `id` are **unique** in the API and teams keep it among all the leagues/cups in which they participate.

To get the logo of a team you have to call the following url: `https://media.api-sports.io/football/teams/{team_id}.png`

> You can find all the teams ids on our [Dashboard](https://dashboard.api-football.com/soccer/ids/teams).


> All the parameters of this endpoint can be used together.

**This endpoint requires at least one parameter.**

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

**Tutorials** :
- [HOW TO GET ALL TEAMS AND PLAYERS FROM A LEAGUE ID](https://www.api-football.com/tutorials/4/how-to-get-all-teams-and-players-from-a-league-id)

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `id` | query | integer | no | The id of the team |
| `name` | query | string | no | The name of the team |
| `league` | query | integer | no | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | no | The season of the league |
| `country` | query | string | no | The country name of the team |
| `code` | query | string minLength: 3 maxLength: 3 | no | The code of the team |
| `venue` | query | integer | no | The id of the venue |
| `search` | query | string minLength: 3 | no | The name or the country name of the team |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<  object {
      team:     object {
            id: integer
            name: string
            code: string
            country: string
            founded: integer
            national: boolean
            logo: string
          }
      venue:     object {
            id: integer
            name: string
            address: string
            city: string
            capacity: integer
            surface: string
            image: string
          }
    }>
}
```

**Example** (`All`):
```json
get: teams
parameters:
  id: '33'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- team:
    id: 33
    name: Manchester United
    code: MUN
    country: England
    founded: 1878
    national: false
    logo: https://media.api-sports.io/football/teams/33.png
  venue:
    id: 556
    name: Old Trafford
    address: Sir Matt Busby Way
    city: Manchester
    capacity: 76212
    surface: grass
    image: https://media.api-sports.io/football/venues/556.png
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: teams parameters:   id: 33 errors:   time: '2019-11-26T00:00:00+00:00'  ...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/teams"
params = {
    "id": '<id>',  # The id of the team
    "name": '<name>',  # The name of the team
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
    "country": '<country>',  # The country name of the team
    "code": '<code>',  # The code of the team
    "venue": '<venue>',  # The id of the venue
    "search": '<search>',  # The name or the country name of the team
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/teams?id=33", headers=headers)

res = conn.getresponse()
data = res.read()
```

---

## `GET /teams/statistics` — Teams statistics

**Tags:** Teams
**Operation ID:** `get-teams-statistics`

Returns the statistics of a team in relation to a given competition and season.

It is possible to add the `date` parameter to calculate statistics from the beginning of the season to the given date. By default the API returns the statistics of all games played by the team for the competition and the season.

**Update Frequency** : This endpoint is updated twice a day.

**Recommended Calls** : 1 call per day for the teams who have at least one fixture during the day otherwise 1 call per week.

> Here is an example of what can be achieved

![demo-teams-statistics](https://www.api-football.com/public/img/demo/demo-teams-statistics.png)

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `league` | query | integer | yes | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | yes | The season of the league |
| `team` | query | integer | yes | The id of the team |
| `date` | query | string pattern: YYYY-MM-DD | no | The limit date |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response:   object {
      league:     object {
            id: integer
            name: string
            country: string
            logo: string
            flag: string
            season: integer
          }
      team:     object {
            id: integer
            name: string
            logo: string
          }
      matches:     object {
            played:       object {
                    home: integer
                    away: integer
                    total: integer
                  }
            wins:       object {
                    home: integer
                    away: integer
                    total: integer
                  }
            draws:       object {
                    home: integer
                    away: integer
                    total: integer
                  }
            loses:       object {
                    home: integer
                    away: integer
                    total: integer
                  }
          }
      goals:     object {
            for:       object {
                    total:         object {
                              home: integer
                              away: integer
                              total: integer
                            }
                    average:         object {
                              home: string
                              away: string
                              total: string
                            }
                  }
            against:       object {
                    total:         object {
                              home: integer
                              away: integer
                              total: integer
                            }
                    average:         object {
                              home: string
                              away: string
                              total: string
                            }
                  }
          }
    }
}
```

**Example** (`All`):
```json
get: teams/statistics
parameters:
  league: '39'
  season: '2019'
  team: '33'
errors: []
results: 11
paging:
  current: 1
  total: 1
response:
  league:
    id: 39
    name: Premier League
    country: England
    logo: https://media.api-sports.io/football/leagues/39.png
    flag: https://media.api-sports.io/flags/gb-eng.svg
    season: 2019
  team:
    id: 33
    name: Manchester United
    logo: https://media.api-sports.io/football/teams/33.png
  form: WDLDWLDLDWLWDDWWDLWWLWLLDWWDWDWWWWDWDW
  fixtures:
    played:
      home: 19
      away: 19
      total: 38
    wins:
      home: 10
      away: 8
      total: 18
    draws:
      home: 7
      away: 5
      total: 12
    loses:
      home: 2
      away: 6
      total: 8
  goals:
    for:
      total:
        home: 40
        away: 26
        total: 66
      average:
        home: '2.1'
        away: '1.4'
        total: '1.7'
      minute:
        0-15:
          total: 4
          percentage: 6.06%
        16-30:
          total: 17
          percentage: 25.76%
        31-45:
          total: 11
          percentage: 16.67%
        46-60:
          total: 13
          percentage: 19.70%
        61-75:
          total: 10
          percentage: 15.15%
        76-90:
          total: 8
          percentage: 12.12%
        91-105:
          total: 3
          percentage: 4.55%
        106-120:
          total: null
          percentage: null
      under_over:
        '0.5':
          over: 30
          under: 8
        '1.5':
          over: 20
          under: 18
        '2.5':
          over: 11
          under: 27
        '3.5':
          over: 4
          under: 34
        '4.5':
          over: 1
          under: 37
    against:
      total:
        home: 17
        away: 19
        total: 36
      average:
        home: '0.9'
        away: '1.0'
        total: '0.9'
      minute:
        0-15:
          total: 6
          percentage: 16.67%
        16-30:
          total: 3
          percentage: 8.33%
        31-45:
          total: 7
          percentage: 19.44%
        46-60:
          total: 9
          percentage: 25.00%
        61-75:
          total: 3
          percentage: 8.33%
        76-90:
          total: 5
          percentage: 13.89%
        91-105:
          total: 3
          percentage: 8.33%
        106-120:
          total: null
          percentage: null
      under_over:
        '0.5':
          over: 25
          under: 13
        '1.5':
          over: 10
          under: 28
        '2.5':
          over: 1
          under: 37
        '3.5':
          over: 0
          under: 38
        '4.5':
          over: 0
          under: 38
  biggest:
    streak:
      wins: 4
      draws: 2
      loses: 2
    wins:
      home: 4-0
      away: 0-3
    loses:
      home: 0-2
      away: 2-0
    goals:
      for:
        home: 5
        away: 3
      against:
        home: 2
        away: 3
  clean_sheet:
    home: 7
    away: 6
    total: 13
  failed_to_score:
    home: 2
    away: 6
    total: 8
  penalty:
    scored:
      total: 10
      percentage: 100.00%
    missed:
      total: 0
      percentage: 0%
    total: 10
  lineups:
  - formation: 4-2-3-1
    played: 32
  - formation: 3-4-1-2
    played: 4
  - formation: 3-4-2-1
    played: 1
  - formation: 4-3-1-2
    played: 1
  cards:
    yellow:
      0-15:
        total: 5
        percentage: 6.85%
      16-30:
        total: 5
        percentage: 6.85%
      31-45:
        total: 16
        percentage: 21.92%
      46-60:
        total: 12
        percentage: 16.44%
      61-75:
        total: 14
        percentage: 19.18%
      76-90:
        total: 21
        percentage: 28.77%
      91-105:
        total: null
        percentage: null
      106-120:
        total: null
        percentage: null
    red:
      0-15:
        total: null
        percentage: null
      16-30:
        total: null
        percentage: null
      31-45:
        total: null
        percentage: null
      46-60:
        total: null
        percentage: null
      61-75:
        total: null
        percentage: null
      76-90:
        total: null
        percentage: null
      91-105:
        total: null
        percentage: null
      106-120:
        total: null
        percentage: null
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: teams/statistics parameters:   team: '33'   league: '39'   season: '2019...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/teams/statistics"
params = {
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
    "team": '<team>',  # The id of the team
    "date": '<date>',  # The limit date
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/teams/statistics?season=2019&team=33&league=39", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /teams/seasons` — Teams seasons

**Tags:** Teams
**Operation ID:** `get-teams-seasons`

Get the list of seasons available for a team.


**This endpoint requires at least one parameter.**

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `team` | query | integer | yes | The id of the team |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: teams/seasons
parameters:
  team: '33'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- 2010
- 2011
- 2012
- 2013
- 2014
- 2015
- 2016
- 2017
- 2018
- 2019
- 2020
- 2021
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: teams parameters:   id: 33 errors:   time: '2019-11-26T00:00:00+00:00'  ...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/teams/seasons"
params = {
    "team": '<team>',  # The id of the team
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/teams/seasons?team=33", headers=headers)

res = conn.getresponse()
data = res.read()
```

---

## `GET /teams/countries` — Teams countries

**Tags:** Teams
**Operation ID:** `get-teams-countries`

Get the list of countries available for the `teams` endpoint.

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: teams/countries
parameters: []
errors: []
results: 258
paging:
  current: 1
  total: 1
response:
- name: England
  code: GB
  flag: https://media.api-sports.io/flags/gb.svg
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: teams parameters:   id: 33 errors:   time: '2019-11-26T00:00:00+00:00'  ...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/teams/countries"
params = {}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/teams/countries", headers=headers)

res = conn.getresponse()
data = res.read()
```

---

## `GET /venues` — Venues

**Tags:** Venues
**Operation ID:** `get-venues`

Get the list of available venues.

The venue `id` are **unique** in the API.

To get the image of a venue you have to call the following url: `https://media.api-sports.io/football/venues/{venue_id}.png`


> All the parameters of this endpoint can be used together.

**This endpoint requires at least one parameter.**

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `id` | query | integer | no | The id of the venue |
| `name` | query | string | no | The name of the venue |
| `city` | query | string | no | The city of the venue |
| `country` | query | string | no | The country name of the venue |
| `search` | query | string minLength: 3 | no | The name, city or the country of the venue |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<  object {
      id: integer
      name: string
      address: string
      city: string
      country: string
      capacity: integer
      surface: string
      image: string
    }>
}
```

**Example** (`All`):
```json
get: venues
parameters:
  id: '556'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- id: 556
  name: Old Trafford
  address: Sir Matt Busby Way
  city: Manchester
  country: England
  capacity: 76212
  surface: grass
  image: https://media.api-sports.io/football/venues/556.png
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: venues parameters:   id: 556 errors:   time: '2019-11-26T00:00:00+00:00'...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/venues"
params = {
    "id": '<id>',  # The id of the venue
    "name": '<name>',  # The name of the venue
    "city": '<city>',  # The city of the venue
    "country": '<country>',  # The country name of the venue
    "search": '<search>',  # The name, city or the country of the venue
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/venues?id=556", headers=headers)

res = conn.getresponse()
data = res.read()
```

---

## `GET /standings` — Standings

**Tags:** Standings
**Operation ID:** `get-standings`

Get the standings for a league or a team.

Return a table of one or more rankings according to the league / cup.

Some competitions have several rankings in a year, group phase, opening ranking, closing ranking etc…


> Most of the parameters of this endpoint can be used together.

**Update Frequency** : This endpoint is updated every hour.

**Recommended Calls** : 1 call per hour for the leagues or teams who have at least one fixture in progress otherwise 1 call per day.

**Tutorials** :
- [HOW TO GET STANDINGS FOR ALL CURRENT SEASONS](https://www.api-football.com/tutorials/6/how-to-get-standings-for-all-current-seasons)

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `league` | query | integer | no | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | yes | The season of the league |
| `team` | query | integer | no | The id of the team |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: standings
parameters:
  league: '39'
  season: '2019'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- league:
    id: 39
    name: Premier League
    country: England
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: https://media.api-sports.io/flags/gb.svg
    season: 2019
    standings:
    - - rank: 1
        team:
          id: 40
          name: Liverpool
          logo: https://media.api-sports.io/football/teams/40.png
        points: 70
        goalsDiff: 41
        group: Premier League
        form: WWWWW
        status: same
        description: Promotion - Champions League (Group Stage)
        all:
          played: 24
          win: 23
          draw: 1
          lose: 0
          goals:
            for: 56
            against: 15
        home:
          played: 12
          win: 12
          draw: 0
          lose: 0
          goals:
            for: 31
            against: 9
        away:
          played: 12
          win: 11
          draw: 1
          lose: 0
          goals:
            for: 25
            against: 6
        update: '2020-01-29T00:00:00+00:00'
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: standings parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   b...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/standings"
params = {
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
    "team": '<team>',  # The id of the team
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/standings?league=39&season=2019", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /fixtures/rounds` — Rounds

**Tags:** Fixtures
**Operation ID:** `get-fixtures-rounds`

Get the rounds for a league or a cup.

The `round` can be used in endpoint fixtures as filters


**Update Frequency** : This endpoint is updated every day.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `league` | query | integer | yes | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | yes | The season of the league |
| `current` | query | boolean enum: true \| false | no | The current round only |
| `dates` | query | boolean enum: true \| false | no | Add the dates of each round in the response |
| `timezone` | query | string | no | A valid timezone from the endpoint `Timezone` |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`Default`):
```json
get: fixtures/rounds
parameters:
  league: '39'
  season: '2019'
errors: []
results: 38
paging:
  current: 1
  total: 1
response:
- Regular Season - 1
- Regular Season - 2
- Regular Season - 3
- Regular Season - 4
- Regular Season - 5
- Regular Season - 6
- Regular Season - 7
- Regular Season - 8
- Regular Season - 9
- Regular Season - 10
- Regular Season - 11
- Regular Season - 12
- Regular Season - 13
- Regular Season - 14
- Regular Season - 15
- Regular Season - 16
- Regular Season - 17
- Regular Season - 18
- Regular Season - 18
- Regular Season - 19
- Regular Season - 20
- Regular Season - 21
- Regular Season - 22
- Regular Season - 23
- Regular Season - 24
- Regular Season - 25
- Regular Season - 26
- Regular Season - 27
- Regular Season - 28
- Regular Season - 29
- Regular Season - 30
- Regular Season - 31
- Regular Season - 32
- Regular Season - 33
- Regular Season - 34
- Regular Season - 35
- Regular Season - 36
- Regular Season - 37
- Regular Season - 38
```

**Example** (`With dates parameter`):
```json
get: fixtures/rounds
parameters:
  league: '39'
  season: '2024'
  dates: 'true'
errors: []
results: 38
paging:
  current: 1
  total: 1
response:
- round: Regular Season - 1
  dates:
  - '2024-08-16'
  - '2024-08-17'
  - '2024-08-18'
  - '2024-08-19'
- round: Regular Season - 2
  dates:
  - '2024-08-24'
  - '2024-08-25'
- round: Regular Season - 3
  dates:
  - '2024-08-31'
  - '2024-09-01'
- round: Regular Season - 4
  dates:
  - '2024-09-14'
  - '2024-09-15'
- round: Regular Season - 5
  dates:
  - '2024-09-21'
  - '2024-09-22'
- round: Regular Season - 6
  dates:
  - '2024-09-28'
  - '2024-09-29'
  - '2024-09-30'
- round: Regular Season - 7
  dates:
  - '2024-10-05'
  - '2024-10-06'
- round: Regular Season - 8
  dates:
  - '2024-10-19'
  - '2024-10-20'
  - '2024-10-21'
- round: Regular Season - 9
  dates:
  - '2024-10-25'
  - '2024-10-26'
  - '2024-10-27'
- round: Regular Season - 10
  dates:
  - '2024-11-02'
  - '2024-11-03'
  - '2024-11-04'
- round: Regular Season - 11
  dates:
  - '2024-11-09'
  - '2024-11-10'
- round: Regular Season - 12
  dates:
  - '2024-11-23'
  - '2024-11-24'
  - '2024-11-25'
- round: Regular Season - 13
  dates:
  - '2024-11-29'
  - '2024-11-30'
  - '2024-12-01'
- round: Regular Season - 14
  dates:
  - '2024-12-03'
  - '2024-12-04'
- round: Regular Season - 15
  dates:
  - '2024-12-07'
- round: Regular Season - 16
  dates:
  - '2024-12-14'
- round: Regular Season - 17
  dates:
  - '2024-12-21'
- round: Regular Season - 18
  dates:
  - '2024-12-26'
- round: Regular Season - 19
  dates:
  - '2024-12-29'
- round: Regular Season - 20
  dates:
  - '2025-01-04'
- round: Regular Season - 21
  dates:
  - '2025-01-14'
  - '2025-01-15'
- round: Regular Season - 22
  dates:
  - '2025-01-18'
- round: Regular Season - 23
  dates:
  - '2025-01-25'
- round: Regular Season - 24
  dates:
  - '2025-02-01'
- round: Regular Season - 25
  dates:
  - '2025-02-15'
- round: Regular Season - 26
  dates:
  - '2025-02-22'
- round: Regular Season - 27
  dates:
  - '2025-02-25'
  - '2025-02-26'
- round: Regular Season - 28
  dates:
  - '2025-03-08'
- round: Regular Season - 29
  dates:
  - '2025-03-15'
- round: Regular Season - 30
  dates:
  - '2025-04-01'
  - '2025-04-02'
- round: Regular Season - 31
  dates:
  - '2025-04-05'
- round: Regular Season - 32
  dates:
  - '2025-04-12'
- round: Regular Season - 33
  dates:
  - '2025-04-19'
- round: Regular Season - 34
  dates:
  - '2025-04-26'
- round: Regular Season - 35
  dates:
  - '2025-05-03'
- round: Regular Season - 36
  dates:
  - '2025-05-10'
- round: Regular Season - 37
  dates:
  - '2025-05-18'
- round: Regular Season - 38
  dates:
  - '2025-05-25'
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: fixtures/rounds parameters: [] errors:   time: '2019-11-26T00:00:00+00:0...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/fixtures/rounds"
params = {
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
    "current": '<current>',  # The current round only
    "dates": '<dates>',  # Add the dates of each round in the response
    "timezone": '<timezone>',  # A valid timezone from the endpoint `Timezone`
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/fixtures/rounds?season=2019&league=61", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /fixtures` — Fixtures

**Tags:** Fixtures
**Operation ID:** `get-fixtures`

For all requests to fixtures you can add the query parameter `timezone` to your request in order to retrieve the list of matches in the time zone of your choice like *“Europe/London“*

To know the list of available time zones you have to use the endpoint timezone.

**Available fixtures status**

| SHORT  | LONG                            | TYPE       | DESCRIPTION                                                                                                                                           |
| -------| --------------------------------| -----------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| TBD    | Time To Be Defined              | Scheduled  | Scheduled but date and time are not known                                                                                                             |
| NS     | Not Started                     | Scheduled  |                                                                                                                                                       |
| 1H     | First Half, Kick Off            | In Play    | First half in play                                                                                                                                    |
| HT     | Halftime                        | In Play    | Finished in the regular time                                                                                                                          |
| 2H     | Second Half, 2nd Half Started   | In Play    | Second half in play                                                                                                                                   |
| ET     | Extra Time                      | In Play    | Extra time in play                                                                                                                                    |
| BT     | Break Time                      | In Play    | Break during extra time                                                                                                                               |
| P      | Penalty In Progress             | In Play    | Penaly played after extra time                                                                                                                        |
| SUSP   | Match Suspended                 | In Play    | Suspended by referee's decision, may be rescheduled another day                                                                                       |
| INT    | Match Interrupted               | In Play    | Interrupted by referee's decision, should resume in a few minutes                                                                                     |
| FT     | Match Finished                  | Finished   | Finished in the regular time                                                                                                                          |
| AET    | Match Finished                  | Finished   | Finished after extra time without going to the penalty shootout                                                                                       |
| PEN    | Match Finished                  | Finished   | Finished after the penalty shootout                                                                                                                   |
| PST    | Match Postponed                 | Postponed  | Postponed to another day, once the new date and time is known the status will change to Not Started                                                   |
| CANC   | Match Cancelled                 | Cancelled  | Cancelled, match will not be played                                                                                                                   |
| ABD    | Match Abandoned                 | Abandoned  | Abandoned for various reasons (Bad Weather, Safety, Floodlights, Playing Staff Or Referees), Can be rescheduled or not, it depends on the competition |
| AWD    | Technical Loss                  | Not Played | |
| WO     | WalkOver                        | Not Played | Victory by forfeit or absence of competitor                                                                                                           |
| LIVE   | In Progress                     | In Play    | Used in very rare cases. It indicates a fixture in progress but the data indicating the half-time or elapsed time are not available                   |

Fixtures with the status `TBD` may indicate an incorrect fixture date or time because the fixture date or time is not yet known or final. Fixtures with this status are checked and updated daily. The same applies to fixtures with the status `PST`, `CANC`.

The fixtures ids are unique and specific to each fixture. In no case an `ID` will change.

Not all competitions have livescore available and only have `final result`. In this case, the status remains in `NS` and will be updated in the minutes/hours following the match (this can take up to 48 hours, depending on the competition).

> Although the data is updated every 15 seconds, depending on the competition there may be a delay between reality and the availability of data in the API.

**Update Frequency** : This endpoint is updated every 15 seconds.

**Recommended Calls** : 1 call per minute for the leagues, teams, fixtures who have at least one fixture in progress otherwise 1 call per day.

> Here are several examples of what can be achieved

![demo-fixtures](https://www.api-football.com/public/img/demo/demo-fixtures.jpg)

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `id` | query | integer enum: id | no | The id of the fixture |
| `ids` | query | string enum: id-id-id pattern: Maximum of 20 fixtures ids | no | One or more fixture ids |
| `live` | query | string enum: all \| id-id | no | All or several leagues ids |
| `date` | query | string pattern: YYYY-MM-DD | no | A valid date |
| `league` | query | integer | no | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | no | The season of the league |
| `team` | query | integer | no | The id of the team |
| `last` | query | integer maxLength: 2 | no | For the X last fixtures |
| `next` | query | integer maxLength: 2 | no | For the X next fixtures |
| `from` | query | string pattern: YYYY-MM-DD | no | A valid date |
| `to` | query | string pattern: YYYY-MM-DD | no | A valid date |
| `round` | query | string | no | The round of the fixture |
| `status` | query | string enum: NS \| NS-PST-FT | no | One or more fixture status short |
| `venue` | query | integer | no | The venue id of the fixture |
| `timezone` | query | string | no | A valid timezone from the endpoint `Timezone` |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: fixtures
parameters:
  live: all
errors: []
results: 4
paging:
  current: 1
  total: 1
response:
- fixture:
    id: 239625
    referee: null
    timezone: UTC
    date: '2020-02-06T14:00:00+00:00'
    timestamp: 1580997600
    periods:
      first: 1580997600
      second: null
    venue:
      id: 1887
      name: Stade Municipal
      city: Oued Zem
    status:
      long: Halftime
      short: HT
      elapsed: 45
      extra: null
  league:
    id: 200
    name: Botola Pro
    country: Morocco
    logo: https://media.api-sports.io/football/leagues/115.png
    flag: https://media.api-sports.io/flags/ma.svg
    season: 2019
    round: Regular Season - 14
  teams:
    home:
      id: 967
      name: Rapide Oued ZEM
      logo: https://media.api-sports.io/football/teams/967.png
      winner: false
    away:
      id: 968
      name: Wydad AC
      logo: https://media.api-sports.io/football/teams/968.png
      winner: true
  goals:
    home: 0
    away: 1
  score:
    halftime:
      home: 0
      away: 1
    fulltime:
      home: null
      away: null
    extratime:
      home: null
      away: null
    penalty:
      home: null
      away: null
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: fixtures parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   bu...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/fixtures"
params = {
    "id": '<id>',  # The id of the fixture
    "ids": '<ids>',  # One or more fixture ids
    "live": '<live>',  # All or several leagues ids
    "date": '<date>',  # A valid date
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
    "team": '<team>',  # The id of the team
    "last": '<last>',  # For the X last fixtures
    "next": '<next>',  # For the X next fixtures
    "from": '<from>',  # A valid date
    "to": '<to>',  # A valid date
    "round": '<round>',  # The round of the fixture
    "status": '<status>',  # One or more fixture status short
    "venue": '<venue>',  # The venue id of the fixture
    "timezone": '<timezone>',  # A valid timezone from the endpoint `Timezone`
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/fixtures?live=all", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /fixtures/headtohead` — Head To Head

**Tags:** Fixtures
**Operation ID:** `get-fixtures-headtohead`

Get heads to heads between two teams.

**Update Frequency** : This endpoint is updated every 15 seconds.

**Recommended Calls** : 1 call per minute for the leagues, teams, fixtures who have at least one fixture in progress otherwise 1 call per day.

> Here is an example of what can be achieved

![demo-h2h](https://www.api-football.com/public/img/demo/demo-h2h.png)

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `h2h` | query | string pattern: ID-ID | yes | The ids of the teams |
| `date` | query | string pattern: YYYY-MM-DD | no |  |
| `league` | query | integer | no | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | no | The season of the league |
| `last` | query | integer | no | For the X last fixtures |
| `next` | query | integer | no | For the X next fixtures |
| `from` | query | string pattern: YYYY-MM-DD | no |  |
| `to` | query | string pattern: YYYY-MM-DD | no |  |
| `status` | query | string enum: NS \| NS-PST-FT | no | One or more fixture status short |
| `venue` | query | integer | no | The venue id of the fixture |
| `timezone` | query | string | no | A valid timezone from the endpoint `Timezone` |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: fixtures/headtohead
parameters:
  h2h: 33-34
  last: '1'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- fixture:
    id: 157201
    referee: Kevin Friend, England
    timezone: UTC
    date: '2019-12-26T17:30:00+00:00'
    timestamp: 1577381400
    periods:
      first: 1577381400
      second: 1577385000
    venue:
      id: 556
      name: Old Trafford
      city: Manchester
    status:
      long: Match Finished
      short: FT
      elapsed: 90
      extra: null
  league:
    id: 39
    name: Premier League
    country: England
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: https://media.api-sports.io/flags/gb.svg
    season: 2019
    round: Regular Season - 19
  teams:
    home:
      id: 33
      name: Manchester United
      logo: https://media.api-sports.io/football/teams/33.png
      winner: true
    away:
      id: 34
      name: Newcastle
      logo: https://media.api-sports.io/football/teams/34.png
      winner: false
  goals:
    home: 4
    away: 1
  score:
    halftime:
      home: 3
      away: 1
    fulltime:
      home: 4
      away: 1
    extratime:
      home: null
      away: null
    penalty:
      home: null
      away: null
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: fixtures/headtohead parameters: [] errors:   time: '2019-11-26T00:00:00+...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/fixtures/headtohead"
params = {
    "h2h": '<h2h>',  # The ids of the teams
    "date": '<date>',  # 
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
    "last": '<last>',  # For the X last fixtures
    "next": '<next>',  # For the X next fixtures
    "from": '<from>',  # 
    "to": '<to>',  # 
    "status": '<status>',  # One or more fixture status short
    "venue": '<venue>',  # The venue id of the fixture
    "timezone": '<timezone>',  # A valid timezone from the endpoint `Timezone`
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/fixtures/headtohead?h2h=33-34", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /fixtures/statistics` — Statistics

**Tags:** Fixtures
**Operation ID:** `get-fixtures-statistics`

Get the statistics for one fixture.

**Available statistics**

* Shots on Goal
* Shots off Goal
* Shots insidebox
* Shots outsidebox
* Total Shots
* Blocked Shots
* Fouls
* Corner Kicks
* Offsides
* Ball Possession
* Yellow Cards
* Red Cards
* Goalkeeper Saves
* Total passes
* Passes accurate
* Passes %

**Update Frequency** : This endpoint is updated every minute.

**Recommended Calls** : 1 call every minute for the teams or fixtures who have at least one fixture in progress otherwise 1 call per day.

> Here is an example of what can be achieved

![demo-statistics](https://www.api-football.com/public/img/demo/demo-statistics.png)

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `fixture` | query | integer | yes | The id of the fixture |
| `team` | query | integer | no | The id of the team |
| `type` | query | string | no | The type of statistics |
| `half` | query | boolean enum: true \| false | no | Add the halftime statistics in the response `Data start from 2024 season for half parameter` |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`Default`):
```json
get: fixtures/statistics
parameters:
  team: '463'
  fixture: '215662'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- team:
    id: 463
    name: Aldosivi
    logo: https://media.api-sports.io/football/teams/463.png
  statistics:
  - type: Shots on Goal
    value: 3
  - type: Shots off Goal
    value: 2
  - type: Total Shots
    value: 9
  - type: Blocked Shots
    value: 4
  - type: Shots insidebox
    value: 4
  - type: Shots outsidebox
    value: 5
  - type: Fouls
    value: 22
  - type: Corner Kicks
    value: 3
  - type: Offsides
    value: 1
  - type: Ball Possession
    value: 32%
  - type: Yellow Cards
    value: 5
  - type: Red Cards
    value: 1
  - type: Goalkeeper Saves
    value: null
  - type: Total passes
    value: 242
  - type: Passes accurate
    value: 121
  - type: Passes %
    value: null
```

**Example** (`With half parameter`):
```json
get: fixtures/statistics
parameters:
  fixture: '1299002'
  half: 'true'
errors: []
results: 2
paging:
  current: 1
  total: 1
response:
- team:
    id: 571
    name: Red Bull Salzburg
    logo: https://media.api-sports.io/football/teams/571.png
  statistics:
  - type: Shots on Goal
    value: 7
  - type: Shots off Goal
    value: 4
  - type: Total Shots
    value: 15
  - type: Blocked Shots
    value: 4
  - type: Shots insidebox
    value: 11
  - type: Shots outsidebox
    value: 4
  - type: Fouls
    value: 17
  - type: Corner Kicks
    value: 4
  - type: Offsides
    value: 3
  - type: Ball Possession
    value: 52%
  - type: Yellow Cards
    value: 3
  - type: Red Cards
    value: null
  - type: Goalkeeper Saves
    value: 2
  - type: Total passes
    value: 453
  - type: Passes accurate
    value: 372
  - type: Passes %
    value: 82%
  - type: expected_goals
    value: '1.53'
  - type: goals_prevented
    value: 2
  statistics_1h:
  - type: Shots on Goal
    value: 4
  - type: Shots off Goal
    value: 3
  - type: Total Shots
    value: 9
  - type: Blocked Shots
    value: 2
  - type: Shots insidebox
    value: 7
  - type: Shots outsidebox
    value: 2
  - type: Fouls
    value: null
  - type: Corner Kicks
    value: 2
  - type: Offsides
    value: 2
  - type: Ball Possession
    value: 54%
  - type: Yellow Cards
    value: 1
  - type: Red Cards
    value: null
  - type: Goalkeeper Saves
    value: null
  - type: Total passes
    value: 254
  - type: Passes accurate
    value: 210
  - type: Passes %
    value: 83%
  - type: expected_goals
    value: '1.04'
  - type: goals_prevented
    value: null
  statistics_2h:
  - type: Shots on Goal
    value: 3
  - type: Shots off Goal
    value: 1
  - type: Total Shots
    value: 6
  - type: Blocked Shots
    value: 2
  - type: Shots insidebox
    value: 4
  - type: Shots outsidebox
    value: 2
  - type: Fouls
    value: null
  - type: Corner Kicks
    value: 2
  - type: Offsides
    value: 1
  - type: Ball Possession
    value: 49%
  - type: Yellow Cards
    value: 2
  - type: Red Cards
    value: null
  - type: Goalkeeper Saves
    value: 2
  - type: Total passes
    value: 199
  - type: Passes accurate
    value: 162
  - type: Passes %
    value: 81%
  - type: expected_goals
    value: '0.49'
  - type: goals_prevented
    value: null
- team:
    id: 106
    name: Stade Brestois 29
    logo: https://media.api-sports.io/football/teams/106.png
  statistics:
  - type: Shots on Goal
    value: 6
  - type: Shots off Goal
    value: 5
  - type: Total Shots
    value: 13
  - type: Blocked Shots
    value: 2
  - type: Shots insidebox
    value: 9
  - type: Shots outsidebox
    value: 4
  - type: Fouls
    value: 11
  - type: Corner Kicks
    value: null
  - type: Offsides
    value: null
  - type: Ball Possession
    value: 48%
  - type: Yellow Cards
    value: 2
  - type: Red Cards
    value: null
  - type: Goalkeeper Saves
    value: 7
  - type: Total passes
    value: 426
  - type: Passes accurate
    value: 339
  - type: Passes %
    value: 80%
  - type: expected_goals
    value: '1.76'
  - type: goals_prevented
    value: 2
  statistics_1h:
  - type: Shots on Goal
    value: 1
  - type: Shots off Goal
    value: 2
  - type: Total Shots
    value: 4
  - type: Blocked Shots
    value: 1
  - type: Shots insidebox
    value: 4
  - type: Shots outsidebox
    value: null
  - type: Fouls
    value: null
  - type: Corner Kicks
    value: null
  - type: Offsides
    value: null
  - type: Ball Possession
    value: 46%
  - type: Yellow Cards
    value: 2
  - type: Red Cards
    value: null
  - type: Goalkeeper Saves
    value: 4
  - type: Total passes
    value: 218
  - type: Passes accurate
    value: 170
  - type: Passes %
    value: 78%
  - type: expected_goals
    value: '0.67'
  - type: goals_prevented
    value: null
  statistics_2h:
  - type: Shots on Goal
    value: 5
  - type: Shots off Goal
    value: 3
  - type: Total Shots
    value: 9
  - type: Blocked Shots
    value: 1
  - type: Shots insidebox
    value: 5
  - type: Shots outsidebox
    value: 4
  - type: Fouls
    value: null
  - type: Corner Kicks
    value: null
  - type: Offsides
    value: null
  - type: Ball Possession
    value: 51%
  - type: Yellow Cards
    value: null
  - type: Red Cards
    value: null
  - type: Goalkeeper Saves
    value: 3
  - type: Total passes
    value: 208
  - type: Passes accurate
    value: 169
  - type: Passes %
    value: 81%
  - type: expected_goals
    value: '1.09'
  - type: goals_prevented
    value: null
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: fixtures/statistics parameters: [] errors:   time: '2019-11-26T00:00:00+...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/fixtures/statistics"
params = {
    "fixture": '<fixture>',  # The id of the fixture
    "team": '<team>',  # The id of the team
    "type": '<type>',  # The type of statistics
    "half": '<half>',  # Add the halftime statistics in the response `Data start from 2024 season for hal
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/fixtures/statistics?fixture=215662&team=463", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /fixtures/events` — Events

**Tags:** Fixtures
**Operation ID:** `get-fixtures-events`

Get the events from a fixture.

**Available events**

| TYPE        |                 |                      |          |                 |
| ----------- | -------------   | ---------            |--------  |--------         |
| Goal        |   Normal Goal   |   Own Goal           | Penalty  | Missed Penalty  |
| Card        |   Yellow Card   |   Red card           |          |                 |
| Subst       | Substitution [1, 2, 3...]  |           |          |                 |
| Var         | Goal cancelled  |   Penalty confirmed  |          |                 |

* *VAR events are available from the 2020-2021 season.*

**Update Frequency** : This endpoint is updated every 15 seconds.

**Recommended Calls** : 1 call per minute for the fixtures in progress otherwise 1 call per day.

You can also retrieve all the events of the fixtures in progress with to the endpoint `fixtures?live=all`

> Here is an example of what can be achieved

![demo-events](https://www.api-football.com/public/img/demo/demo-events.png)

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `fixture` | query | integer | yes | The id of the fixture |
| `team` | query | integer | no | The id of the team |
| `player` | query | integer | no | The id of the player |
| `type` | query | string | no | The type |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: fixtures/events
parameters:
  fixture: '215662'
errors: []
results: 18
paging:
  current: 1
  total: 1
response:
- time:
    elapsed: 25
    extra: null
  team:
    id: 463
    name: Aldosivi
    logo: https://media.api-sports.io/football/teams/463.png
  player:
    id: 6126
    name: F. Andrada
  assist:
    id: null
    name: null
  type: Goal
  detail: Normal Goal
  comments: null
- time:
    elapsed: 33
    extra: null
  team:
    id: 442
    name: Defensa Y Justicia
    logo: https://media.api-sports.io/football/teams/442.png
  player:
    id: 5936
    name: Julio González
  assist:
    id: null
    name: null
  type: Card
  detail: Yellow Card
  comments: null
- time:
    elapsed: 33
    extra: null
  team:
    id: 463
    name: Aldosivi
    logo: https://media.api-sports.io/football/teams/463.png
  player:
    id: 6126
    name: Federico Andrada
  assist:
    id: null
    name: null
  type: Card
  detail: Yellow Card
  comments: null
- time:
    elapsed: 36
    extra: null
  team:
    id: 442
    name: Defensa Y Justicia
    logo: https://media.api-sports.io/football/teams/442.png
  player:
    id: 5931
    name: Diego Rodríguez
  assist:
    id: null
    name: null
  type: Card
  detail: Yellow Card
  comments: null
- time:
    elapsed: 39
    extra: null
  team:
    id: 442
    name: Defensa Y Justicia
    logo: https://media.api-sports.io/football/teams/442.png
  player:
    id: 5954
    name: Fernando Márquez
  assist:
    id: null
    name: null
  type: Card
  detail: Yellow Card
  comments: null
- time:
    elapsed: 44
    extra: null
  team:
    id: 463
    name: Aldosivi
    logo: https://media.api-sports.io/football/teams/463.png
  player:
    id: 6262
    name: Emanuel Iñiguez
  assist:
    id: null
    name: null
  type: Card
  detail: Yellow Card
  comments: null
- time:
    elapsed: 46
    extra: null
  team:
    id: 442
    name: Defensa Y Justicia
    logo: https://media.api-sports.io/football/teams/442.png
  player:
    id: 35695
    name: D. Rodríguez
  assist:
    id: 5947
    name: B. Merlini
  type: subst
  detail: Substitution 1
  comments: null
- time:
    elapsed: 62
    extra: null
  team:
    id: 463
    name: Aldosivi
    logo: https://media.api-sports.io/football/teams/463.png
  player:
    id: 6093
    name: Gonzalo Verón
  assist:
    id: null
    name: null
  type: Card
  detail: Yellow Card
  comments: null
- time:
    elapsed: 73
    extra: null
  team:
    id: 442
    name: Defensa Y Justicia
    logo: https://media.api-sports.io/football/teams/442.png
  player:
    id: 5942
    name: A. Castro
  assist:
    id: 6059
    name: G. Mainero
  type: subst
  detail: Substitution 2
  comments: null
- time:
    elapsed: 74
    extra: null
  team:
    id: 463
    name: Aldosivi
    logo: https://media.api-sports.io/football/teams/463.png
  player:
    id: 6561
    name: N. Solís
  assist:
    id: 35845
    name: H. Burbano
  type: subst
  detail: Substitution 1
  comments: null
- time:
    elapsed: 75
    extra: null
  team:
    id: 463
    name: Aldosivi
    logo: https://media.api-sports.io/football/teams/463.png
  player:
    id: 6093
    name: G. Verón
  assist:
    id: 6396
    name: N. Bazzana
  type: subst
  detail: Substitution 2
  comments: null
- time:
    elapsed: 79
    extra: null
  team:
    id: 463
    name: Aldosivi
    logo: https://media.api-sports.io/football/teams/463.png
  player:
    id: 6474
    name: G. Gil
  assist:
    id: 6550
    name: F. Grahl
  type: subst
  detail: Substitution 3
  comments: null
- time:
    elapsed: 79
    extra: null
  team:
    id: 442
    name: Defensa Y Justicia
    logo: https://media.api-sports.io/football/teams/442.png
  player:
    id: 5936
    name: J. González
  assist:
    id: 70767
    name: B. Ojeda
  type: subst
  detail: Substitution 3
  comments: null
- time:
    elapsed: 84
    extra: null
  team:
    id: 442
    name: Defensa Y Justicia
    logo: https://media.api-sports.io/football/teams/442.png
  player:
    id: 6540
    name: Juan Rodriguez
  assist:
    id: null
    name: null
  type: Card
  detail: Yellow Card
  comments: null
- time:
    elapsed: 85
    extra: null
  team:
    id: 463
    name: Aldosivi
    logo: https://media.api-sports.io/football/teams/463.png
  player:
    id: 35845
    name: Hernán Burbano
  assist:
    id: null
    name: null
  type: Card
  detail: Yellow Card
  comments: null
- time:
    elapsed: 90
    extra: null
  team:
    id: 442
    name: Defensa Y Justicia
    logo: https://media.api-sports.io/football/teams/442.png
  player:
    id: 5912
    name: Neri Cardozo
  assist:
    id: null
    name: null
  type: Card
  detail: Yellow Card
  comments: null
- time:
    elapsed: 90
    extra: null
  team:
    id: 463
    name: Aldosivi
    logo: https://media.api-sports.io/football/teams/463.png
  player:
    id: 35845
    name: Hernán Burbano
  assist:
    id: null
    name: null
  type: Card
  detail: Red Card
  comments: null
- time:
    elapsed: 90
    extra: null
  team:
    id: 463
    name: Aldosivi
    logo: https://media.api-sports.io/football/teams/463.png
  player:
    id: 35845
    name: Hernán Burbano
  assist:
    id: null
    name: null
  type: Card
  detail: Yellow Card
  comments: null
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: fixtures/events parameters: [] errors:   time: '2019-11-26T00:00:00+00:0...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/fixtures/events"
params = {
    "fixture": '<fixture>',  # The id of the fixture
    "team": '<team>',  # The id of the team
    "player": '<player>',  # The id of the player
    "type": '<type>',  # The type
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/fixtures/events?fixture=215662", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /fixtures/lineups` — Lineups

**Tags:** Fixtures
**Operation ID:** `get-fixtures-lineups`

Get the lineups for a fixture.

Lineups are available between 20 and 40 minutes before the fixture when the competition covers this feature. You can check this with the endpoint `leagues` and the `coverage` field.

> It's possible that for some competitions the lineups are not available before the fixture, in this case, they are updated and available after the match with a variable delay depending on the competition.       

**Available datas**

* Formation
* Coach
* Start XI
* Substitutes

**Players' positions on the grid `*`**

**X** = row and **Y** = column (X:Y)

Line 1 **X** being the one of the goal and then for each line this number is incremented. The column **Y** will go from left to right, and incremented for each player of the line.

`* As a new feature, some irregularities may occur, do not hesitate to report them on our public Roadmap`

**Update Frequency** : This endpoint is updated every 15 minutes.

**Recommended Calls** : 1 call every 15 minutes for the fixtures in progress otherwise 1 call per day.

> Here are several examples of what can be done

![demo-lineups](https://www.api-football.com/public/img/demo/demo-lineups-1.jpg)

![demo-lineups](https://www.api-football.com/public/img/demo/demo-lineups.png)

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `fixture` | query | integer | yes | The id of the fixture |
| `team` | query | integer | no | The id of the team |
| `player` | query | integer | no | The id of the player |
| `type` | query | string | no | The type |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: fixtures/lineups
parameters:
  fixture: '592872'
errors: []
results: 2
paging:
  current: 1
  total: 1
response:
- team:
    id: 50
    name: Manchester City
    logo: https://media.api-sports.io/football/teams/50.png
    colors:
      player:
        primary: 5badff
        number: ffffff
        border: 99ff99
      goalkeeper:
        primary: 99ff99
        number: '000000'
        border: 99ff99
  formation: 4-3-3
  startXI:
  - player:
      id: 617
      name: Ederson
      number: 31
      pos: G
      grid: '1:1'
  - player:
      id: 627
      name: Kyle Walker
      number: 2
      pos: D
      grid: '2:4'
  - player:
      id: 626
      name: John Stones
      number: 5
      pos: D
      grid: '2:3'
  - player:
      id: 567
      name: Rúben Dias
      number: 3
      pos: D
      grid: '2:2'
  - player:
      id: 641
      name: Oleksandr Zinchenko
      number: 11
      pos: D
      grid: '2:1'
  - player:
      id: 629
      name: Kevin De Bruyne
      number: 17
      pos: M
      grid: '3:3'
  - player:
      id: 640
      name: Fernandinho
      number: 25
      pos: M
      grid: '3:2'
  - player:
      id: 631
      name: Phil Foden
      number: 47
      pos: M
      grid: '3:1'
  - player:
      id: 635
      name: Riyad Mahrez
      number: 26
      pos: F
      grid: '4:3'
  - player:
      id: 643
      name: Gabriel Jesus
      number: 9
      pos: F
      grid: '4:2'
  - player:
      id: 645
      name: Raheem Sterling
      number: 7
      pos: F
      grid: '4:1'
  substitutes:
  - player:
      id: 50828
      name: Zack Steffen
      number: 13
      pos: G
      grid: null
  - player:
      id: 623
      name: Benjamin Mendy
      number: 22
      pos: D
      grid: null
  - player:
      id: 18861
      name: Nathan Aké
      number: 6
      pos: D
      grid: null
  - player:
      id: 622
      name: Aymeric Laporte
      number: 14
      pos: D
      grid: null
  - player:
      id: 633
      name: İlkay Gündoğan
      number: 8
      pos: M
      grid: null
  - player:
      id: 44
      name: Rodri
      number: 16
      pos: M
      grid: null
  - player:
      id: 931
      name: Ferrán Torres
      number: 21
      pos: F
      grid: null
  - player:
      id: 636
      name: Bernardo Silva
      number: 20
      pos: M
      grid: null
  - player:
      id: 642
      name: Sergio Agüero
      number: 10
      pos: F
      grid: null
  coach:
    id: 4
    name: Guardiola
    photo: https://media.api-sports.io/football/coachs/4.png
- team:
    id: 45
    name: Everton
    logo: https://media.api-sports.io/football/teams/45.png
    colors:
      player:
        primary: '070707'
        number: ffffff
        border: 66ff00
      goalkeeper:
        primary: 66ff00
        number: '000000'
        border: 66ff00
  formation: 4-3-1-2
  startXI:
  - player:
      id: 2932
      name: Jordan Pickford
      number: 1
      pos: G
      grid: '1:1'
  - player:
      id: 19150
      name: Mason Holgate
      number: 4
      pos: D
      grid: '2:4'
  - player:
      id: 2934
      name: Michael Keane
      number: 5
      pos: D
      grid: '2:3'
  - player:
      id: 19073
      name: Ben Godfrey
      number: 22
      pos: D
      grid: '2:2'
  - player:
      id: 2724
      name: Lucas Digne
      number: 12
      pos: D
      grid: '2:1'
  - player:
      id: 18805
      name: Abdoulaye Doucouré
      number: 16
      pos: M
      grid: '3:3'
  - player:
      id: 326
      name: Allan
      number: 6
      pos: M
      grid: '3:2'
  - player:
      id: 18762
      name: Tom Davies
      number: 26
      pos: M
      grid: '3:1'
  - player:
      id: 2795
      name: Gylfi Sigurðsson
      number: 10
      pos: M
      grid: '4:1'
  - player:
      id: 18766
      name: Dominic Calvert-Lewin
      number: 9
      pos: F
      grid: '5:2'
  - player:
      id: 2413
      name: Richarlison
      number: 7
      pos: F
      grid: '5:1'
  substitutes:
  - player:
      id: 18755
      name: João Virgínia
      number: 31
      pos: G
      grid: null
  - player:
      id: 766
      name: Robin Olsen
      number: 33
      pos: G
      grid: null
  - player:
      id: 156490
      name: Niels Nkounkou
      number: 18
      pos: D
      grid: null
  - player:
      id: 18758
      name: Séamus Coleman
      number: 23
      pos: D
      grid: null
  - player:
      id: 138849
      name: Kyle John
      number: 48
      pos: D
      grid: null
  - player:
      id: 18765
      name: André Gomes
      number: 21
      pos: M
      grid: null
  - player:
      id: 1455
      name: Alex Iwobi
      number: 17
      pos: F
      grid: null
  - player:
      id: 18761
      name: Bernard
      number: 20
      pos: F
      grid: null
  coach:
    id: 2407
    name: C. Ancelotti
    photo: https://media.api-sports.io/football/coachs/2407.png
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: fixtures/lineups parameters: [] errors:   time: '2019-11-26T00:00:00+00:...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/fixtures/lineups"
params = {
    "fixture": '<fixture>',  # The id of the fixture
    "team": '<team>',  # The id of the team
    "player": '<player>',  # The id of the player
    "type": '<type>',  # The type
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/fixtures/lineups?fixture=592872", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /fixtures/players` — Players statistics

**Tags:** Fixtures
**Operation ID:** `get-fixtures-players`

Get the players statistics from one fixture.

**Update Frequency** : This endpoint is updated every minute.

**Recommended Calls** : 1 call every minute for the fixtures in progress otherwise 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `fixture` | query | integer | yes | The id of the fixture |
| `team` | query | integer | no | The id of the team |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: fixtures/players
parameters:
  fixture: '169080'
errors: []
results: 2
paging:
  current: 1
  total: 1
response:
- team:
    id: 2284
    name: Monarcas
    logo: https://media.api-sports.io/football/teams/2284.png
    update: '2020-01-13T16:12:12+00:00'
  players:
  - player:
      id: 35931
      name: Sebastián Sosa
      photo: https://media.api-sports.io/football/players/35931.png
    statistics:
    - games:
        minutes: 90
        number: 13
        position: G
        rating: '6.3'
        captain: false
        substitute: false
      offsides: null
      shots:
        total: 0
        'on': 0
      goals:
        total: null
        conceded: 1
        assists: null
        saves: 0
      passes:
        total: 17
        key: 0
        accuracy: 68%
      tackles:
        total: null
        blocks: 0
        interceptions: 0
      duels:
        total: null
        won: null
      dribbles:
        attempts: 0
        success: 0
        past: null
      fouls:
        drawn: 0
        committed: 0
      cards:
        yellow: 0
        red: 0
      penalty:
        won: null
        commited: null
        scored: 0
        missed: 0
        saved: 0
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: fixtures/players parameters: [] errors:   time: '2019-11-26T00:00:00+00:...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/fixtures/players"
params = {
    "fixture": '<fixture>',  # The id of the fixture
    "team": '<team>',  # The id of the team
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/fixtures/players?fixture=169080", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /injuries` — Injuries

**Tags:** Injuries
**Operation ID:** `get-injuries`

Get the list of players not participating in the fixtures for various reasons such as `suspended`, `injured` for example.

Being a new endpoint, the data is only available from April 2021.

**There are two types:**

* `Missing Fixture` : The player will not play the fixture.
* `Questionable` : The information is not yet 100% sure, the player may eventually play the fixture.


> All the parameters of this endpoint can be used together.

**This endpoint requires at least one parameter.**

**Update Frequency** : This endpoint is updated every 4 hours.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `league` | query | integer | no | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | no | The season of the league, **required** with `league`, `team` and `player` parameters |
| `fixture` | query | integer | no | The id of the fixture |
| `team` | query | integer | no | The id of the team |
| `player` | query | integer | no | The id of the player |
| `date` | query | string pattern: YYYY-MM-DD | no | A valid date |
| `ids` | query | string enum: id-id-id pattern: Maximum of 20 fixtures ids | no | One or more fixture ids |
| `timezone` | query | string | no | A valid timezone from the endpoint `Timezone` |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: injuries
parameters:
  fixture: '686314'
errors: []
results: 13
paging:
  current: 1
  total: 1
response:
- player:
    id: 865
    name: D. Costa
    photo: https://media.api-sports.io/football/players/865.png
    type: Missing Fixture
    reason: Broken ankle
  team:
    id: 157
    name: Bayern Munich
    logo: https://media.api-sports.io/football/teams/157.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 510
    name: S. Gnabry
    photo: https://media.api-sports.io/football/players/510.png
    type: Missing Fixture
    reason: Illness
  team:
    id: 157
    name: Bayern Munich
    logo: https://media.api-sports.io/football/teams/157.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 496
    name: R. Hoffmann
    photo: https://media.api-sports.io/football/players/496.png
    type: Missing Fixture
    reason: Knee Injury
  team:
    id: 157
    name: Bayern Munich
    logo: https://media.api-sports.io/football/teams/157.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 521
    name: R. Lewandowski
    photo: https://media.api-sports.io/football/players/521.png
    type: Missing Fixture
    reason: Knee Injury
  team:
    id: 157
    name: Bayern Munich
    logo: https://media.api-sports.io/football/teams/157.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 514
    name: J. Martinez
    photo: https://media.api-sports.io/football/players/514.png
    type: Missing Fixture
    reason: Knock
  team:
    id: 157
    name: Bayern Munich
    logo: https://media.api-sports.io/football/teams/157.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 162037
    name: M. Tillman
    photo: https://media.api-sports.io/football/players/162037.png
    type: Missing Fixture
    reason: Knee Injury
  team:
    id: 157
    name: Bayern Munich
    logo: https://media.api-sports.io/football/teams/157.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 519
    name: C. Tolisso
    photo: https://media.api-sports.io/football/players/519.png
    type: Missing Fixture
    reason: Tendon Injury
  team:
    id: 157
    name: Bayern Munich
    logo: https://media.api-sports.io/football/teams/157.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 258
    name: J. Bernat
    photo: https://media.api-sports.io/football/players/258.png
    type: Missing Fixture
    reason: Knee Injury
  team:
    id: 85
    name: Paris Saint Germain
    logo: https://media.api-sports.io/football/teams/85.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 769
    name: A. Florenzi
    photo: https://media.api-sports.io/football/players/769.png
    type: Missing Fixture
    reason: Illness
  team:
    id: 85
    name: Paris Saint Germain
    logo: https://media.api-sports.io/football/teams/85.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 216
    name: M. Icardi
    photo: https://media.api-sports.io/football/players/216.png
    type: Missing Fixture
    reason: Muscle Injury
  team:
    id: 85
    name: Paris Saint Germain
    logo: https://media.api-sports.io/football/teams/85.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 263
    name: L. Kurzawa
    photo: https://media.api-sports.io/football/players/263.png
    type: Missing Fixture
    reason: Calf Injury
  team:
    id: 85
    name: Paris Saint Germain
    logo: https://media.api-sports.io/football/teams/85.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 271
    name: L. Paredes
    photo: https://media.api-sports.io/football/players/271.png
    type: Missing Fixture
    reason: Suspended
  team:
    id: 85
    name: Paris Saint Germain
    logo: https://media.api-sports.io/football/teams/85.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
- player:
    id: 273
    name: M. Verratti
    photo: https://media.api-sports.io/football/players/273.png
    type: Missing Fixture
    reason: Illness
  team:
    id: 85
    name: Paris Saint Germain
    logo: https://media.api-sports.io/football/teams/85.png
  fixture:
    id: 686314
    timezone: UTC
    date: '2021-04-07T19:00:00+00:00'
    timestamp: 1617822000
  league:
    id: 2
    season: 2020
    name: UEFA Champions League
    country: World
    logo: https://media.api-sports.io/football/leagues/2.png
    flag: null
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: injuries parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   bu...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/injuries"
params = {
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league, **required** with `league`, `team` and `player` parame
    "fixture": '<fixture>',  # The id of the fixture
    "team": '<team>',  # The id of the team
    "player": '<player>',  # The id of the player
    "date": '<date>',  # A valid date
    "ids": '<ids>',  # One or more fixture ids
    "timezone": '<timezone>',  # A valid timezone from the endpoint `Timezone`
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/injuries?fixture=686314", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /predictions` — Predictions

**Tags:** Predictions
**Operation ID:** `get-predictions`

Get predictions about a fixture.

The predictions are made using several algorithms including the poisson distribution, comparison of team statistics, last matches, players etc…

Bookmakers odds are not used to make these predictions

Also provides some comparative statistics between teams

**Available Predictions**
* Match winner : Id of the team that can potentially win the fixture
* Win or Draw : If `True` indicates that the designated team can win or draw
* Under / Over : -1.5 / -2.5 / -3.5 / -4.5 / +1.5 / +2.5 / +3.5 / +4.5 `*`
* Goals Home : -1.5 / -2.5 / -3.5 / -4.5 `*`
* Goals Away -1.5 / -2.5 / -3.5 / -4.5 `*`
* Advice *(Ex : Deportivo Santani or draws and -3.5 goals)*

`*` **-1.5** means that there will be a maximum of **1.5** goals in the fixture, i.e : **1** goal

**Update Frequency** : This endpoint is updated every hour.

**Recommended Calls** : 1 call per hour for the fixtures in progress otherwise 1 call per day.

>Here is an example of what can be achieved

![demo-prediction](https://www.api-football.com/public/img/demo/demo-prediction.png)

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `fixture` | query | integer | yes | The id of the fixture |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: predictions
parameters:
  fixture: '198772'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- predictions:
    winner:
      id: 1189
      name: Deportivo Santani
      comment: Win or draw
    win_or_draw: true
    under_over: '-3.5'
    goals:
      home: '-2.5'
      away: '-1.5'
    advice: 'Combo Double chance : Deportivo Santani or draw and -3.5 goals'
    percent:
      home: 45%
      draw: 45%
      away: 10%
  league:
    id: 252
    name: Primera Division - Clausura
    country: Paraguay
    logo: https://media.api-sports.io/football/leagues/252.png
    flag: https://media.api-sports.io/flags/py.svg
    season: 2019
  teams:
    home:
      id: 1189
      name: Deportivo Santani
      logo: https://media.api-sports.io/football/teams/1189.png
      last_5:
        form: 60%
        att: 60%
        def: 0%
        goals:
          for:
            total: 3
            average: 0.6
          against:
            total: 5
            average: 1
      league:
        form: LDLDLDLWLWWLW
        fixtures:
          played:
            home: 6
            away: 7
            total: 13
          wins:
            home: 2
            away: 2
            total: 4
          draws:
            home: 3
            away: 0
            total: 3
          loses:
            home: 1
            away: 5
            total: 6
        goals:
          for:
            total:
              home: 7
              away: 4
              total: 11
            average:
              home: '1.2'
              away: '0.6'
              total: '0.8'
          against:
            total:
              home: 6
              away: 14
              total: 20
            average:
              home: '1.0'
              away: '2.0'
              total: '1.5'
        biggest:
          streak:
            wins: 2
            draws: 1
            loses: 1
          wins:
            home: 3-1
            away: 0-1
          loses:
            home: 0-2
            away: 4-0
          goals:
            for:
              home: 3
              away: 1
            against:
              home: 2
              away: 4
        clean_sheet:
          home: 1
          away: 2
          total: 3
        failed_to_score:
          home: 1
          away: 3
          total: 4
    away:
      id: 1180
      name: Deportivo Capiata
      logo: https://media.api-sports.io/football/teams/1180.png
      last_5:
        form: 40%
        att: 80%
        def: 0%
        goals:
          for:
            total: 4
            average: 0.8
          against:
            total: 8
            average: 1.6
      league:
        form: WLWLDLDLLLLWW
        fixtures:
          played:
            home: 7
            away: 6
            total: 13
          wins:
            home: 3
            away: 1
            total: 4
          draws:
            home: 0
            away: 2
            total: 2
          loses:
            home: 4
            away: 3
            total: 7
        goals:
          for:
            total:
              home: 8
              away: 3
              total: 11
            average:
              home: '1.1'
              away: '0.5'
              total: '0.8'
          against:
            total:
              home: 14
              away: 10
              total: 24
            average:
              home: '2.0'
              away: '1.7'
              total: '1.8'
        biggest:
          streak:
            wins: 1
            draws: 1
            loses: 4
          wins:
            home: 3-1
            away: 0-1
          loses:
            home: 0-6
            away: 3-0
          goals:
            for:
              home: 3
              away: 1
            against:
              home: 6
              away: 3
        clean_sheet:
          home: 1
          away: 1
          total: 2
        failed_to_score:
          home: 3
          away: 3
          total: 6
  comparison:
    form:
      home: 60%
      away: 40%
    att:
      home: 43%
      away: 57%
    def:
      home: 62%
      away: 38%
    poisson_distribution:
      home: 75%
      away: 25%
    h2h:
      home: 29%
      away: 71%
    goals:
      home: 40%
      away: 60%
    total:
      home: 51.5%
      away: 48.5%
  h2h:
  - fixture:
      id: 198706
      referee: J. Méndez
      timezone: UTC
      date: '2019-07-27T19:30:00+00:00'
      timestamp: 1564255800
      periods:
        first: 1564255800
        second: 1564259400
      venue:
        id: null
        name: Estadio Lic. Erico Galeano Segovia (Capiatá)
        city: null
      status:
        long: Match Finished
        short: FT
        elapsed: 90
        extra: null
    league:
      id: 252
      name: Primera Division - Clausura
      country: Paraguay
      logo: https://media.api-sports.io/football/leagues/252.png
      flag: https://media.api-sports.io/flags/py.svg
      season: 2019
      round: Clausura - 3
    teams:
      home:
        id: 1180
        name: Deportivo Capiata
        logo: https://media.api-sports.io/football/teams/1180.png
        winner: true
      away:
        id: 1189
        name: Deportivo Santani
        logo: https://media.api-sports.io/football/teams/1189.png
        winner: false
    goals:
      home: 3
      away: 1
    score:
      halftime:
        home: 1
        away: 1
      fulltime:
        home: 3
        away: 1
      extratime:
        home: null
        away: null
      penalty:
        home: null
        away: null
  - fixture:
      id: 144182
      referee: null
      timezone: UTC
      date: '2019-03-25T23:15:00+00:00'
      timestamp: 1553555700
      periods:
        first: 1553555700
        second: 1553559300
      venue:
        id: null
        name: Estadio Lic. Erico Galeano Segovia (Capiatá)
        city: null
      status:
        long: Match Finished
        short: FT
        elapsed: 90
        extra: null
    league:
      id: 250
      name: Primera Division - Apertura
      country: Paraguay
      logo: https://media.api-sports.io/football/leagues/250.png
      flag: https://media.api-sports.io/flags/py.svg
      season: 2019
      round: Regular Season - 12
    teams:
      home:
        id: 1180
        name: Deportivo Capiata
        logo: https://media.api-sports.io/football/teams/1180.png
        winner: true
      away:
        id: 1189
        name: Deportivo Santani
        logo: https://media.api-sports.io/football/teams/1189.png
        winner: false
    goals:
      home: 2
      away: 1
    score:
      halftime:
        home: 2
        away: 1
      fulltime:
        home: 2
        away: 1
      extratime:
        home: null
        away: null
      penalty:
        home: null
        away: null
  - fixture:
      id: 144113
      referee: null
      timezone: UTC
      date: '2019-01-23T21:00:00+00:00'
      timestamp: 1548277200
      periods:
        first: 1548277200
        second: 1548280800
      venue:
        id: null
        name: Estadio Juan José Vázquez (San Estanislao)
        city: null
      status:
        long: Match Finished
        short: FT
        elapsed: 90
        extra: null
    league:
      id: 250
      name: Primera Division - Apertura
      country: Paraguay
      logo: https://media.api-sports.io/football/leagues/250.png
      flag: https://media.api-sports.io/flags/py.svg
      season: 2019
      round: Regular Season - 1
    teams:
      home:
        id: 1189
        name: Deportivo Santani
        logo: https://media.api-sports.io/football/teams/1189.png
        winner: null
      away:
        id: 1180
        name: Deportivo Capiata
        logo: https://media.api-sports.io/football/teams/1180.png
        winner: null
    goals:
      home: 0
      away: 0
    score:
      halftime:
        home: 0
        away: 0
      fulltime:
        home: 0
        away: 0
      extratime:
        home: null
        away: null
      penalty:
        home: null
        away: null
  - fixture:
      id: 144745
      referee: null
      timezone: UTC
      date: '2018-11-12T20:45:00+00:00'
      timestamp: 1542055500
      periods:
        first: 1542055500
        second: 1542059100
      venue:
        id: null
        name: Estadio Lic. Erico Galeano Segovia (Capiatá)
        city: null
      status:
        long: Match Finished
        short: FT
        elapsed: 90
        extra: null
    league:
      id: 252
      name: Primera Division - Clausura
      country: Paraguay
      logo: https://media.api-sports.io/football/leagues/252.png
      flag: https://media.api-sports.io/flags/py.svg
      season: 2018
      round: Regular Season - 18
    teams:
      home:
        id: 1180
        name: Deportivo Capiata
        logo: https://media.api-sports.io/football/teams/1180.png
        winner: false
      away:
        id: 1189
        name: Deportivo Santani
        logo: https://media.api-sports.io/football/teams/1189.png
        winner: true
    goals:
      home: 0
      away: 2
    score:
      halftime:
        home: 0
        away: 1
      fulltime:
        home: 0
        away: 2
      extratime:
        home: null
        away: null
      penalty:
        home: null
        away: null
  - fixture:
      id: 144679
      referee: null
      timezone: UTC
      date: '2018-08-26T19:30:00+00:00'
      timestamp: 1535311800
      periods:
        first: 1535311800
        second: 1535315400
      venue:
        id: null
        name: Estadio Juan José Vázquez (San Estanislao)
        city: null
      status:
        long: Match Finished
        short: FT
        elapsed: 90
        extra: null
    league:
      id: 252
      name: Primera Division - Clausura
      country: Paraguay
      logo: https://media.api-sports.io/football/leagues/252.png
      flag: https://media.api-sports.io/flags/py.svg
      season: 2018
      round: Regular Season - 7
    teams:
      home:
        id: 1189
        name: Deportivo Santani
        logo: https://media.api-sports.io/football/teams/1189.png
        winner: false
      away:
        id: 1180
        name: Deportivo Capiata
        logo: https://media.api-sports.io/football/teams/1180.png
        winner: true
    goals:
      home: 0
      away: 1
    score:
      halftime:
        home: 0
        away: 1
      fulltime:
        home: 0
        away: 1
      extratime:
        home: null
        away: null
      penalty:
        home: null
        away: null
  - fixture:
      id: 144330
      referee: null
      timezone: UTC
      date: '2018-05-05T21:30:00+00:00'
      timestamp: 1525555800
      periods:
        first: 1525555800
        second: 1525559400
      venue:
        id: null
        name: Estadio Juan José Vázquez (San Estanislao)
        city: null
      status:
        long: Match Finished
        short: FT
        elapsed: 90
        extra: null
    league:
      id: 250
      name: Primera Division - Apertura
      country: Paraguay
      logo: https://media.api-sports.io/football/leagues/250.png
      flag: https://media.api-sports.io/flags/py.svg
      season: 2018
      round: Regular Season - 15
    teams:
      home:
        id: 1189
        name: Deportivo Santani
        logo: https://media.api-sports.io/football/teams/1189.png
        winner: null
      away:
        id: 1180
        name: Deportivo Capiata
        logo: https://media.api-sports.io/football/teams/1180.png
        winner: null
    goals:
      home: 3
      away: 3
    score:
      halftime:
        home: 2
        away: 1
      fulltime:
        home: 3
        away: 3
      extratime:
        home: null
        away: null
      penalty:
        home: null
        away: null
  - fixture:
      id: 144264
      referee: null
      timezone: UTC
      date: '2018-02-25T20:45:00+00:00'
      timestamp: 1519591500
      periods:
        first: 1519591500
        second: 1519595100
      venue:
        id: null
        name: Estadio Lic. Erico Galeano Segovia (Capiatá)
        city: null
      status:
        long: Match Finished
        short: FT
        elapsed: 90
        extra: null
    league:
      id: 250
      name: Primera Division - Apertura
      country: Paraguay
      logo: https://media.api-sports.io/football/leagues/250.png
      flag: https://media.api-sports.io/flags/py.svg
      season: 2018
      round: Regular Season - 4
    teams:
      home:
        id: 1180
        name: Deportivo Capiata
        logo: https://media.api-sports.io/football/teams/1180.png
        winner: true
      away:
        id: 1189
        name: Deportivo Santani
        logo: https://media.api-sports.io/football/teams/1189.png
        winner: false
    goals:
      home: 2
      away: 1
    score:
      halftime:
        home: 1
        away: 1
      fulltime:
        home: 2
        away: 1
      extratime:
        home: null
        away: null
      penalty:
        home: null
        away: null
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: predictions parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'  ...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/predictions"
params = {
    "fixture": '<fixture>',  # The id of the fixture
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/predictions?fixture=198772", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /coachs` — Coachs

**Tags:** Coachs
**Operation ID:** `get-coachs`

Get all the information about the coachs and their careers.

To get the photo of a coach you have to call the following url: `https://media.api-sports.io/football/coachs/{coach_id}.png`

**Update Frequency** : This endpoint is updated every day.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `id` | query | integer | no | The id of the coach |
| `team` | query | integer | no | The id of the team |
| `search` | query | string minLength: 3 | no | The name of the coach |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: coachs
parameters:
  team: '85'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- id: 40
  name: T. Tuchel
  firstname: Thomas
  lastname: Tuchel
  age: 47
  birth:
    date: '1973-08-29'
    place: Krumbach
    country: Germany
  nationality: Germany
  height: 192 cm
  weight: 85 kg
  photo: https://media.api-sports.io/football/coachs/40.png
  team:
    id: 85
    name: PSG
    logo: https://media.api-sports.io/football/teams/85.png
  career:
  - team:
      id: 85
      name: PSG
      logo: https://media.api-sports.io/football/teams/85.png
    start: '2018-07-01'
    end: null
  - team:
      id: 165
      name: Borussia Dortmund
      logo: https://media.api-sports.io/football/teams/165.png
    start: '2015-07-01'
    end: '2017-05-01'
  - team:
      id: 164
      name: Mainz 05
      logo: https://media.api-sports.io/football/teams/164.png
    start: '2009-08-01'
    end: '2014-05-01'
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: coachs parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   bug:...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/coachs"
params = {
    "id": '<id>',  # The id of the coach
    "team": '<team>',  # The id of the team
    "search": '<search>',  # The name of the coach
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/coachs?team=85", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /players/seasons` — Seasons

**Tags:** Players
**Operation ID:** `get-players-seasons`

Get all available seasons for players statistics.

**Update Frequency** : This endpoint is updated every day.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `player` | query | integer | no | The id of the player |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: players/seasons
parameters: []
errors: []
results: 35
paging:
  current: 1
  total: 1
response:
- 1966
- 1982
- 1986
- 1990
- 1991
- 1992
- 1993
- 1994
- 1995
- 1996
- 1997
- 1998
- 1999
- 2000
- 2001
- 2002
- 2003
- 2004
- 2005
- 2006
- 2007
- 2008
- 2009
- 2010
- 2011
- 2012
- 2013
- 2014
- 2015
- 2016
- 2017
- 2018
- 2019
- 2020
- 2022
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: players/seasons parameters: [] errors:   time: '2019-11-26T00:00:00+00:0...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/players/seasons"
params = {
    "player": '<player>',  # The id of the player
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/players/seasons", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /players/profiles` — Profiles

**Tags:** Players
**Operation ID:** `get-players-profiles`

Returns the list of all available players.

It is possible to call this endpoint without parameters, but you will need to use the **pagination** to get  all available players.

To get the photo of a player you have to call the following url: `https://media.api-sports.io/football/players/{player_id}.png`

This endpoint uses a **pagination system**, you can navigate between the different pages with to the `page` parameter.

> **Pagination** : 250 results per page.

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per week.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `player` | query | integer | no | The id of the player |
| `search` | query | string minLength: 4 | no | The lastname of the player |
| `page` | query | integer | no | Use for the pagination |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: players/profiles
parameters:
  player: '276'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- player:
    id: 276
    name: Neymar
    firstname: Neymar
    lastname: da Silva Santos Júnior
    age: 32
    birth:
      date: '1992-02-05'
      place: Mogi das Cruzes
      country: Brazil
    nationality: Brazil
    height: 175 cm
    weight: 68 kg
    number: 10
    position: Attacker
    photo: https://media.api-sports.io/football/players/276.png
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: players/squad parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/players/profiles"
params = {
    "player": '<player>',  # The id of the player
    "search": '<search>',  # The lastname of the player
    "page": '<page>',  # Use for the pagination
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/players/profiles?player=276", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /players` — Statistics

**Tags:** Players
**Operation ID:** `get-players`

Get players statistics.

This endpoint returns the players for whom the `profile` and `statistics` data are available. Note that it is possible that a player has statistics for 2 teams in the same season in case of transfers.

The statistics are calculated according to the team `id`, league `id` and `season`.

You can find the available `seasons` by using the endpoint `players/seasons`.

> To get the squads of the teams it is better to use the endpoint `players/squads`.

The players `id` are unique in the API and players keep it among all the teams they have been in.

In this endpoint you have the `rating` field, which is the rating of the player according to a match or a season. This data is calculated according to the performance of the player in relation to the other players of the game or the season who occupy the same position *(Attacker, defender, goal...)*. There are different algorithms that take into account the position of the player and assign points according to his performance.

To get the photo of a player you have to call the following url: `https://media.api-sports.io/football/players/{player_id}.png`

This endpoint uses a **pagination system**, you can navigate between the different pages with to the `page` parameter.

> **Pagination** : 20 results per page.

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

**Tutorials** :
- [HOW TO GET ALL TEAMS AND PLAYERS FROM A LEAGUE ID](https://www.api-football.com/tutorials/4/how-to-get-all-teams-and-players-from-a-league-id)

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `id` | query | integer | no | The id of the player |
| `team` | query | integer | no | The id of the team |
| `league` | query | integer | no | The id of the league |
| `season` | query | integer pattern: YYYY \| Requires the fields Id, League or Team minLength: 4 maxLength: 4 | no | The season of the league |
| `search` | query | string pattern: Requires the fields League or Team minLength: 4 | no | The name of the player |
| `page` | query | integer | no | Use for the pagination |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: players
parameters:
  id: '276'
  season: '2019'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- player:
    id: 276
    name: Neymar
    firstname: Neymar
    lastname: da Silva Santos Júnior
    age: 28
    birth:
      date: '1992-02-05'
      place: Mogi das Cruzes
      country: Brazil
    nationality: Brazil
    height: 175 cm
    weight: 68 kg
    injured: false
    photo: https://media.api-sports.io/football/players/276.png
  statistics:
  - team:
      id: 85
      name: Paris Saint Germain
      logo: https://media.api-sports.io/football/teams/85.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2019
    games:
      appearences: 15
      lineups: 15
      minutes: 1322
      number: null
      position: Attacker
      rating: '8.053333'
      captain: false
    substitutes:
      in: 0
      out: 3
      bench: 0
    shots:
      total: 70
      'on': 36
    goals:
      total: 13
      conceded: null
      assists: 6
      saves: 0
    passes:
      total: 704
      key: 39
      accuracy: 79
    tackles:
      total: 13
      blocks: 0
      interceptions: 4
    duels:
      total: null
      won: null
    dribbles:
      attempts: 143
      success: 88
      past: null
    fouls:
      drawn: 62
      committed: 14
    cards:
      yellow: 3
      yellowred: 1
      red: 0
    penalty:
      won: 1
      commited: null
      scored: 4
      missed: 1
      saved: null
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: players parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   bug...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/players"
params = {
    "id": '<id>',  # The id of the player
    "team": '<team>',  # The id of the team
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
    "search": '<search>',  # The name of the player
    "page": '<page>',  # Use for the pagination
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/players?id=276&season=2019", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /players/squads` — Squads

**Tags:** Players
**Operation ID:** `get-players-squads`

Return the current squad of a team when the `team` parameter is used. When the `player` parameter is used the endpoint returns the set of teams associated with the player.

> The response format is the same regardless of the parameter sent.

**This endpoint requires at least one parameter.**

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per week.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `team` | query | integer | no | The id of the team |
| `player` | query | integer | no | The id of the player |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: players/squads
parameters:
  team: '33'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- team:
    id: 33
    name: Manchester United
    logo: https://media.api-sports.io/football/teams/33.png
  players:
  - id: 20319
    name: N. Bishop
    age: 22
    number: 30
    position: Goalkeeper
    photo: https://media.api-sports.io/football/players/20319.png
  - id: 882
    name: David de Gea
    age: 31
    number: 1
    position: Goalkeeper
    photo: https://media.api-sports.io/football/players/882.png
  - id: 883
    name: L. Grant
    age: 38
    number: 13
    position: Goalkeeper
    photo: https://media.api-sports.io/football/players/883.png
  - id: 2931
    name: T. Heaton
    age: 35
    number: null
    position: Goalkeeper
    photo: https://media.api-sports.io/football/players/2931.png
  - id: 19088
    name: D. Henderson
    age: 24
    number: 26
    position: Goalkeeper
    photo: https://media.api-sports.io/football/players/19088.png
  - id: 885
    name: E. Bailly
    age: 27
    number: 3
    position: Defender
    photo: https://media.api-sports.io/football/players/885.png
  - id: 886
    name: Diogo Dalot
    age: 22
    number: 20
    position: Defender
    photo: https://media.api-sports.io/football/players/886.png
  - id: 153434
    name: W. Fish
    age: 18
    number: 48
    position: Defender
    photo: https://media.api-sports.io/football/players/153434.png
  - id: 888
    name: P. Jones
    age: 29
    number: 4
    position: Defender
    photo: https://media.api-sports.io/football/players/888.png
  - id: 138775
    name: E. Laird
    age: 20
    number: null
    position: Defender
    photo: https://media.api-sports.io/football/players/138775.png
  - id: 2935
    name: H. Maguire
    age: 28
    number: 5
    position: Defender
    photo: https://media.api-sports.io/football/players/2935.png
  - id: 889
    name: V. Lindelöf
    age: 27
    number: 2
    position: Defender
    photo: https://media.api-sports.io/football/players/889.png
  - id: 891
    name: L. Shaw
    age: 26
    number: 23
    position: Defender
    photo: https://media.api-sports.io/football/players/891.png
  - id: 378
    name: Alex Telles
    age: 29
    number: 27
    position: Defender
    photo: https://media.api-sports.io/football/players/378.png
  - id: 19182
    name: A. Tuanzebe
    age: 24
    number: 38
    position: Defender
    photo: https://media.api-sports.io/football/players/19182.png
  - id: 18846
    name: A. Wan-Bissaka
    age: 24
    number: 29
    position: Defender
    photo: https://media.api-sports.io/football/players/18846.png
  - id: 138806
    name: B. Williams
    age: 21
    number: 33
    position: Defender
    photo: https://media.api-sports.io/football/players/138806.png
  - id: 1485
    name: Bruno Fernandes
    age: 27
    number: 18
    position: Midfielder
    photo: https://media.api-sports.io/football/players/1485.png
  - id: 906
    name: T. Chong
    age: 22
    number: 44
    position: Midfielder
    photo: https://media.api-sports.io/football/players/906.png
  - id: 895
    name: J. Garner
    age: 20
    number: null
    position: Midfielder
    photo: https://media.api-sports.io/football/players/895.png
  - id: 899
    name: Andreas Pereira
    age: 25
    number: 15
    position: Midfielder
    photo: https://media.api-sports.io/football/players/899.png
  - id: 900
    name: J. Lingard
    age: 29
    number: 14
    position: Midfielder
    photo: https://media.api-sports.io/football/players/900.png
  - id: 901
    name: Mata
    age: 33
    number: 8
    position: Midfielder
    photo: https://media.api-sports.io/football/players/901.png
  - id: 902
    name: N. Matić
    age: 33
    number: 31
    position: Midfielder
    photo: https://media.api-sports.io/football/players/902.png
  - id: 903
    name: S. McTominay
    age: 25
    number: 39
    position: Midfielder
    photo: https://media.api-sports.io/football/players/903.png
  - id: 180560
    name: H. Mejbri
    age: 18
    number: 46
    position: Midfielder
    photo: https://media.api-sports.io/football/players/180560.png
  - id: 904
    name: P. Pogba
    age: 28
    number: 6
    position: Midfielder
    photo: https://media.api-sports.io/football/players/904.png
  - id: 905
    name: Fred
    age: 28
    number: 17
    position: Midfielder
    photo: https://media.api-sports.io/football/players/905.png
  - id: 163054
    name: S. Shoretire
    age: 17
    number: 74
    position: Midfielder
    photo: https://media.api-sports.io/football/players/163054.png
  - id: 547
    name: D. van de Beek
    age: 24
    number: 34
    position: Midfielder
    photo: https://media.api-sports.io/football/players/547.png
  - id: 138814
    name: E. Galbraith
    age: 20
    number: null
    position: Midfielder
    photo: https://media.api-sports.io/football/players/138814.png
  - id: 274
    name: E. Cavani
    age: 34
    number: 7
    position: Attacker
    photo: https://media.api-sports.io/football/players/274.png
  - id: 153430
    name: A. Elanga
    age: 19
    number: 56
    position: Attacker
    photo: https://media.api-sports.io/football/players/153430.png
  - id: 897
    name: M. Greenwood
    age: 20
    number: 11
    position: Attacker
    photo: https://media.api-sports.io/football/players/897.png
  - id: 19329
    name: D. James
    age: 24
    number: 21
    position: Attacker
    photo: https://media.api-sports.io/football/players/19329.png
  - id: 908
    name: A. Martial
    age: 26
    number: 9
    position: Attacker
    photo: https://media.api-sports.io/football/players/908.png
  - id: 909
    name: M. Rashford
    age: 24
    number: 10
    position: Attacker
    photo: https://media.api-sports.io/football/players/909.png
  - id: 157997
    name: A. Diallo
    age: 19
    number: 19
    position: Attacker
    photo: https://media.api-sports.io/football/players/157997.png
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: players/squad parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/players/squads"
params = {
    "team": '<team>',  # The id of the team
    "player": '<player>',  # The id of the player
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/players/squads?team=33", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /players/teams` — Teams

**Tags:** Players
**Operation ID:** `get-players-teams`

Returns the list of teams and seasons in which the player played during his career.

**This endpoint requires at least one parameter.**

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per week.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `player` | query | integer | yes | The id of the player |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: players/teams
parameters:
  player: '276'
errors: []
results: 8
paging:
  current: 1
  total: 1
response:
- team:
    id: 6
    name: Brazil
    logo: https://media.api-sports.io/football/teams/6.png
  seasons:
  - 2026
  - 2023
  - 2022
  - 2021
  - 2019
  - 2018
  - 2017
  - 2016
  - 2015
  - 2014
  - 2013
  - 2012
  - 2011
  - 2010
- team:
    id: 2932
    name: Al-Hilal Saudi FC
    logo: https://media.api-sports.io/football/teams/2932.png
  seasons:
  - 2024
  - 2023
- team:
    id: 85
    name: Paris Saint Germain
    logo: https://media.api-sports.io/football/teams/85.png
  seasons:
  - 2022
  - 2021
  - 2020
  - 2019
  - 2018
  - 2017
- team:
    id: 529
    name: Barcelona
    logo: https://media.api-sports.io/football/teams/529.png
  seasons:
  - 2016
  - 2015
  - 2014
  - 2013
- team:
    id: 10171
    name: Brazil  U23
    logo: https://media.api-sports.io/football/teams/10171.png
  seasons:
  - 2016
  - 2012
- team:
    id: 128
    name: Santos
    logo: https://media.api-sports.io/football/teams/128.png
  seasons:
  - 2012
  - 2011
  - 2010
  - 2009
- team:
    id: 16200
    name: Brazil U20
    logo: https://media.api-sports.io/football/teams/16200.png
  seasons:
  - 2011
- team:
    id: 12502
    name: Brazil U17
    logo: https://media.api-sports.io/football/teams/12502.png
  seasons:
  - 2009
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: players/squad parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/players/teams"
params = {
    "player": '<player>',  # The id of the player
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/players/teams?player=276", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /players/topscorers` — Top Scorers

**Tags:** Players
**Operation ID:** `get-players-topscorers`

Get the 20 best players for a league or cup.

**How it is calculated:**

* 1 : The player that has scored the higher number of goals
* 2 : The player that has scored the fewer number of penalties
* 3 : The player that has delivered the higher number of goal assists
* 4 : The player that scored their goals in the higher number of matches
* 5 : The player that played the fewer minutes
* 6 : The player that plays for the team placed higher on the table
* 7 : The player that received the fewer number of red cards
* 8 : The player that received the fewer number of yellow cards

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `league` | query | integer | yes | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | yes | The season of the league |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: players/topscorers
parameters:
  league: '61'
  season: '2018'
errors: []
results: 20
paging:
  current: 1
  total: 1
response:
- player:
    id: 278
    name: K. Mbappé
    firstname: Kylian
    lastname: Mbappé Lottin
    age: 22
    birth:
      date: '1998-12-20'
      place: Paris
      country: France
    nationality: France
    height: 178 cm
    weight: 73 kg
    injured: false
    photo: https://media.api-sports.io/football/players/278.png
  statistics:
  - team:
      id: 85
      name: Paris Saint Germain
      logo: https://media.api-sports.io/football/teams/85.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2018
    games:
      appearences: 29
      lineups: 24
      minutes: 2340
      number: null
      position: Attacker
      rating: '7.871428'
      captain: false
    substitutes:
      in: 5
      out: 1
      bench: 5
    shots:
      total: 122
      'on': 68
    goals:
      total: 33
      conceded: null
      assists: 7
      saves: 0
    passes:
      total: 591
      key: 48
      accuracy: 78
    tackles:
      total: 4
      blocks: 0
      interceptions: 4
    duels:
      total: 232
      won: 112
    dribbles:
      attempts: 115
      success: 64
      past: null
    fouls:
      drawn: 39
      committed: 19
    cards:
      yellow: 5
      yellowred: 0
      red: 1
    penalty:
      won: 3
      commited: null
      scored: 1
      missed: 0
      saved: null
- player:
    id: 3246
    name: N. Pépé
    firstname: Nicolas
    lastname: Pépé
    age: 25
    birth:
      date: '1995-05-29'
      place: Mantes-la-Jolie
      country: France
    nationality: Côte d'Ivoire
    height: 178 cm
    weight: 68 kg
    injured: false
    photo: https://media.api-sports.io/football/players/3246.png
  statistics:
  - team:
      id: 79
      name: Lille
      logo: https://media.api-sports.io/football/teams/79.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2018
    games:
      appearences: 38
      lineups: 37
      minutes: 3332
      number: null
      position: Attacker
      rating: '7.281578'
      captain: false
    substitutes:
      in: 1
      out: 9
      bench: 1
    shots:
      total: 118
      'on': 61
    goals:
      total: 22
      conceded: null
      assists: 11
      saves: 0
    passes:
      total: 946
      key: 70
      accuracy: 78
    tackles:
      total: 9
      blocks: 0
      interceptions: 12
    duels:
      total: 556
      won: 279
    dribbles:
      attempts: 182
      success: 102
      past: null
    fouls:
      drawn: 108
      committed: 24
    cards:
      yellow: 1
      yellowred: 0
      red: 0
    penalty:
      won: 5
      commited: null
      scored: 9
      missed: 1
      saved: null
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: players/topscorers parameters: [] errors:   time: '2019-11-26T00:00:00+0...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/players/topscorers"
params = {
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/players/topscorers?season=2018&league=61", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /players/topassists` — Top Assists

**Tags:** Players
**Operation ID:** `get-players-topassists`

Get the 20 best players assists for a league or cup.

**How it is calculated:**

* 1 : The player that has delivered the higher number of goal assists
* 2 : The player that has scored the higher number of goals
* 3 : The player that has scored the fewer number of penalties
* 4 : The player that assists in the higher number of matches
* 5 : The player that played the fewer minutes
* 6 : The player that received the fewer number of red cards
* 7 : The player that received the fewer number of yellow cards

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `league` | query | integer | yes | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | yes | The season of the league |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: players/topassists
parameters:
  season: '2020'
  league: '61'
errors: []
results: 20
paging:
  current: 0
  total: 1
response:
- player:
    id: 667
    name: M. Depay
    firstname: Memphis
    lastname: Depay
    age: 27
    birth:
      date: '1994-02-13'
      place: Moordrecht
      country: Netherlands
    nationality: Netherlands
    height: 176 cm
    weight: 78 kg
    injured: false
    photo: https://media.api-sports.io/football/players/667.png
  statistics:
  - team:
      id: 80
      name: Lyon
      logo: https://media.api-sports.io/football/teams/80.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 30
      lineups: 26
      minutes: 2313
      number: null
      position: Attacker
      rating: '7.496666'
      captain: false
    substitutes:
      in: 4
      out: 12
      bench: 4
    shots:
      total: 72
      'on': 39
    goals:
      total: 14
      conceded: 0
      assists: 9
      saves: null
    passes:
      total: 808
      key: 79
      accuracy: 22
    tackles:
      total: 4
      blocks: 1
      interceptions: 4
    duels:
      total: 282
      won: 108
    dribbles:
      attempts: 119
      success: 56
      past: null
    fouls:
      drawn: 38
      committed: 27
    cards:
      yellow: 3
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 7
      missed: 0
      saved: null
- player:
    id: 22235
    name: J. Bamba
    firstname: Jonathan
    lastname: Bamba
    age: 25
    birth:
      date: '1996-03-26'
      place: Alfortville
      country: France
    nationality: France
    height: 175 cm
    weight: 72 kg
    injured: false
    photo: https://media.api-sports.io/football/players/22235.png
  statistics:
  - team:
      id: 79
      name: Lille
      logo: https://media.api-sports.io/football/teams/79.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 29
      lineups: 27
      minutes: 2379
      number: null
      position: Attacker
      rating: '6.965517'
      captain: false
    substitutes:
      in: 2
      out: 9
      bench: 2
    shots:
      total: 32
      'on': 14
    goals:
      total: 6
      conceded: 0
      assists: 8
      saves: null
    passes:
      total: 1186
      key: 52
      accuracy: 37
    tackles:
      total: 35
      blocks: 1
      interceptions: 21
    duels:
      total: 354
      won: 147
    dribbles:
      attempts: 106
      success: 48
      past: null
    fouls:
      drawn: 51
      committed: 23
    cards:
      yellow: 1
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 266
    name: Á. Di María
    firstname: Ángel Fabián
    lastname: Di María Hernández
    age: 33
    birth:
      date: '1988-02-14'
      place: Rosario
      country: Argentina
    nationality: Argentina
    height: 180 cm
    weight: 75 kg
    injured: false
    photo: https://media.api-sports.io/football/players/266.png
  statistics:
  - team:
      id: 85
      name: Paris Saint Germain
      logo: https://media.api-sports.io/football/teams/85.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 21
      lineups: 19
      minutes: 1507
      number: null
      position: Midfielder
      rating: '7.547619'
      captain: false
    substitutes:
      in: 2
      out: 13
      bench: 2
    shots:
      total: 36
      'on': 15
    goals:
      total: 4
      conceded: 0
      assists: 8
      saves: null
    passes:
      total: 781
      key: 54
      accuracy: 30
    tackles:
      total: 21
      blocks: 1
      interceptions: 6
    duels:
      total: 156
      won: 73
    dribbles:
      attempts: 64
      success: 29
      past: null
    fouls:
      drawn: 23
      committed: 9
    cards:
      yellow: 1
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 989
    name: K. Volland
    firstname: Kevin
    lastname: Volland
    age: 29
    birth:
      date: '1992-07-30'
      place: Marktoberdorf
      country: Germany
    nationality: Germany
    height: 178 cm
    weight: 85 kg
    injured: false
    photo: https://media.api-sports.io/football/players/989.png
  statistics:
  - team:
      id: 91
      name: Monaco
      logo: https://media.api-sports.io/football/teams/91.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 28
      lineups: 27
      minutes: 2173
      number: null
      position: Attacker
      rating: '7.082142'
      captain: false
    substitutes:
      in: 1
      out: 17
      bench: 1
    shots:
      total: 33
      'on': 26
    goals:
      total: 13
      conceded: 0
      assists: 7
      saves: null
    passes:
      total: 592
      key: 27
      accuracy: 14
    tackles:
      total: 26
      blocks: null
      interceptions: 3
    duels:
      total: 282
      won: 120
    dribbles:
      attempts: 35
      success: 15
      past: null
    fouls:
      drawn: 30
      committed: 42
    cards:
      yellow: 3
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 21592
    name: G. Laborde
    firstname: Gaëtan
    lastname: Laborde
    age: 27
    birth:
      date: '1994-05-03'
      place: Mont-de-Marsan
      country: France
    nationality: France
    height: 182 cm
    weight: 81 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21592.png
  statistics:
  - team:
      id: 82
      name: Montpellier
      logo: https://media.api-sports.io/football/teams/82.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 30
      lineups: 30
      minutes: 2597
      number: null
      position: Attacker
      rating: '7.080000'
      captain: false
    substitutes:
      in: 0
      out: 11
      bench: 0
    shots:
      total: 63
      'on': 32
    goals:
      total: 10
      conceded: 0
      assists: 7
      saves: null
    passes:
      total: 661
      key: 32
      accuracy: 16
    tackles:
      total: 28
      blocks: 3
      interceptions: 12
    duels:
      total: 417
      won: 185
    dribbles:
      attempts: 60
      success: 28
      past: null
    fouls:
      drawn: 24
      committed: 49
    cards:
      yellow: 3
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 21591
    name: A. Delort
    firstname: Andy
    lastname: Delort
    age: 30
    birth:
      date: '1991-10-09'
      place: Sete
      country: France
    nationality: Algeria
    height: 182 cm
    weight: 82 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21591.png
  statistics:
  - team:
      id: 82
      name: Montpellier
      logo: https://media.api-sports.io/football/teams/82.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 21
      lineups: 21
      minutes: 1700
      number: null
      position: Attacker
      rating: '7.495238'
      captain: false
    substitutes:
      in: 0
      out: 10
      bench: 0
    shots:
      total: 47
      'on': 27
    goals:
      total: 10
      conceded: 0
      assists: 7
      saves: null
    passes:
      total: 511
      key: 40
      accuracy: 16
    tackles:
      total: 8
      blocks: null
      interceptions: 3
    duels:
      total: 284
      won: 139
    dribbles:
      attempts: 41
      success: 19
      past: null
    fouls:
      drawn: 33
      committed: 42
    cards:
      yellow: 4
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 1922
    name: F. Thauvin
    firstname: Florian
    lastname: Thauvin
    age: 28
    birth:
      date: '1993-01-26'
      place: Orleans
      country: France
    nationality: France
    height: 179 cm
    weight: 70 kg
    injured: false
    photo: https://media.api-sports.io/football/players/1922.png
  statistics:
  - team:
      id: 81
      name: Marseille
      logo: https://media.api-sports.io/football/teams/81.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 29
      lineups: 26
      minutes: 2132
      number: null
      position: Midfielder
      rating: '7.220689'
      captain: false
    substitutes:
      in: 3
      out: 17
      bench: 3
    shots:
      total: 39
      'on': 15
    goals:
      total: 8
      conceded: 0
      assists: 7
      saves: null
    passes:
      total: 887
      key: 43
      accuracy: 26
    tackles:
      total: 31
      blocks: 0
      interceptions: 11
    duels:
      total: 259
      won: 130
    dribbles:
      attempts: 84
      success: 47
      past: null
    fouls:
      drawn: 42
      committed: 21
    cards:
      yellow: 3
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 2
      saved: null
- player:
    id: 109
    name: A. Golovin
    firstname: Aleksandr
    lastname: Golovin
    age: 25
    birth:
      date: '1996-05-30'
      place: Kaltan
      country: Russia
    nationality: Russia
    height: 180 cm
    weight: 69 kg
    injured: false
    photo: https://media.api-sports.io/football/players/109.png
  statistics:
  - team:
      id: 91
      name: Monaco
      logo: https://media.api-sports.io/football/teams/91.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 14
      lineups: 6
      minutes: 609
      number: null
      position: Midfielder
      rating: '7.400000'
      captain: false
    substitutes:
      in: 8
      out: 6
      bench: 8
    shots:
      total: 14
      'on': 7
    goals:
      total: 4
      conceded: 0
      assists: 7
      saves: null
    passes:
      total: 244
      key: 27
      accuracy: 22
    tackles:
      total: 17
      blocks: 0
      interceptions: 6
    duels:
      total: 94
      won: 43
    dribbles:
      attempts: 22
      success: 11
      past: null
    fouls:
      drawn: 9
      committed: 9
    cards:
      yellow: 1
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 278
    name: K. Mbappé
    firstname: Kylian
    lastname: Mbappé Lottin
    age: 23
    birth:
      date: '1998-12-20'
      place: Paris
      country: France
    nationality: France
    height: 178 cm
    weight: 73 kg
    injured: false
    photo: https://media.api-sports.io/football/players/278.png
  statistics:
  - team:
      id: 85
      name: Paris Saint Germain
      logo: https://media.api-sports.io/football/teams/85.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 25
      lineups: 21
      minutes: 1866
      number: null
      position: Attacker
      rating: '7.328000'
      captain: false
    substitutes:
      in: 4
      out: 8
      bench: 4
    shots:
      total: 64
      'on': 40
    goals:
      total: 20
      conceded: 0
      assists: 6
      saves: null
    passes:
      total: 761
      key: 27
      accuracy: 24
    tackles:
      total: 3
      blocks: 1
      interceptions: 1
    duels:
      total: 259
      won: 113
    dribbles:
      attempts: 143
      success: 72
      past: null
    fouls:
      drawn: 33
      committed: 17
    cards:
      yellow: 3
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 5
      missed: 0
      saved: null
- player:
    id: 85041
    name: A. Gouiri
    firstname: Amine
    lastname: Gouiri
    age: 21
    birth:
      date: '2000-02-16'
      place: Bourgoin-Jallieu
      country: France
    nationality: France
    height: 180 cm
    weight: 72 kg
    injured: false
    photo: https://media.api-sports.io/football/players/85041.png
  statistics:
  - team:
      id: 84
      name: Nice
      logo: https://media.api-sports.io/football/teams/84.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 29
      lineups: 27
      minutes: 2429
      number: null
      position: Attacker
      rating: '7.227586'
      captain: false
    substitutes:
      in: 2
      out: 7
      bench: 2
    shots:
      total: 61
      'on': 34
    goals:
      total: 12
      conceded: 0
      assists: 6
      saves: null
    passes:
      total: 905
      key: 44
      accuracy: 28
    tackles:
      total: 24
      blocks: 6
      interceptions: 14
    duels:
      total: 306
      won: 119
    dribbles:
      attempts: 81
      success: 45
      past: null
    fouls:
      drawn: 31
      committed: 42
    cards:
      yellow: 5
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 4
      missed: 0
      saved: null
- player:
    id: 663
    name: M. Terrier
    firstname: Martin
    lastname: Terrier
    age: 24
    birth:
      date: '1997-03-04'
      place: Armentières
      country: France
    nationality: France
    height: 184 cm
    weight: 71 kg
    injured: false
    photo: https://media.api-sports.io/football/players/663.png
  statistics:
  - team:
      id: 94
      name: Rennes
      logo: https://media.api-sports.io/football/teams/94.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 26
      lineups: 22
      minutes: 1821
      number: null
      position: Attacker
      rating: '7.048000'
      captain: false
    substitutes:
      in: 4
      out: 15
      bench: 4
    shots:
      total: 27
      'on': 10
    goals:
      total: 5
      conceded: 0
      assists: 6
      saves: null
    passes:
      total: 599
      key: 28
      accuracy: 23
    tackles:
      total: 29
      blocks: 0
      interceptions: 15
    duels:
      total: 251
      won: 124
    dribbles:
      attempts: 40
      success: 25
      past: null
    fouls:
      drawn: 30
      committed: 27
    cards:
      yellow: 2
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 1
      missed: 0
      saved: null
- player:
    id: 3175
    name: Z. Ferhat
    firstname: Zinedine
    lastname: Ferhat
    age: 28
    birth:
      date: '1993-03-01'
      place: Bordj Menaïel
      country: Algeria
    nationality: Algeria
    height: 183 cm
    weight: 77 kg
    injured: false
    photo: https://media.api-sports.io/football/players/3175.png
  statistics:
  - team:
      id: 92
      name: Nimes
      logo: https://media.api-sports.io/football/teams/92.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 25
      lineups: 25
      minutes: 2244
      number: null
      position: Midfielder
      rating: '7.076000'
      captain: false
    substitutes:
      in: 0
      out: 1
      bench: 0
    shots:
      total: 37
      'on': 18
    goals:
      total: 4
      conceded: 0
      assists: 6
      saves: null
    passes:
      total: 809
      key: 39
      accuracy: 27
    tackles:
      total: 28
      blocks: 0
      interceptions: 25
    duels:
      total: 350
      won: 186
    dribbles:
      attempts: 95
      success: 48
      past: null
    fouls:
      drawn: 52
      committed: 18
    cards:
      yellow: 3
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 1709
    name: K. Toko Ekambi
    firstname: Karl Brillant
    lastname: Toko Ekambi
    age: 29
    birth:
      date: '1992-09-14'
      place: Paris
      country: France
    nationality: Cameroon
    height: 185 cm
    weight: 74 kg
    injured: false
    photo: https://media.api-sports.io/football/players/1709.png
  statistics:
  - team:
      id: 80
      name: Lyon
      logo: https://media.api-sports.io/football/teams/80.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 27
      lineups: 26
      minutes: 2142
      number: null
      position: Attacker
      rating: '7.259259'
      captain: false
    substitutes:
      in: 1
      out: 15
      bench: 1
    shots:
      total: 56
      'on': 32
    goals:
      total: 12
      conceded: 0
      assists: 5
      saves: null
    passes:
      total: 663
      key: 40
      accuracy: 22
    tackles:
      total: 12
      blocks: 0
      interceptions: 20
    duels:
      total: 224
      won: 98
    dribbles:
      attempts: 85
      success: 50
      past: null
    fouls:
      drawn: 15
      committed: 20
    cards:
      yellow: 3
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 20526
    name: F. Boulaya
    firstname: Farid
    lastname: Boulaya
    age: 28
    birth:
      date: '1993-02-25'
      place: Vitrolles
      country: France
    nationality: Algeria
    height: 179 cm
    weight: 70 kg
    injured: false
    photo: https://media.api-sports.io/football/players/20526.png
  statistics:
  - team:
      id: 112
      name: Metz
      logo: https://media.api-sports.io/football/teams/112.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 26
      lineups: 26
      minutes: 2309
      number: null
      position: Midfielder
      rating: '7.496153'
      captain: false
    substitutes:
      in: 0
      out: 6
      bench: 1
    shots:
      total: 48
      'on': 24
    goals:
      total: 5
      conceded: 0
      assists: 5
      saves: null
    passes:
      total: 1092
      key: 61
      accuracy: 33
    tackles:
      total: 19
      blocks: 2
      interceptions: 9
    duels:
      total: 286
      won: 141
    dribbles:
      attempts: 74
      success: 48
      past: null
    fouls:
      drawn: 51
      committed: 18
    cards:
      yellow: 5
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 1
      saved: null
- player:
    id: 20600
    name: R. Perraud
    firstname: Romain
    lastname: Perraud
    age: 24
    birth:
      date: '1997-09-22'
      place: Toulouse
      country: France
    nationality: France
    height: 173 cm
    weight: 68 kg
    injured: false
    photo: https://media.api-sports.io/football/players/20600.png
  statistics:
  - team:
      id: 106
      name: Stade Brestois 29
      logo: https://media.api-sports.io/football/teams/106.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 27
      lineups: 26
      minutes: 2331
      number: null
      position: Defender
      rating: '6.970370'
      captain: false
    substitutes:
      in: 1
      out: 1
      bench: 1
    shots:
      total: 28
      'on': 11
    goals:
      total: 3
      conceded: 0
      assists: 5
      saves: null
    passes:
      total: 1109
      key: 27
      accuracy: 34
    tackles:
      total: 49
      blocks: 3
      interceptions: 34
    duels:
      total: 237
      won: 132
    dribbles:
      attempts: 32
      success: 22
      past: null
    fouls:
      drawn: 42
      committed: 37
    cards:
      yellow: 3
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 665
    name: M. Cornet
    firstname: Gnaly Maxwel
    lastname: Cornet
    age: 25
    birth:
      date: '1996-09-27'
      place: Bregbo
      country: Côte d'Ivoire
    nationality: Côte d'Ivoire
    height: 179 cm
    weight: 69 kg
    injured: false
    photo: https://media.api-sports.io/football/players/665.png
  statistics:
  - team:
      id: 80
      name: Lyon
      logo: https://media.api-sports.io/football/teams/80.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 28
      lineups: 22
      minutes: 1867
      number: null
      position: Attacker
      rating: '6.996428'
      captain: false
    substitutes:
      in: 6
      out: 15
      bench: 6
    shots:
      total: 13
      'on': 8
    goals:
      total: 2
      conceded: 0
      assists: 5
      saves: null
    passes:
      total: 1044
      key: 23
      accuracy: 32
    tackles:
      total: 56
      blocks: 3
      interceptions: 32
    duels:
      total: 222
      won: 126
    dribbles:
      attempts: 29
      success: 18
      past: null
    fouls:
      drawn: 26
      committed: 26
    cards:
      yellow: 5
      yellowred: 0
      red: 0
    penalty:
      won: 1
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 1265
    name: Y. Adli
    firstname: Yacine
    lastname: Adli
    age: 21
    birth:
      date: '2000-07-29'
      place: Vitry-sur-Seine
      country: France
    nationality: France
    height: 186 cm
    weight: 73 kg
    injured: false
    photo: https://media.api-sports.io/football/players/1265.png
  statistics:
  - team:
      id: 78
      name: Bordeaux
      logo: https://media.api-sports.io/football/teams/78.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 26
      lineups: 16
      minutes: 1622
      number: null
      position: Midfielder
      rating: '6.996153'
      captain: false
    substitutes:
      in: 10
      out: 8
      bench: 10
    shots:
      total: 10
      'on': 5
    goals:
      total: 1
      conceded: 0
      assists: 5
      saves: null
    passes:
      total: 1077
      key: 38
      accuracy: 35
    tackles:
      total: 58
      blocks: 2
      interceptions: 30
    duels:
      total: 265
      won: 137
    dribbles:
      attempts: 56
      success: 36
      past: null
    fouls:
      drawn: 25
      committed: 24
    cards:
      yellow: 6
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 21585
    name: S. Sambia
    firstname: Salomon Junior
    lastname: Sambia
    age: 25
    birth:
      date: '1996-09-07'
      place: Lyon
      country: France
    nationality: France
    height: 181 cm
    weight: 68 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21585.png
  statistics:
  - team:
      id: 82
      name: Montpellier
      logo: https://media.api-sports.io/football/teams/82.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 28
      lineups: 19
      minutes: 1819
      number: null
      position: Midfielder
      rating: '6.818518'
      captain: false
    substitutes:
      in: 9
      out: 4
      bench: 10
    shots:
      total: 13
      'on': 4
    goals:
      total: 0
      conceded: 0
      assists: 5
      saves: null
    passes:
      total: 808
      key: 24
      accuracy: 26
    tackles:
      total: 37
      blocks: 6
      interceptions: 29
    duels:
      total: 228
      won: 126
    dribbles:
      attempts: 53
      success: 26
      past: null
    fouls:
      drawn: 30
      committed: 18
    cards:
      yellow: 1
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 19334
    name: B. Celina
    firstname: Bersant
    lastname: Celina
    age: 25
    birth:
      date: '1996-09-09'
      place: Prizren
      country: Kosovo
    nationality: Kosovo
    height: 181 cm
    weight: null
    injured: false
    photo: https://media.api-sports.io/football/players/19334.png
  statistics:
  - team:
      id: 89
      name: Dijon
      logo: https://media.api-sports.io/football/teams/89.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 26
      lineups: 19
      minutes: 1819
      number: null
      position: Midfielder
      rating: '6.792307'
      captain: false
    substitutes:
      in: 7
      out: 6
      bench: 7
    shots:
      total: 17
      'on': 5
    goals:
      total: 0
      conceded: 0
      assists: 5
      saves: null
    passes:
      total: 751
      key: 44
      accuracy: 23
    tackles:
      total: 9
      blocks: 1
      interceptions: 4
    duels:
      total: 129
      won: 41
    dribbles:
      attempts: 34
      success: 19
      past: null
    fouls:
      drawn: 12
      committed: 13
    cards:
      yellow: 4
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 2059
    name: W. Ben Yedder
    firstname: Wissam
    lastname: Ben Yedder
    age: 31
    birth:
      date: '1990-08-12'
      place: Sarcelles
      country: France
    nationality: France
    height: 170 cm
    weight: 68 kg
    injured: false
    photo: https://media.api-sports.io/football/players/2059.png
  statistics:
  - team:
      id: 91
      name: Monaco
      logo: https://media.api-sports.io/football/teams/91.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 29
      lineups: 27
      minutes: 2073
      number: null
      position: Attacker
      rating: '7.024137'
      captain: false
    substitutes:
      in: 2
      out: 20
      bench: 2
    shots:
      total: 45
      'on': 25
    goals:
      total: 13
      conceded: 0
      assists: 4
      saves: null
    passes:
      total: 661
      key: 30
      accuracy: 20
    tackles:
      total: 17
      blocks: 0
      interceptions: 11
    duels:
      total: 224
      won: 97
    dribbles:
      attempts: 49
      success: 23
      past: null
    fouls:
      drawn: 27
      committed: 7
    cards:
      yellow: 2
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 7
      missed: 1
      saved: null
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: players/topassists parameters: [] errors:   time: '2019-11-26T00:00:00+0...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/players/topassists"
params = {
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/players/topassists?season=2020&league=61", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /players/topyellowcards` — Top Yellow Cards

**Tags:** Players
**Operation ID:** `get-players-topyellowcards`

Get the 20 players with the most yellow cards for a league or cup.

**How it is calculated:**

* 1 : The player that received the higher number of yellow cards
* 2 : The player that received the higher number of red cards
* 3 : The player that assists in the higher number of matches
* 4 : The player that played the fewer minutes

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `league` | query | integer | yes | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | yes | The season of the league |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: players/topyellowcards
parameters:
  season: '2020'
  league: '61'
errors: []
results: 20
paging:
  current: 0
  total: 1
response:
- player:
    id: 8694
    name: W. Faes
    firstname: Wout
    lastname: Faes
    age: 23
    birth:
      date: '1998-04-03'
      place: null
      country: Belgium
    nationality: Belgium
    height: 187 cm
    weight: 84 kg
    injured: false
    photo: https://media.api-sports.io/football/players/8694.png
  statistics:
  - team:
      id: 93
      name: Reims
      logo: https://media.api-sports.io/football/teams/93.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 26
      lineups: 26
      minutes: 2292
      number: null
      position: Defender
      rating: '6.907692'
      captain: false
    substitutes:
      in: 0
      out: 0
      bench: 0
    shots:
      total: 5
      'on': 1
    goals:
      total: 1
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 1228
      key: 0
      accuracy: 43
    tackles:
      total: 25
      blocks: 24
      interceptions: 55
    duels:
      total: 164
      won: 95
    dribbles:
      attempts: 12
      success: 10
      past: null
    fouls:
      drawn: 12
      committed: 16
    cards:
      yellow: 10
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 1689
    name: Álvaro González
    firstname: Álvaro
    lastname: González Soberón
    age: 31
    birth:
      date: '1990-01-08'
      place: Potes
      country: Spain
    nationality: Spain
    height: 182 cm
    weight: 75 kg
    injured: false
    photo: https://media.api-sports.io/football/players/1689.png
  statistics:
  - team:
      id: 81
      name: Marseille
      logo: https://media.api-sports.io/football/teams/81.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 25
      lineups: 25
      minutes: 2204
      number: null
      position: Defender
      rating: '6.912000'
      captain: false
    substitutes:
      in: 0
      out: 3
      bench: 0
    shots:
      total: 9
      'on': 2
    goals:
      total: 1
      conceded: 0
      assists: 3
      saves: null
    passes:
      total: 1367
      key: 4
      accuracy: 47
    tackles:
      total: 25
      blocks: 12
      interceptions: 26
    duels:
      total: 160
      won: 91
    dribbles:
      attempts: 3
      success: 3
      past: null
    fouls:
      drawn: 23
      committed: 26
    cards:
      yellow: 10
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 6231
    name: F. Medina
    firstname: Facundo Axel
    lastname: Medina
    age: 22
    birth:
      date: '1999-05-28'
      place: Buenos Aires
      country: Argentina
    nationality: Argentina
    height: 180 cm
    weight: 78 kg
    injured: false
    photo: https://media.api-sports.io/football/players/6231.png
  statistics:
  - team:
      id: 116
      name: Lens
      logo: https://media.api-sports.io/football/teams/116.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 21
      lineups: 20
      minutes: 1769
      number: null
      position: Defender
      rating: '6.761904'
      captain: false
    substitutes:
      in: 1
      out: 1
      bench: 5
    shots:
      total: 7
      'on': 4
    goals:
      total: 2
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 1396
      key: 8
      accuracy: 58
    tackles:
      total: 34
      blocks: 7
      interceptions: 34
    duels:
      total: 154
      won: 71
    dribbles:
      attempts: 10
      success: 6
      past: null
    fouls:
      drawn: 7
      committed: 28
    cards:
      yellow: 9
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 21635
    name: J. Gradit
    firstname: Jonathan
    lastname: Gradit
    age: 29
    birth:
      date: '1992-11-24'
      place: Talence
      country: France
    nationality: France
    height: 180 cm
    weight: 75 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21635.png
  statistics:
  - team:
      id: 116
      name: Lens
      logo: https://media.api-sports.io/football/teams/116.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 26
      lineups: 26
      minutes: 2198
      number: null
      position: Defender
      rating: '6.904000'
      captain: false
    substitutes:
      in: 0
      out: 5
      bench: 1
    shots:
      total: 1
      'on': 0
    goals:
      total: 0
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 1303
      key: 4
      accuracy: 47
    tackles:
      total: 50
      blocks: 12
      interceptions: 41
    duels:
      total: 271
      won: 162
    dribbles:
      attempts: 35
      success: 24
      past: null
    fouls:
      drawn: 46
      committed: 41
    cards:
      yellow: 8
      yellowred: 1
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 20696
    name: P. Gueye
    firstname: Pape Alassane
    lastname: Gueye
    age: 22
    birth:
      date: '1999-01-24'
      place: Montreuil
      country: France
    nationality: France
    height: 187 cm
    weight: 65 kg
    injured: false
    photo: https://media.api-sports.io/football/players/20696.png
  statistics:
  - team:
      id: 81
      name: Marseille
      logo: https://media.api-sports.io/football/teams/81.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 25
      lineups: 16
      minutes: 1485
      number: null
      position: Midfielder
      rating: '6.684000'
      captain: false
    substitutes:
      in: 9
      out: 6
      bench: 11
    shots:
      total: 6
      'on': 2
    goals:
      total: 1
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 924
      key: 5
      accuracy: 30
    tackles:
      total: 39
      blocks: 5
      interceptions: 36
    duels:
      total: 216
      won: 106
    dribbles:
      attempts: 9
      success: 4
      past: null
    fouls:
      drawn: 30
      committed: 36
    cards:
      yellow: 8
      yellowred: 1
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 22004
    name: Moreto Cassamã
    firstname: Moreto Moro
    lastname: Cassamã
    age: 23
    birth:
      date: '1998-02-16'
      place: Bissau
      country: Portugal
    nationality: Guinea-Bissau
    height: 165 cm
    weight: 63 kg
    injured: false
    photo: https://media.api-sports.io/football/players/22004.png
  statistics:
  - team:
      id: 93
      name: Reims
      logo: https://media.api-sports.io/football/teams/93.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 23
      lineups: 20
      minutes: 1550
      number: null
      position: Midfielder
      rating: '6.760869'
      captain: false
    substitutes:
      in: 3
      out: 10
      bench: 5
    shots:
      total: 7
      'on': 2
    goals:
      total: 1
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 1005
      key: 10
      accuracy: 43
    tackles:
      total: 31
      blocks: 5
      interceptions: 33
    duels:
      total: 131
      won: 74
    dribbles:
      attempts: 24
      success: 22
      past: null
    fouls:
      drawn: 18
      committed: 22
    cards:
      yellow: 8
      yellowred: 0
      red: 2
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 1902
    name: D. Ćaleta-Car
    firstname: Duje
    lastname: Ćaleta-Car
    age: 25
    birth:
      date: '1996-09-17'
      place: Šibenik
      country: Croatia
    nationality: Croatia
    height: 192 cm
    weight: 89 kg
    injured: false
    photo: https://media.api-sports.io/football/players/1902.png
  statistics:
  - team:
      id: 81
      name: Marseille
      logo: https://media.api-sports.io/football/teams/81.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 28
      lineups: 27
      minutes: 2423
      number: null
      position: Defender
      rating: '6.985185'
      captain: false
    substitutes:
      in: 1
      out: 2
      bench: 1
    shots:
      total: 9
      'on': 3
    goals:
      total: 2
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 1558
      key: 4
      accuracy: 51
    tackles:
      total: 25
      blocks: 20
      interceptions: 39
    duels:
      total: 176
      won: 108
    dribbles:
      attempts: 2
      success: 2
      past: null
    fouls:
      drawn: 14
      committed: 26
    cards:
      yellow: 8
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 21504
    name: D. Ndong
    firstname: Didier
    lastname: Ndong Ibrahim
    age: 27
    birth:
      date: '1994-06-17'
      place: Lambaréné
      country: Gabon
    nationality: Gabon
    height: 179 cm
    weight: 75 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21504.png
  statistics:
  - team:
      id: 89
      name: Dijon
      logo: https://media.api-sports.io/football/teams/89.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 28
      lineups: 28
      minutes: 2520
      number: null
      position: Midfielder
      rating: '6.767857'
      captain: false
    substitutes:
      in: 0
      out: 0
      bench: 1
    shots:
      total: 6
      'on': 1
    goals:
      total: 0
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 1370
      key: 10
      accuracy: 46
    tackles:
      total: 52
      blocks: 7
      interceptions: 35
    duels:
      total: 247
      won: 114
    dribbles:
      attempts: 27
      success: 20
      past: null
    fouls:
      drawn: 17
      committed: 38
    cards:
      yellow: 8
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 20531
    name: H. Maïga
    firstname: Digbo G'nampa Habib
    lastname: Maïga
    age: 25
    birth:
      date: '1996-01-01'
      place: Gagnoa
      country: Côte d'Ivoire
    nationality: Côte d'Ivoire
    height: 181 cm
    weight: 80 kg
    injured: false
    photo: https://media.api-sports.io/football/players/20531.png
  statistics:
  - team:
      id: 112
      name: Metz
      logo: https://media.api-sports.io/football/teams/112.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 23
      lineups: 23
      minutes: 2006
      number: null
      position: Midfielder
      rating: '6.978260'
      captain: false
    substitutes:
      in: 0
      out: 3
      bench: 0
    shots:
      total: 16
      'on': 4
    goals:
      total: 1
      conceded: 0
      assists: 3
      saves: null
    passes:
      total: 969
      key: 24
      accuracy: 36
    tackles:
      total: 65
      blocks: 4
      interceptions: 43
    duels:
      total: 290
      won: 155
    dribbles:
      attempts: 40
      success: 29
      past: null
    fouls:
      drawn: 30
      committed: 45
    cards:
      yellow: 8
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 22143
    name: Y. Cahuzac
    firstname: Yannick
    lastname: Cahuzac
    age: 36
    birth:
      date: '1985-01-18'
      place: Ajaccio
      country: France
    nationality: France
    height: 178 cm
    weight: 72 kg
    injured: false
    photo: https://media.api-sports.io/football/players/22143.png
  statistics:
  - team:
      id: 116
      name: Lens
      logo: https://media.api-sports.io/football/teams/116.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 22
      lineups: 18
      minutes: 1561
      number: null
      position: Midfielder
      rating: '6.720000'
      captain: false
    substitutes:
      in: 4
      out: 6
      bench: 9
    shots:
      total: 3
      'on': 1
    goals:
      total: 1
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 627
      key: 9
      accuracy: 26
    tackles:
      total: 18
      blocks: 4
      interceptions: 24
    duels:
      total: 118
      won: 60
    dribbles:
      attempts: 4
      success: 3
      past: null
    fouls:
      drawn: 15
      committed: 22
    cards:
      yellow: 8
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 1271
    name: A. Tchouaméni
    firstname: Aurélien
    lastname: Tchouaméni
    age: 21
    birth:
      date: '2000-01-27'
      place: Rouen
      country: France
    nationality: France
    height: 185 cm
    weight: 80 kg
    injured: false
    photo: https://media.api-sports.io/football/players/1271.png
  statistics:
  - team:
      id: 91
      name: Monaco
      logo: https://media.api-sports.io/football/teams/91.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 29
      lineups: 29
      minutes: 2450
      number: null
      position: Midfielder
      rating: '7.175862'
      captain: false
    substitutes:
      in: 0
      out: 8
      bench: 0
    shots:
      total: 29
      'on': 10
    goals:
      total: 2
      conceded: 0
      assists: 2
      saves: null
    passes:
      total: 1420
      key: 15
      accuracy: 44
    tackles:
      total: 102
      blocks: 10
      interceptions: 50
    duels:
      total: 380
      won: 231
    dribbles:
      attempts: 30
      success: 19
      past: null
    fouls:
      drawn: 46
      committed: 49
    cards:
      yellow: 7
      yellowred: 1
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 22254
    name: Y. Fofana
    firstname: Youssouf
    lastname: Fofana
    age: 22
    birth:
      date: '1999-01-10'
      place: null
      country: France
    nationality: France
    height: 178 cm
    weight: null
    injured: false
    photo: https://media.api-sports.io/football/players/22254.png
  statistics:
  - team:
      id: 91
      name: Monaco
      logo: https://media.api-sports.io/football/teams/91.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 27
      lineups: 27
      minutes: 2204
      number: null
      position: Midfielder
      rating: '6.833333'
      captain: false
    substitutes:
      in: 0
      out: 7
      bench: 1
    shots:
      total: 16
      'on': 3
    goals:
      total: 0
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 1253
      key: 22
      accuracy: 43
    tackles:
      total: 78
      blocks: 3
      interceptions: 29
    duels:
      total: 265
      won: 137
    dribbles:
      attempts: 44
      success: 22
      past: null
    fouls:
      drawn: 26
      committed: 39
    cards:
      yellow: 7
      yellowred: 1
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 18764
    name: M. Schneiderlin
    firstname: Morgan
    lastname: Schneiderlin
    age: 32
    birth:
      date: '1989-11-08'
      place: Zellwiller
      country: France
    nationality: France
    height: 181 cm
    weight: 75 kg
    injured: false
    photo: https://media.api-sports.io/football/players/18764.png
  statistics:
  - team:
      id: 84
      name: Nice
      logo: https://media.api-sports.io/football/teams/84.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 22
      lineups: 19
      minutes: 1756
      number: null
      position: Midfielder
      rating: '6.890909'
      captain: false
    substitutes:
      in: 3
      out: 1
      bench: 5
    shots:
      total: 8
      'on': 3
    goals:
      total: 0
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 1250
      key: 10
      accuracy: 53
    tackles:
      total: 40
      blocks: 11
      interceptions: 44
    duels:
      total: 189
      won: 87
    dribbles:
      attempts: 16
      success: 12
      past: null
    fouls:
      drawn: 6
      committed: 37
    cards:
      yellow: 7
      yellowred: 1
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 20654
    name: F. Centonze
    firstname: Fabien
    lastname: Centonze
    age: 25
    birth:
      date: '1996-01-16'
      place: Voiron
      country: France
    nationality: France
    height: 182 cm
    weight: 75 kg
    injured: false
    photo: https://media.api-sports.io/football/players/20654.png
  statistics:
  - team:
      id: 112
      name: Metz
      logo: https://media.api-sports.io/football/teams/112.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 28
      lineups: 28
      minutes: 2502
      number: null
      position: Defender
      rating: '7.121428'
      captain: false
    substitutes:
      in: 0
      out: 1
      bench: 0
    shots:
      total: 13
      'on': 4
    goals:
      total: 0
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 971
      key: 19
      accuracy: 28
    tackles:
      total: 83
      blocks: 15
      interceptions: 90
    duels:
      total: 363
      won: 214
    dribbles:
      attempts: 80
      success: 44
      past: null
    fouls:
      drawn: 43
      committed: 32
    cards:
      yellow: 7
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 3339
    name: C. Doucouré
    firstname: Cheick Oumar
    lastname: Doucouré
    age: 21
    birth:
      date: '2000-01-08'
      place: Bamako
      country: Mali
    nationality: Mali
    height: 180 cm
    weight: 73 kg
    injured: false
    photo: https://media.api-sports.io/football/players/3339.png
  statistics:
  - team:
      id: 116
      name: Lens
      logo: https://media.api-sports.io/football/teams/116.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 26
      lineups: 23
      minutes: 2032
      number: null
      position: Midfielder
      rating: '7.080000'
      captain: false
    substitutes:
      in: 3
      out: 6
      bench: 5
    shots:
      total: 18
      'on': 5
    goals:
      total: 2
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 1093
      key: 22
      accuracy: 40
    tackles:
      total: 67
      blocks: 3
      interceptions: 38
    duels:
      total: 227
      won: 129
    dribbles:
      attempts: 37
      success: 31
      past: null
    fouls:
      drawn: 9
      committed: 36
    cards:
      yellow: 7
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 179843
    name: L. Gourna-Douath
    firstname: Lucas
    lastname: Gourna-Douath
    age: 18
    birth:
      date: '2003-08-05'
      place: null
      country: France
    nationality: France
    height: null
    weight: null
    injured: false
    photo: https://media.api-sports.io/football/players/179843.png
  statistics:
  - team:
      id: 1063
      name: Saint Etienne
      logo: https://media.api-sports.io/football/teams/1063.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 24
      lineups: 10
      minutes: 1031
      number: null
      position: Midfielder
      rating: '6.547619'
      captain: false
    substitutes:
      in: 14
      out: 5
      bench: 19
    shots:
      total: 3
      'on': null
    goals:
      total: 0
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 475
      key: 2
      accuracy: 18
    tackles:
      total: 27
      blocks: null
      interceptions: 21
    duels:
      total: 131
      won: 65
    dribbles:
      attempts: 8
      success: 4
      past: null
    fouls:
      drawn: 24
      committed: 27
    cards:
      yellow: 7
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 2198
    name: S. Doumbia
    firstname: Souleyman
    lastname: Doumbia
    age: 25
    birth:
      date: '1996-09-24'
      place: Paris
      country: France
    nationality: Côte d'Ivoire
    height: 177 cm
    weight: 73 kg
    injured: false
    photo: https://media.api-sports.io/football/players/2198.png
  statistics:
  - team:
      id: 77
      name: Angers
      logo: https://media.api-sports.io/football/teams/77.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 23
      lineups: 21
      minutes: 1918
      number: null
      position: Defender
      rating: '6.669565'
      captain: false
    substitutes:
      in: 2
      out: 2
      bench: 3
    shots:
      total: 7
      'on': 3
    goals:
      total: 0
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 780
      key: 12
      accuracy: 32
    tackles:
      total: 43
      blocks: 4
      interceptions: 39
    duels:
      total: 175
      won: 94
    dribbles:
      attempts: 32
      success: 20
      past: null
    fouls:
      drawn: 13
      committed: 26
    cards:
      yellow: 7
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 22005
    name: X. Chavalerin
    firstname: Xavier
    lastname: Chavalerin
    age: 30
    birth:
      date: '1991-03-07'
      place: Villeurbanne
      country: France
    nationality: France
    height: 178 cm
    weight: 66 kg
    injured: false
    photo: https://media.api-sports.io/football/players/22005.png
  statistics:
  - team:
      id: 93
      name: Reims
      logo: https://media.api-sports.io/football/teams/93.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 22
      lineups: 21
      minutes: 1743
      number: null
      position: Midfielder
      rating: '6.966666'
      captain: false
    substitutes:
      in: 1
      out: 3
      bench: 1
    shots:
      total: 13
      'on': 5
    goals:
      total: 0
      conceded: 0
      assists: 2
      saves: null
    passes:
      total: 626
      key: 15
      accuracy: 30
    tackles:
      total: 66
      blocks: 6
      interceptions: 25
    duels:
      total: 185
      won: 98
    dribbles:
      attempts: 19
      success: 13
      past: null
    fouls:
      drawn: 6
      committed: 31
    cards:
      yellow: 7
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 103
    name: J. Aholou
    firstname: Jean Eudès
    lastname: Aholou
    age: 27
    birth:
      date: '1994-03-20'
      place: Yopougnon
      country: Côte d'Ivoire
    nationality: Côte d'Ivoire
    height: 186 cm
    weight: 71 kg
    injured: false
    photo: https://media.api-sports.io/football/players/103.png
  statistics:
  - team:
      id: 95
      name: Strasbourg
      logo: https://media.api-sports.io/football/teams/95.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 20
      lineups: 19
      minutes: 1561
      number: null
      position: Midfielder
      rating: '6.550000'
      captain: false
    substitutes:
      in: 1
      out: 9
      bench: 1
    shots:
      total: 2
      'on': 1
    goals:
      total: 2
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 7
      key: 0
      accuracy: 62
    tackles:
      total: 1
      blocks: 0
      interceptions: 1
    duels:
      total: 5
      won: 3
    dribbles:
      attempts: 0
      success: 0
      past: null
    fouls:
      drawn: 1
      committed: 0
    cards:
      yellow: 7
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 4399
    name: H. Boudaoui
    firstname: Hichem
    lastname: Boudaoui
    age: 22
    birth:
      date: '1999-09-23'
      place: Béchar
      country: Algeria
    nationality: Algeria
    height: 175 cm
    weight: 61 kg
    injured: false
    photo: https://media.api-sports.io/football/players/4399.png
  statistics:
  - team:
      id: 84
      name: Nice
      logo: https://media.api-sports.io/football/teams/84.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 19
      lineups: 17
      minutes: 1327
      number: null
      position: Midfielder
      rating: '6.731578'
      captain: false
    substitutes:
      in: 2
      out: 12
      bench: 3
    shots:
      total: 9
      'on': 5
    goals:
      total: 1
      conceded: 0
      assists: 2
      saves: null
    passes:
      total: 648
      key: 7
      accuracy: 28
    tackles:
      total: 44
      blocks: 3
      interceptions: 21
    duels:
      total: 200
      won: 93
    dribbles:
      attempts: 29
      success: 18
      past: null
    fouls:
      drawn: 19
      committed: 23
    cards:
      yellow: 7
      yellowred: 0
      red: 0
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: players/topyellowcards parameters: [] errors:   time: '2019-11-26T00:00:...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/players/topyellowcards"
params = {
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/players/topyellowcards?season=2020&league=61", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /players/topredcards` — Top Red Cards

**Tags:** Players
**Operation ID:** `get-players-topredcards`

Get the 20 players with the most red cards for a league or cup.

**How it is calculated:**

* 1 : The player that received the higher number of red cards
* 2 : The player that received the higher number of yellow cards
* 3 : The player that assists in the higher number of matches
* 4 : The player that played the fewer minutes

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `league` | query | integer | yes | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | yes | The season of the league |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: players/topredcards
parameters:
  season: '2020'
  league: '61'
errors: []
results: 20
paging:
  current: 0
  total: 1
response:
- player:
    id: 22004
    name: Moreto Cassamã
    firstname: Moreto Moro
    lastname: Cassamã
    age: 23
    birth:
      date: '1998-02-16'
      place: Bissau
      country: Portugal
    nationality: Guinea-Bissau
    height: 165 cm
    weight: 63 kg
    injured: false
    photo: https://media.api-sports.io/football/players/22004.png
  statistics:
  - team:
      id: 93
      name: Reims
      logo: https://media.api-sports.io/football/teams/93.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 23
      lineups: 20
      minutes: 1550
      number: null
      position: Midfielder
      rating: '6.760869'
      captain: false
    substitutes:
      in: 3
      out: 10
      bench: 5
    shots:
      total: 7
      'on': 2
    goals:
      total: 1
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 1005
      key: 10
      accuracy: 43
    tackles:
      total: 31
      blocks: 5
      interceptions: 33
    duels:
      total: 131
      won: 74
    dribbles:
      attempts: 24
      success: 22
      past: null
    fouls:
      drawn: 18
      committed: 22
    cards:
      yellow: 8
      yellowred: 0
      red: 2
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 21998
    name: A. Disasi
    firstname: Axel
    lastname: Disasi
    age: 23
    birth:
      date: '1998-03-11'
      place: Gonesse
      country: France
    nationality: France
    height: 190 cm
    weight: 86 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21998.png
  statistics:
  - team:
      id: 91
      name: Monaco
      logo: https://media.api-sports.io/football/teams/91.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 22
      lineups: 19
      minutes: 1602
      number: null
      position: Defender
      rating: '6.747619'
      captain: false
    substitutes:
      in: 3
      out: 3
      bench: 8
    shots:
      total: 13
      'on': 6
    goals:
      total: 3
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 1180
      key: 4
      accuracy: 47
    tackles:
      total: 21
      blocks: 10
      interceptions: 21
    duels:
      total: 143
      won: 77
    dribbles:
      attempts: 8
      success: 5
      past: null
    fouls:
      drawn: 12
      committed: 21
    cards:
      yellow: 4
      yellowred: 0
      red: 2
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 1912
    name: D. Payet
    firstname: Dimitri
    lastname: Payet
    age: 34
    birth:
      date: '1987-03-29'
      place: Saint-Pierre
      country: Réunion
    nationality: France
    height: 175 cm
    weight: 77 kg
    injured: false
    photo: https://media.api-sports.io/football/players/1912.png
  statistics:
  - team:
      id: 81
      name: Marseille
      logo: https://media.api-sports.io/football/teams/81.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 25
      lineups: 20
      minutes: 1716
      number: null
      position: Midfielder
      rating: '6.956000'
      captain: false
    substitutes:
      in: 5
      out: 11
      bench: 5
    shots:
      total: 21
      'on': 9
    goals:
      total: 4
      conceded: 0
      assists: 4
      saves: null
    passes:
      total: 816
      key: 45
      accuracy: 25
    tackles:
      total: 17
      blocks: 2
      interceptions: 4
    duels:
      total: 156
      won: 81
    dribbles:
      attempts: 46
      success: 28
      past: null
    fouls:
      drawn: 32
      committed: 11
    cards:
      yellow: 3
      yellowred: 0
      red: 2
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 1
      saved: null
- player:
    id: 21571
    name: Hilton
    firstname: Vitorino
    lastname: Hilton da Silva
    age: 44
    birth:
      date: '1977-09-13'
      place: Brasília
      country: Brazil
    nationality: Brazil
    height: 180 cm
    weight: 78 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21571.png
  statistics:
  - team:
      id: 82
      name: Montpellier
      logo: https://media.api-sports.io/football/teams/82.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 22
      lineups: 18
      minutes: 1537
      number: null
      position: Defender
      rating: '6.588888'
      captain: false
    substitutes:
      in: 4
      out: 0
      bench: 7
    shots:
      total: 10
      'on': 3
    goals:
      total: 0
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 808
      key: null
      accuracy: 33
    tackles:
      total: 10
      blocks: 19
      interceptions: 27
    duels:
      total: 91
      won: 49
    dribbles:
      attempts: 1
      success: 1
      past: null
    fouls:
      drawn: 10
      committed: 15
    cards:
      yellow: 3
      yellowred: 0
      red: 2
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 2478
    name: D. Benedetto
    firstname: Darío Ismael
    lastname: Benedetto
    age: 31
    birth:
      date: '1990-05-17'
      place: Berazategui
      country: Argentina
    nationality: Argentina
    height: 177 cm
    weight: 75 kg
    injured: false
    photo: https://media.api-sports.io/football/players/2478.png
  statistics:
  - team:
      id: 81
      name: Marseille
      logo: https://media.api-sports.io/football/teams/81.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 26
      lineups: 18
      minutes: 1484
      number: null
      position: Attacker
      rating: '6.553846'
      captain: false
    substitutes:
      in: 8
      out: 15
      bench: 8
    shots:
      total: 32
      'on': 13
    goals:
      total: 4
      conceded: 0
      assists: 3
      saves: null
    passes:
      total: 310
      key: 13
      accuracy: 9
    tackles:
      total: 5
      blocks: 2
      interceptions: 3
    duels:
      total: 164
      won: 56
    dribbles:
      attempts: 15
      success: 9
      past: null
    fouls:
      drawn: 19
      committed: 17
    cards:
      yellow: 2
      yellowred: 1
      red: 1
    penalty:
      won: null
      commited: null
      scored: 1
      missed: 0
      saved: null
- player:
    id: 21433
    name: F. Miguel
    firstname: Florian
    lastname: Miguel
    age: 25
    birth:
      date: '1996-09-01'
      place: Brugge
      country: France
    nationality: France
    height: 179 cm
    weight: 70 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21433.png
  statistics:
  - team:
      id: 92
      name: Nimes
      logo: https://media.api-sports.io/football/teams/92.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 19
      lineups: 16
      minutes: 1357
      number: null
      position: Defender
      rating: '6.783333'
      captain: false
    substitutes:
      in: 3
      out: 2
      bench: 10
    shots:
      total: 6
      'on': 3
    goals:
      total: 0
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 714
      key: 1
      accuracy: 35
    tackles:
      total: 13
      blocks: 12
      interceptions: 40
    duels:
      total: 125
      won: 71
    dribbles:
      attempts: 4
      success: 3
      past: null
    fouls:
      drawn: 29
      committed: 14
    cards:
      yellow: 2
      yellowred: 1
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 7
    name: A. Diallo
    firstname: Abdou
    lastname: Diallo
    age: 25
    birth:
      date: '1996-05-04'
      place: Tours
      country: France
    nationality: Senegal
    height: 187 cm
    weight: 79 kg
    injured: false
    photo: https://media.api-sports.io/football/players/7.png
  statistics:
  - team:
      id: 85
      name: Paris Saint Germain
      logo: https://media.api-sports.io/football/teams/85.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 18
      lineups: 14
      minutes: 1209
      number: null
      position: Defender
      rating: '7.005882'
      captain: false
    substitutes:
      in: 4
      out: 1
      bench: 8
    shots:
      total: 3
      'on': null
    goals:
      total: 0
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 951
      key: 1
      accuracy: 49
    tackles:
      total: 12
      blocks: 8
      interceptions: 22
    duels:
      total: 92
      won: 55
    dribbles:
      attempts: 20
      success: 14
      past: null
    fouls:
      drawn: 8
      committed: 15
    cards:
      yellow: 1
      yellowred: 1
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 8694
    name: W. Faes
    firstname: Wout
    lastname: Faes
    age: 23
    birth:
      date: '1998-04-03'
      place: null
      country: Belgium
    nationality: Belgium
    height: 187 cm
    weight: 84 kg
    injured: false
    photo: https://media.api-sports.io/football/players/8694.png
  statistics:
  - team:
      id: 93
      name: Reims
      logo: https://media.api-sports.io/football/teams/93.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 26
      lineups: 26
      minutes: 2292
      number: null
      position: Defender
      rating: '6.907692'
      captain: false
    substitutes:
      in: 0
      out: 0
      bench: 0
    shots:
      total: 5
      'on': 1
    goals:
      total: 1
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 1228
      key: 0
      accuracy: 43
    tackles:
      total: 25
      blocks: 24
      interceptions: 55
    duels:
      total: 164
      won: 95
    dribbles:
      attempts: 12
      success: 10
      past: null
    fouls:
      drawn: 12
      committed: 16
    cards:
      yellow: 10
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 1907
    name: H. Sakai
    firstname: Hiroki
    lastname: Sakai
    age: 31
    birth:
      date: '1990-04-12'
      place: Kashiwa
      country: Japan
    nationality: Japan
    height: 183 cm
    weight: 70 kg
    injured: false
    photo: https://media.api-sports.io/football/players/1907.png
  statistics:
  - team:
      id: 81
      name: Marseille
      logo: https://media.api-sports.io/football/teams/81.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 25
      lineups: 23
      minutes: 2087
      number: null
      position: Defender
      rating: '6.776000'
      captain: false
    substitutes:
      in: 2
      out: 4
      bench: 3
    shots:
      total: 1
      'on': 0
    goals:
      total: 0
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 926
      key: 18
      accuracy: 31
    tackles:
      total: 71
      blocks: 4
      interceptions: 50
    duels:
      total: 250
      won: 133
    dribbles:
      attempts: 21
      success: 7
      past: null
    fouls:
      drawn: 15
      committed: 41
    cards:
      yellow: 6
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 21443
    name: T. Savanier
    firstname: Téji
    lastname: Savanier
    age: 30
    birth:
      date: '1991-12-22'
      place: Montpellier
      country: France
    nationality: France
    height: 171 cm
    weight: 62 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21443.png
  statistics:
  - team:
      id: 82
      name: Montpellier
      logo: https://media.api-sports.io/football/teams/82.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 22
      lineups: 21
      minutes: 1738
      number: null
      position: Midfielder
      rating: '7.100000'
      captain: false
    substitutes:
      in: 1
      out: 8
      bench: 1
    shots:
      total: 33
      'on': 15
    goals:
      total: 5
      conceded: 0
      assists: 4
      saves: null
    passes:
      total: 850
      key: 49
      accuracy: 30
    tackles:
      total: 39
      blocks: 4
      interceptions: 32
    duels:
      total: 322
      won: 149
    dribbles:
      attempts: 70
      success: 41
      past: null
    fouls:
      drawn: 54
      committed: 45
    cards:
      yellow: 6
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 2
      missed: 2
      saved: null
- player:
    id: 941
    name: L. Benito
    firstname: Loris
    lastname: Benito Souto
    age: 29
    birth:
      date: '1992-01-07'
      place: Aarau
      country: Switzerland
    nationality: Switzerland
    height: 184 cm
    weight: 80 kg
    injured: false
    photo: https://media.api-sports.io/football/players/941.png
  statistics:
  - team:
      id: 78
      name: Bordeaux
      logo: https://media.api-sports.io/football/teams/78.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 25
      lineups: 24
      minutes: 2113
      number: null
      position: Defender
      rating: '6.828000'
      captain: false
    substitutes:
      in: 1
      out: 2
      bench: 4
    shots:
      total: 6
      'on': 1
    goals:
      total: 0
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 1240
      key: 11
      accuracy: 45
    tackles:
      total: 35
      blocks: 7
      interceptions: 39
    duels:
      total: 158
      won: 84
    dribbles:
      attempts: 2
      success: 2
      past: null
    fouls:
      drawn: 13
      committed: 32
    cards:
      yellow: 5
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 22232
    name: Thiago Mendes
    firstname: Thiago Henrique
    lastname: Mendes Ribeiro
    age: 29
    birth:
      date: '1992-03-15'
      place: São Luís
      country: Brazil
    nationality: Brazil
    height: 176 cm
    weight: 78 kg
    injured: false
    photo: https://media.api-sports.io/football/players/22232.png
  statistics:
  - team:
      id: 80
      name: Lyon
      logo: https://media.api-sports.io/football/teams/80.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 23
      lineups: 19
      minutes: 1813
      number: null
      position: Midfielder
      rating: '6.956521'
      captain: false
    substitutes:
      in: 4
      out: 2
      bench: 5
    shots:
      total: 15
      'on': 6
    goals:
      total: 0
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 1220
      key: 22
      accuracy: 46
    tackles:
      total: 32
      blocks: 6
      interceptions: 32
    duels:
      total: 157
      won: 84
    dribbles:
      attempts: 17
      success: 11
      past: null
    fouls:
      drawn: 20
      committed: 22
    cards:
      yellow: 5
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 3080
    name: M. Munetsi
    firstname: Marshall Nyasha
    lastname: Munetsi
    age: 25
    birth:
      date: '1996-06-22'
      place: Bulawayo
      country: Zimbabwe
    nationality: Zimbabwe
    height: 188 cm
    weight: 83 kg
    injured: false
    photo: https://media.api-sports.io/football/players/3080.png
  statistics:
  - team:
      id: 93
      name: Reims
      logo: https://media.api-sports.io/football/teams/93.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 21
      lineups: 15
      minutes: 1386
      number: null
      position: Midfielder
      rating: '6.828571'
      captain: false
    substitutes:
      in: 6
      out: 3
      bench: 9
    shots:
      total: 9
      'on': 3
    goals:
      total: 1
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 587
      key: 7
      accuracy: 30
    tackles:
      total: 27
      blocks: 17
      interceptions: 51
    duels:
      total: 163
      won: 93
    dribbles:
      attempts: 17
      success: 12
      past: null
    fouls:
      drawn: 15
      committed: 23
    cards:
      yellow: 5
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 3416
    name: J. Boye
    firstname: John
    lastname: Boye
    age: 34
    birth:
      date: '1987-04-23'
      place: Accra
      country: Ghana
    nationality: Ghana
    height: 184 cm
    weight: 73 kg
    injured: false
    photo: https://media.api-sports.io/football/players/3416.png
  statistics:
  - team:
      id: 112
      name: Metz
      logo: https://media.api-sports.io/football/teams/112.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 28
      lineups: 28
      minutes: 2456
      number: null
      position: Defender
      rating: '6.885714'
      captain: false
    substitutes:
      in: 0
      out: 3
      bench: 0
    shots:
      total: 9
      'on': 1
    goals:
      total: 1
      conceded: 0
      assists: 2
      saves: null
    passes:
      total: 980
      key: 6
      accuracy: 30
    tackles:
      total: 39
      blocks: 18
      interceptions: 61
    duels:
      total: 188
      won: 99
    dribbles:
      attempts: 3
      success: 3
      past: null
    fouls:
      drawn: 13
      committed: 23
    cards:
      yellow: 4
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 21711
    name: F. Sammaritano
    firstname: Frédéric
    lastname: Sammaritano
    age: 35
    birth:
      date: '1986-03-23'
      place: Vannes
      country: France
    nationality: France
    height: 162 cm
    weight: 65 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21711.png
  statistics:
  - team:
      id: 89
      name: Dijon
      logo: https://media.api-sports.io/football/teams/89.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 24
      lineups: 9
      minutes: 941
      number: null
      position: Midfielder
      rating: '6.604166'
      captain: false
    substitutes:
      in: 15
      out: 9
      bench: 18
    shots:
      total: 8
      'on': 3
    goals:
      total: 0
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 322
      key: 20
      accuracy: 17
    tackles:
      total: 15
      blocks: 0
      interceptions: 9
    duels:
      total: 107
      won: 49
    dribbles:
      attempts: 23
      success: 14
      past: null
    fouls:
      drawn: 18
      committed: 12
    cards:
      yellow: 4
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 21499
    name: L. Deaux
    firstname: Lucas
    lastname: Deaux
    age: 33
    birth:
      date: '1988-12-26'
      place: Reims
      country: France
    nationality: France
    height: 188 cm
    weight: 82 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21499.png
  statistics:
  - team:
      id: 92
      name: Nimes
      logo: https://media.api-sports.io/football/teams/92.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 17
      lineups: 15
      minutes: 1347
      number: null
      position: Midfielder
      rating: '6.629411'
      captain: false
    substitutes:
      in: 2
      out: 2
      bench: 3
    shots:
      total: 10
      'on': 4
    goals:
      total: 1
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 739
      key: 13
      accuracy: 41
    tackles:
      total: 30
      blocks: 3
      interceptions: 16
    duels:
      total: 178
      won: 90
    dribbles:
      attempts: 23
      success: 16
      past: null
    fouls:
      drawn: 15
      committed: 25
    cards:
      yellow: 4
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 6
    name: L. Balerdi
    firstname: Leonardo Julián
    lastname: Balerdi Rossa
    age: 22
    birth:
      date: '1999-01-26'
      place: Villa Mercedes
      country: Argentina
    nationality: Argentina
    height: 187 cm
    weight: 85 kg
    injured: false
    photo: https://media.api-sports.io/football/players/6.png
  statistics:
  - team:
      id: 81
      name: Marseille
      logo: https://media.api-sports.io/football/teams/81.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 13
      lineups: 12
      minutes: 1004
      number: null
      position: Defender
      rating: '6.476923'
      captain: false
    substitutes:
      in: 1
      out: 1
      bench: 16
    shots:
      total: 8
      'on': 2
    goals:
      total: 1
      conceded: 0
      assists: null
      saves: null
    passes:
      total: 561
      key: 0
      accuracy: 41
    tackles:
      total: 14
      blocks: 6
      interceptions: 16
    duels:
      total: 114
      won: 48
    dribbles:
      attempts: 5
      success: 2
      past: null
    fouls:
      drawn: 13
      committed: 21
    cards:
      yellow: 4
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 276
    name: Neymar
    firstname: Neymar
    lastname: da Silva Santos Júnior
    age: 29
    birth:
      date: '1992-02-05'
      place: Mogi das Cruzes
      country: Brazil
    nationality: Brazil
    height: 175 cm
    weight: 68 kg
    injured: false
    photo: https://media.api-sports.io/football/players/276.png
  statistics:
  - team:
      id: 85
      name: Paris Saint Germain
      logo: https://media.api-sports.io/football/teams/85.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 11
      lineups: 9
      minutes: 865
      number: null
      position: Attacker
      rating: '7.490909'
      captain: false
    substitutes:
      in: 2
      out: 0
      bench: 2
    shots:
      total: 32
      'on': 14
    goals:
      total: 6
      conceded: 0
      assists: 3
      saves: null
    passes:
      total: 552
      key: 32
      accuracy: 39
    tackles:
      total: 8
      blocks: null
      interceptions: 6
    duels:
      total: 216
      won: 111
    dribbles:
      attempts: 99
      success: 57
      past: null
    fouls:
      drawn: 43
      committed: 17
    cards:
      yellow: 4
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 3
      missed: 0
      saved: null
- player:
    id: 21097
    name: Andrei Girotto
    firstname: Andrei
    lastname: Girotto
    age: 29
    birth:
      date: '1992-02-17'
      place: Bento Gonçalves
      country: Brazil
    nationality: Brazil
    height: 186 cm
    weight: 73 kg
    injured: false
    photo: https://media.api-sports.io/football/players/21097.png
  statistics:
  - team:
      id: 83
      name: Nantes
      logo: https://media.api-sports.io/football/teams/83.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 27
      lineups: 26
      minutes: 2282
      number: null
      position: Midfielder
      rating: '6.844444'
      captain: false
    substitutes:
      in: 1
      out: 0
      bench: 1
    shots:
      total: 20
      'on': 5
    goals:
      total: 1
      conceded: 0
      assists: 1
      saves: null
    passes:
      total: 1278
      key: 10
      accuracy: 40
    tackles:
      total: 58
      blocks: 11
      interceptions: 50
    duels:
      total: 254
      won: 157
    dribbles:
      attempts: 5
      success: 3
      past: null
    fouls:
      drawn: 21
      committed: 25
    cards:
      yellow: 3
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: null
- player:
    id: 20519
    name: A. Oukidja
    firstname: Alexandre
    lastname: Oukidja
    age: 33
    birth:
      date: '1988-07-19'
      place: Nevers
      country: France
    nationality: Algeria
    height: 184 cm
    weight: 79 kg
    injured: false
    photo: https://media.api-sports.io/football/players/20519.png
  statistics:
  - team:
      id: 112
      name: Metz
      logo: https://media.api-sports.io/football/teams/112.png
    league:
      id: 61
      name: Ligue 1
      country: France
      logo: https://media.api-sports.io/football/leagues/61.png
      flag: https://media.api-sports.io/flags/fr.svg
      season: 2020
    games:
      appearences: 27
      lineups: 27
      minutes: 2430
      number: null
      position: Goalkeeper
      rating: '6.922222'
      captain: false
    substitutes:
      in: 0
      out: 1
      bench: 0
    shots:
      total: 0
      'on': 0
    goals:
      total: 0
      conceded: 26
      assists: null
      saves: 69
    passes:
      total: 685
      key: 1
      accuracy: 16
    tackles:
      total: null
      blocks: 0
      interceptions: 0
    duels:
      total: 24
      won: 20
    dribbles:
      attempts: 2
      success: 2
      past: null
    fouls:
      drawn: 6
      committed: 0
    cards:
      yellow: 3
      yellowred: 0
      red: 1
    penalty:
      won: null
      commited: null
      scored: 0
      missed: 0
      saved: 2
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: players/topredcards parameters: [] errors:   time: '2019-11-26T00:00:00+...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/players/topredcards"
params = {
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/players/topredcards?season=2020&league=61", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /transfers` — Transfers

**Tags:** Transfers
**Operation ID:** `get-transfers`

Get all available transfers for players and teams

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `player` | query | integer | no | The id of the player |
| `team` | query | integer | no | The id of the team |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: transfers
parameters:
  player: '35845'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- player:
    id: 35845
    name: Hernán Darío Burbano
  update: '2020-02-06T00:08:15+00:00'
  transfers:
  - date: '2019-07-15'
    type: Free
    teams:
      in:
        id: 2283
        name: Atlas
        logo: https://media.api-sports.io/football/teams/2283.png
      out:
        id: 2283
        name: Atlas
        logo: https://media.api-sports.io/football/teams/2283.png
  - date: '2019-01-01'
    type: N/A
    teams:
      in:
        id: 1937
        name: Atletico Atlas
        logo: https://media.api-sports.io/football/teams/1937.png
      out:
        id: 1139
        name: Santa Fe
        logo: https://media.api-sports.io/football/teams/1139.png
  - date: '2018-07-01'
    type: N/A
    teams:
      in:
        id: 1139
        name: Santa Fe
        logo: https://media.api-sports.io/football/teams/1139.png
      out:
        id: 2289
        name: Leon
        logo: https://media.api-sports.io/football/teams/2289.png
  - date: '2015-06-11'
    type: N/A
    teams:
      in:
        id: 2289
        name: Leon
        logo: https://media.api-sports.io/football/teams/2289.png
      out:
        id: 2279
        name: Tigres UANL
        logo: https://media.api-sports.io/football/teams/2279.png
  - date: '2014-01-01'
    type: N/A
    teams:
      in:
        id: 2279
        name: Tigres UANL
        logo: https://media.api-sports.io/football/teams/2279.png
      out:
        id: 2289
        name: Leon
        logo: https://media.api-sports.io/football/teams/2289.png
  - date: '2012-01-01'
    type: N/A
    teams:
      in:
        id: 2289
        name: Leon
        logo: https://media.api-sports.io/football/teams/2289.png
      out:
        id: 1127
        name: Deportivo Cali
        logo: https://media.api-sports.io/football/teams/1127.png
  - date: '2011-01-01'
    type: N/A
    teams:
      in:
        id: 1127
        name: Deportivo Cali
        logo: https://media.api-sports.io/football/teams/1127.png
      out:
        id: 1126
        name: Deportivo Pasto
        logo: https://media.api-sports.io/football/teams/1126.png
  - date: '2020-01-01'
    type: null
    teams:
      in:
        id: 1470
        name: Cucuta
        logo: https://media.api-sports.io/football/teams/1470.png
      out:
        id: 463
        name: Aldosivi
        logo: https://media.api-sports.io/football/teams/463.png
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: transfers parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   b...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/transfers"
params = {
    "player": '<player>',  # The id of the player
    "team": '<team>',  # The id of the team
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/transfers?player=35845", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /trophies` — Trophies

**Tags:** Trophies
**Operation ID:** `get-trophies`

Get all available trophies for a player or a coach.

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `player` | query | integer | no | The id of the player |
| `players` | query | string enum: id-id-id pattern: Maximum of 20 players ids | no | One or more players ids |
| `coach` | query | integer | no | The id of the coach |
| `coachs` | query | string enum: id-id-id pattern: Maximum of 20 coachs ids | no | One or more coachs ids |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`Default`):
```json
get: trophies
parameters:
  player: '276'
errors: []
results: 38
paging:
  current: 1
  total: 1
response:
- league: Sudamericano U20
  country: South-America
  season: Peru 2011
  place: Winner
- league: Trophée des Champions
  country: France
  season: 2019/2020
  place: Winner
- league: Copa America
  country: South-America
  season: 2019 Brazil
  place: Winner
- league: Ligue 1
  country: France
  season: 2018/2019
  place: Winner
- league: Coupe de France
  country: France
  season: 2018/2019
  place: 2nd Place
- league: Trophée des Champions
  country: France
  season: 2018/2019
  place: Winner
- league: Ligue 1
  country: France
  season: 2017/2018
  place: Winner
- league: Coupe de France
  country: France
  season: 2017/2018
  place: Winner
- league: Coupe de la Ligue
  country: France
  season: 2017/2018
  place: Winner
- league: La Liga
  country: Spain
  season: 2016/2017
  place: 2nd Place
```

**Example** (`With players or Coachs parameter`):
```json
get: trophies
parameters:
  players: 276-278
errors: []
results: 2
paging:
  current: 1
  total: 1
response:
- id: 276
  trophies:
  - league: La Liga
    country: Spain
    season: 2015/2016
    place: Winner
  - league: La Liga
    country: Spain
    season: 2014/2015
    place: Winner
  - league: La Liga
    country: Spain
    season: 2016/2017
    place: 2nd Place
  - league: Ligue 1
    country: France
    season: 2022/2023
    place: Winner
- id: 278
  trophies:
  - league: FIFA World Cup
    country: World
    season: 2018 Russia
    place: Winner
  - league: FIFA World Cup
    country: World
    season: 2022 Qatar
    place: 2nd Place
  - league: Ligue 1
    country: France
    season: 2023/2024
    place: Winner
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: trophies parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   bu...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/trophies"
params = {
    "player": '<player>',  # The id of the player
    "players": '<players>',  # One or more players ids
    "coach": '<coach>',  # The id of the coach
    "coachs": '<coachs>',  # One or more coachs ids
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/trophies?player=276", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /sidelined` — Sidelined

**Tags:** Sidelined
**Operation ID:** `get-sidelined`

Get all available sidelined for a player or a coach.

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `player` | query | integer | no | The id of the player |
| `players` | query | string enum: id-id-id pattern: Maximum of 20 players ids | no | One or more players ids |
| `coach` | query | integer | no | The id of the coach |
| `coachs` | query | string enum: id-id-id pattern: Maximum of 20 coachs ids | no | One or more coachs ids |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`Default`):
```json
get: sidelined
parameters:
  player: '276'
errors: []
results: 27
paging:
  current: 1
  total: 1
response:
- type: Suspended
  start: '2020-02-26'
  end: '2020-03-01'
- type: Hip/Thigh Injury
  start: '2020-02-02'
  end: '2020-02-10'
- type: Groin/Pelvis Injury
  start: '2019-10-11'
  end: '2019-11-20'
- type: Ankle/Foot Injury
  start: '2019-08-01'
  end: '2019-08-23'
- type: Suspended
  start: '2019-05-15'
  end: '2019-05-27'
- type: Ankle/Foot Injury
  start: '2019-01-24'
  end: '2019-04-20'
- type: Groin Strain
  start: '2018-12-03'
  end: '2019-01-02'
- type: Groin Strain
  start: '2018-11-21'
  end: '2018-11-27'
- type: Broken Toe
  start: '2018-02-26'
  end: '2018-05-20'
- type: Thigh Muscle Strain
  start: '2018-01-20'
  end: '2018-01-25'
- type: Rib Injury
  start: '2018-01-11'
  end: '2018-01-16'
- type: Suspended
  start: '2017-12-05'
  end: '2017-12-11'
- type: Thigh Muscle Strain
  start: '2017-11-03'
  end: '2017-11-15'
- type: Suspended
  start: '2017-10-23'
  end: '2017-10-28'
- type: Ankle/Foot Injury
  start: '2017-09-21'
  end: '2017-09-25'
- type: Suspended
  start: '2017-04-09'
  end: '2017-04-27'
- type: Suspended
  start: '2016-12-04'
  end: '2016-12-11'
- type: Suspended
  start: '2016-03-04'
  end: '2016-03-07'
- type: Hamstring
  start: '2016-01-21'
  end: '2016-01-26'
- type: Hamstring
  start: '2015-12-08'
  end: '2015-12-16'
- type: Virus
  start: '2015-08-09'
  end: '2015-08-26'
- type: Suspended
  start: '2015-03-01'
  end: '2015-03-09'
- type: Sprained Ankle
  start: '2014-08-22'
  end: '2014-08-29'
- type: Vertebral Fracture
  start: '2014-07-05'
  end: '2014-08-05'
- type: Ankle/Foot Injury
  start: '2014-04-17'
  end: '2014-05-10'
- type: Sprained Ankle
  start: '2014-01-17'
  end: '2014-02-14'
- type: Suspended
  start: '2013-12-15'
  end: '2013-12-23'
```

**Example** (`With players or Coachs parameter`):
```json
get: sidelined
parameters:
  players: 276-278
errors: []
results: 2
paging:
  current: 1
  total: 1
response:
- id: 276
  sidelined:
  - type: Virus
    start: '2023-08-10'
    end: '2023-08-15'
  - type: Ankle Injury
    start: '2023-02-20'
    end: '2023-06-30'
  - type: Groin Injury
    start: '2023-01-31'
    end: '2023-02-07'
  - type: Suspended
    start: '2022-12-29'
    end: '2023-01-03'
  - type: Ankle/Foot Injury
    start: '2022-11-25'
    end: '2022-12-03'
- id: 278
  sidelined:
  - type: Unknown
    start: '2024-11-28'
    end: '2024-11-29'
  - type: Hamstring
    start: '2024-09-25'
    end: '2024-09-30'
  - type: Broken Nose
    start: '2024-06-18'
    end: '2024-06-19'
  - type: Virus
    start: '2024-06-13'
    end: '2024-06-14'
  - type: Thigh Injury
    start: '2023-02-02'
    end: '2023-02-13'
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: sidelined parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   b...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/sidelined"
params = {
    "player": '<player>',  # The id of the player
    "players": '<players>',  # One or more players ids
    "coach": '<coach>',  # The id of the coach
    "coachs": '<coachs>',  # One or more coachs ids
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/sidelined?player=276", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /odds/live` — odds/live

**Tags:** Odds (In-Play)
**Operation ID:** `get-odds-live`

This endpoint returns in-play odds for fixtures in progress.

Fixtures are added between 15 and 5 minutes before the start of the fixture. Once the fixture is over they are removed from the endpoint between 5 and 20 minutes. **No history is stored**. So fixtures that are about to start, fixtures in progress and fixtures that have just ended are available in this endpoint.

**Update Frequency** : This endpoint is updated every 5 seconds.`*`

`* This value can change in the range of 5 to 60 seconds`

**INFORMATIONS ABOUT STATUS**
```
"status": {
    "stopped": false, // True if the fixture is stopped by the referee for X reason
    "blocked": false, // True if bets on this fixture are temporarily blocked
    "finished": false // True if the fixture has not started or if it is finished
},
```

**INFORMATIONS ABOUT VALUES**

When several identical values exist for the same bet the `main` field is set to `True` for the bet being considered, the others will have the value `False`.

The `main` field will be set to `True` only if several identical values exist for the same bet.

When a value is unique for a bet the `main` value will always be `False` or `null`.

**Example below** :
```
"id": 36,
"name": "Over/Under Line",
"values": [
    {
        "value": "Over",
        "odd": "1.975",
        "handicap": "2",
        "main": true, // Bet to consider
        "suspended": false // True if this bet is temporarily suspended
    },
    {
        "value": "Over",
        "odd": "3.45",
        "handicap": "2",
        "main": false, // Bet to no consider
        "suspended": false
    },
]
```

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `fixture` | query | integer | no | The id of the fixture |
| `league` | query | integer pattern:  (In this endpoint the "season" parameter is not needed) | no | The id of the league |
| `bet` | query | integer | no | The id of the bet |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: odds/live
parameters:
  fixture: '721238'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- fixture:
    id: 721238
    status:
      long: Second Half
      elapsed: 62
      seconds: '62:14'
  league:
    id: 30
    season: 2022
  teams:
    home:
      id: 1563
      goals: 1
    away:
      id: 1565
      goals: 0
  status:
    stopped: false
    blocked: false
    finished: false
  update: '2022-01-27T16:21:01+00:00'
  odds:
  - id: 20
    name: Match Corners
    values:
    - value: Over
      odd: '2.5'
      handicap: '8'
      main: null
      suspended: false
    - value: Exactly
      odd: '4.333'
      handicap: '8'
      main: null
      suspended: false
    - value: Under
      odd: '2.2'
      handicap: '8'
      main: null
      suspended: false
    - value: Over
      odd: '9'
      handicap: '10'
      main: null
      suspended: false
    - value: Exactly
      odd: '7.5'
      handicap: '10'
      main: null
      suspended: false
    - value: Under
      odd: '1.181'
      handicap: '10'
      main: null
      suspended: false
    - value: Over
      odd: '1.615'
      handicap: '7'
      main: null
      suspended: false
    - value: Exactly
      odd: '4'
      handicap: '7'
      main: null
      suspended: false
    - value: Under
      odd: '4.333'
      handicap: '7'
      main: null
      suspended: false
    - value: Over
      odd: '1.2'
      handicap: '6'
      main: null
      suspended: false
    - value: Exactly
      odd: '5.5'
      handicap: '6'
      main: null
      suspended: false
    - value: Under
      odd: '15'
      handicap: '6'
      main: null
      suspended: false
    - value: Over
      odd: '4.5'
      handicap: '9'
      main: null
      suspended: false
    - value: Exactly
      odd: '5'
      handicap: '9'
      main: null
      suspended: false
    - value: Under
      odd: '1.5'
      handicap: '9'
      main: null
      suspended: false
  - id: 33
    name: Asian Handicap
    values:
    - value: Home
      odd: '1.475'
      handicap: '-1'
      main: false
      suspended: false
    - value: Away
      odd: '2.6'
      handicap: '1'
      main: false
      suspended: false
    - value: Home
      odd: '2.05'
      handicap: '-1'
      main: true
      suspended: false
    - value: Away
      odd: '1.8'
      handicap: '1'
      main: true
      suspended: false
    - value: Home
      odd: '3.8'
      handicap: '-2'
      main: false
      suspended: false
    - value: Away
      odd: '1.25'
      handicap: '2'
      main: false
      suspended: false
    - value: Home
      odd: '1.3'
      handicap: '-1'
      main: false
      suspended: false
    - value: Away
      odd: '3.45'
      handicap: '1'
      main: false
      suspended: false
    - value: Home
      odd: '2.85'
      handicap: '-1'
      main: false
      suspended: false
    - value: Away
      odd: '1.4'
      handicap: '1'
      main: false
      suspended: false
  - id: 85
    name: Which team will score the 2nd goal?
    values:
    - value: '1'
      odd: '3.2'
      handicap: null
      main: null
      suspended: false
    - value: No goal
      odd: '2.2'
      handicap: null
      main: null
      suspended: false
    - value: '2'
      odd: '2.875'
      handicap: null
      main: null
      suspended: false
  - id: 36
    name: Over/Under Line
    values:
    - value: Over
      odd: '1.625'
      handicap: '2'
      main: false
      suspended: false
    - value: Under
      odd: '2.25'
      handicap: '2'
      main: false
      suspended: false
    - value: Over
      odd: '2.675'
      handicap: '2'
      main: false
      suspended: false
    - value: Under
      odd: '1.45'
      handicap: '2'
      main: false
      suspended: false
    - value: Over
      odd: '3.45'
      handicap: '2'
      main: false
      suspended: false
    - value: Under
      odd: '1.3'
      handicap: '2'
      main: false
      suspended: false
    - value: Over
      odd: '1.975'
      handicap: '2'
      main: true
      suspended: false
    - value: Under
      odd: '1.875'
      handicap: '2'
      main: true
      suspended: false
  - id: 60
    name: To Score 3 or More
    values:
    - value: Correa Caio Canedo
      odd: '67'
      handicap: null
      main: null
      suspended: false
    - value: Omar Al-Somah
      odd: '126'
      handicap: null
      main: null
      suspended: false
    - value: Omar Khrbin
      odd: '151'
      handicap: null
      main: null
      suspended: false
    - value: Ali Saleh
      odd: '401'
      handicap: null
      main: null
      suspended: false
    - value: Tahnoon Al Zaabi
      odd: '501'
      handicap: null
      main: null
      suspended: false
    - value: Mahmood Al Mawas
      odd: '401'
      handicap: null
      main: null
      suspended: false
    - value: Khalil Ibrahim
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Abdullah Ramadan
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Oliver Kass Kawo
      odd: '501'
      handicap: null
      main: null
      suspended: false
    - value: Ali Salmeen
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Amro Jenyat
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Fahd Youssef
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Mouhamad Anez
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Abdelaziz Sanqour
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Walid Abbas
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Mohamad Al Attas
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Tamer Haj Mohamad
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Moaiad Al Khouli
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Omar Midani
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Mahmoud Al Hammadi
      odd: '0'
      handicap: null
      main: null
      suspended: true
  - id: 23
    name: Final Score
    values:
    - value: 1-0
      odd: '2.2'
      handicap: null
      main: null
      suspended: false
    - value: 2-0
      odd: '4.5'
      handicap: null
      main: null
      suspended: false
    - value: 2-1
      odd: '9'
      handicap: null
      main: null
      suspended: false
    - value: 3-0
      odd: '19'
      handicap: null
      main: null
      suspended: false
    - value: 3-1
      odd: '34'
      handicap: null
      main: null
      suspended: false
    - value: 3-2
      odd: '67'
      handicap: null
      main: null
      suspended: false
    - value: 4-0
      odd: '67'
      handicap: null
      main: null
      suspended: false
    - value: 4-1
      odd: '101'
      handicap: null
      main: null
      suspended: false
    - value: 4-2
      odd: '301'
      handicap: null
      main: null
      suspended: false
    - value: 4-3
      odd: '351'
      handicap: null
      main: null
      suspended: true
    - value: 5-0
      odd: '301'
      handicap: null
      main: null
      suspended: false
    - value: 5-1
      odd: '301'
      handicap: null
      main: null
      suspended: true
    - value: 5-2
      odd: '351'
      handicap: null
      main: null
      suspended: true
    - value: 6-0
      odd: '351'
      handicap: null
      main: null
      suspended: true
    - value: 6-1
      odd: '401'
      handicap: null
      main: null
      suspended: true
    - value: 0-0
      odd: '3.4'
      handicap: null
      main: null
      suspended: true
    - value: 1-1
      odd: '4.333'
      handicap: null
      main: null
      suspended: false
    - value: 2-2
      odd: '29'
      handicap: null
      main: null
      suspended: false
    - value: 3-3
      odd: '301'
      handicap: null
      main: null
      suspended: false
    - value: 0-1
      odd: '5.5'
      handicap: null
      main: null
      suspended: true
    - value: 0-2
      odd: '17'
      handicap: null
      main: null
      suspended: true
    - value: 1-2
      odd: '17'
      handicap: null
      main: null
      suspended: false
    - value: 0-3
      odd: '51'
      handicap: null
      main: null
      suspended: true
    - value: 1-3
      odd: '51'
      handicap: null
      main: null
      suspended: false
    - value: 2-3
      odd: '81'
      handicap: null
      main: null
      suspended: false
    - value: 0-4
      odd: '201'
      handicap: null
      main: null
      suspended: true
    - value: 1-4
      odd: '201'
      handicap: null
      main: null
      suspended: false
    - value: 2-4
      odd: '351'
      handicap: null
      main: null
      suspended: true
    - value: 3-4
      odd: '351'
      handicap: null
      main: null
      suspended: true
    - value: 0-5
      odd: '351'
      handicap: null
      main: null
      suspended: true
    - value: 1-5
      odd: '401'
      handicap: null
      main: null
      suspended: true
    - value: 2-5
      odd: '401'
      handicap: null
      main: null
      suspended: true
    - value: 5-3
      odd: '401'
      handicap: null
      main: null
      suspended: true
    - value: 4-4
      odd: '401'
      handicap: null
      main: null
      suspended: true
  - id: 29
    name: Result / Both Teams To Score
    values:
    - value: Home/Yes
      odd: '8'
      handicap: null
      main: null
      suspended: false
    - value: Away/Yes
      odd: '17'
      handicap: null
      main: null
      suspended: false
    - value: Draw/Yes
      odd: '4.333'
      handicap: null
      main: null
      suspended: false
    - value: Home/No
      odd: '1.5'
      handicap: null
      main: null
      suspended: false
    - value: Away/No
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Draw/No
      odd: '0'
      handicap: null
      main: null
      suspended: true
  - id: 27
    name: Home Team Score a Goal (2nd Half)
    values:
    - value: 'Yes'
      odd: '2.625'
      handicap: null
      main: null
      suspended: false
    - value: 'No'
      odd: '1.444'
      handicap: null
      main: null
      suspended: false
  - id: 58
    name: Home Team Goals
    values:
    - value: Over
      odd: '2.625'
      handicap: '2'
      main: null
      suspended: false
    - value: Under
      odd: '1.444'
      handicap: '2'
      main: null
      suspended: false
    - value: Over
      odd: '13'
      handicap: '3'
      main: null
      suspended: false
    - value: Under
      odd: '1.04'
      handicap: '3'
      main: null
      suspended: false
  - id: 46
    name: Goal Scorer
    values:
    - value: Omar Al-Somah
      odd: '7'
      handicap: '2'
      main: null
      suspended: false
    - value: Correa Caio Canedo
      odd: '10'
      handicap: '2'
      main: null
      suspended: false
    - value: Omar Khrbin
      odd: '8.5'
      handicap: '2'
      main: null
      suspended: false
    - value: Ali Saleh
      odd: '12'
      handicap: '2'
      main: null
      suspended: false
    - value: Mahmood Al Mawas
      odd: '13'
      handicap: '2'
      main: null
      suspended: false
    - value: Tahnoon Al Zaabi
      odd: '15'
      handicap: '2'
      main: null
      suspended: false
    - value: Khalil Ibrahim
      odd: '19'
      handicap: '2'
      main: null
      suspended: false
    - value: Oliver Kass Kawo
      odd: '17'
      handicap: '2'
      main: null
      suspended: false
    - value: Abdullah Ramadan
      odd: '23'
      handicap: '2'
      main: null
      suspended: false
    - value: Fahd Youssef
      odd: '19'
      handicap: '2'
      main: null
      suspended: false
    - value: Amro Jenyat
      odd: '21'
      handicap: '2'
      main: null
      suspended: false
    - value: Ali Salmeen
      odd: '23'
      handicap: '2'
      main: null
      suspended: false
    - value: Mouhamad Anez
      odd: '21'
      handicap: '2'
      main: null
      suspended: false
    - value: Tamer Haj Mohamad
      odd: '26'
      handicap: '2'
      main: null
      suspended: false
    - value: Abdelaziz Sanqour
      odd: '41'
      handicap: '2'
      main: null
      suspended: false
    - value: Mahmoud Al Hammadi
      odd: '41'
      handicap: '2'
      main: null
      suspended: false
    - value: Walid Abbas
      odd: '41'
      handicap: '2'
      main: null
      suspended: false
    - value: Moaiad Al Khouli
      odd: '34'
      handicap: '2'
      main: null
      suspended: false
    - value: Mohamad Al Attas
      odd: '41'
      handicap: '2'
      main: null
      suspended: false
    - value: Omar Midani
      odd: '41'
      handicap: '2'
      main: null
      suspended: false
    - value: No 2nd Goal
      odd: '2.2'
      handicap: '2'
      main: null
      suspended: false
  - id: 21
    name: 3-Way Handicap
    values:
    - value: Home
      odd: '1.025'
      handicap: '1'
      main: false
      suspended: false
    - value: Draw
      odd: '19'
      handicap: '-1'
      main: false
      suspended: false
    - value: Away
      odd: '51'
      handicap: '-1'
      main: false
      suspended: false
    - value: Home
      odd: '51'
      handicap: '-3'
      main: false
      suspended: false
    - value: Draw
      odd: '17'
      handicap: '3'
      main: false
      suspended: false
    - value: Away
      odd: '1.025'
      handicap: '3'
      main: false
      suspended: false
    - value: Home
      odd: '15'
      handicap: '-2'
      main: false
      suspended: false
    - value: Draw
      odd: '4.333'
      handicap: '2'
      main: false
      suspended: false
    - value: Away
      odd: '1.222'
      handicap: '2'
      main: false
      suspended: false
    - value: Home
      odd: '3.75'
      handicap: '-1'
      main: true
      suspended: false
    - value: Draw
      odd: '1.833'
      handicap: '1'
      main: true
      suspended: false
    - value: Away
      odd: '3.4'
      handicap: '1'
      main: true
      suspended: false
  - id: 32
    name: Asian Corners
    values:
    - value: Over
      odd: '2.05'
      handicap: '8'
      main: null
      suspended: false
    - value: Under
      odd: '1.75'
      handicap: '8'
      main: null
      suspended: false
  - id: 25
    name: Match Goals
    values:
    - value: Over
      odd: '11'
      handicap: '4'
      main: null
      suspended: false
    - value: Under
      odd: '1.05'
      handicap: '4'
      main: null
      suspended: false
    - value: Over
      odd: '1.615'
      handicap: '2'
      main: null
      suspended: false
    - value: Under
      odd: '2.2'
      handicap: '2'
      main: null
      suspended: false
    - value: Over
      odd: '3.75'
      handicap: '3'
      main: null
      suspended: false
    - value: Under
      odd: '1.25'
      handicap: '3'
      main: null
      suspended: false
  - id: 35
    name: To Win 2nd Half
    values:
    - value: Home
      odd: '3.75'
      handicap: null
      main: null
      suspended: false
    - value: Draw
      odd: '1.833'
      handicap: null
      main: null
      suspended: false
    - value: Away
      odd: '3.4'
      handicap: null
      main: null
      suspended: false
  - id: 45
    name: Race to the 7th corner?
    values:
    - value: '1'
      odd: '81'
      handicap: null
      main: null
      suspended: false
    - value: '2'
      odd: '3.4'
      handicap: null
      main: null
      suspended: false
    - value: Neither
      odd: '1.3'
      handicap: null
      main: null
      suspended: false
  - id: 16
    name: How many goals will Away Team score?
    values:
    - value: No goal
      odd: '1.5'
      handicap: null
      main: null
      suspended: false
    - value: '1'
      odd: '2.75'
      handicap: null
      main: null
      suspended: false
    - value: '2'
      odd: '11'
      handicap: null
      main: null
      suspended: false
    - value: 3 or more
      odd: '41'
      handicap: null
      main: null
      suspended: false
  - id: 44
    name: Race to the 9th corner?
    values:
    - value: '1'
      odd: '101'
      handicap: null
      main: null
      suspended: false
    - value: '2'
      odd: '15'
      handicap: null
      main: null
      suspended: false
    - value: Neither
      odd: '1.03'
      handicap: null
      main: null
      suspended: false
  - id: 59
    name: Fulltime Result
    values:
    - value: Home
      odd: '1.3'
      handicap: null
      main: null
      suspended: false
    - value: Draw
      odd: '4.333'
      handicap: null
      main: null
      suspended: false
    - value: Away
      odd: '17'
      handicap: null
      main: null
      suspended: false
  - id: 72
    name: Double Chance
    values:
    - value: Home or Draw
      odd: '1.025'
      handicap: null
      main: null
      suspended: false
    - value: Away or Draw
      odd: '3.4'
      handicap: null
      main: null
      suspended: false
    - value: Home or Away
      odd: '1.2'
      handicap: null
      main: null
      suspended: false
  - id: 66
    name: Home Team Clean Sheet
    values:
    - value: 'Yes'
      odd: '1.5'
      handicap: null
      main: null
      suspended: false
    - value: 'No'
      odd: '2.5'
      handicap: null
      main: null
      suspended: false
  - id: 90
    name: 2nd Goal in Interval
    values:
    - value: 'Yes'
      odd: '4.5'
      handicap: '70'
      main: null
      suspended: false
    - value: 'No'
      odd: '1.166'
      handicap: '70'
      main: null
      suspended: false
    - value: 'Yes'
      odd: '2.5'
      handicap: '80'
      main: null
      suspended: false
    - value: 'No'
      odd: '1.5'
      handicap: '80'
      main: null
      suspended: false
  - id: 88
    name: Which team will score the 7th corner? (2 Way)
    values:
    - value: '1'
      odd: '2.375'
      handicap: null
      main: null
      suspended: false
    - value: '2'
      odd: '1.533'
      handicap: null
      main: null
      suspended: false
  - id: 68
    name: Goals Odd/Even
    values:
    - value: Odd
      odd: '1.615'
      handicap: null
      main: null
      suspended: false
    - value: Even
      odd: '2.2'
      handicap: null
      main: null
      suspended: false
  - id: 39
    name: Away Team Goals
    values:
    - value: Over
      odd: '11'
      handicap: '2'
      main: null
      suspended: false
    - value: Under
      odd: '1.05'
      handicap: '2'
      main: null
      suspended: false
  - id: 48
    name: Draw No Bet
    values:
    - value: Home
      odd: '1.05'
      handicap: null
      main: null
      suspended: false
    - value: Away
      odd: '11'
      handicap: null
      main: null
      suspended: false
  - id: 65
    name: Next 10 Minutes Total
    values:
    - value: Goals/Over  0.5
      odd: '3.75'
      handicap: '70'
      main: null
      suspended: false
    - value: Goals/Under  0.5
      odd: '1.25'
      handicap: '70'
      main: null
      suspended: false
    - value: Corners/Over  0.5
      odd: '1.571'
      handicap: '70'
      main: null
      suspended: false
    - value: Corners/Under  0.5
      odd: '2.25'
      handicap: '70'
      main: null
      suspended: false
  - id: 37
    name: Total Corners
    values:
    - value: Over
      odd: '1.615'
      handicap: '8'
      main: null
      suspended: false
    - value: Under
      odd: '2.2'
      handicap: '8'
      main: null
      suspended: false
  - id: 52
    name: 1x2 - 80 minutes
    values:
    - value: Home
      odd: '1.142'
      handicap: null
      main: null
      suspended: false
    - value: Draw
      odd: '5'
      handicap: null
      main: null
      suspended: false
    - value: Away
      odd: '41'
      handicap: null
      main: null
      suspended: false
  - id: 69
    name: Both Teams to Score
    values:
    - value: 'Yes'
      odd: '2.5'
      handicap: null
      main: null
      suspended: false
    - value: 'No'
      odd: '1.5'
      handicap: null
      main: null
      suspended: false
  - id: 43
    name: Both Teams To Score (2nd Half)
    values:
    - value: 'Yes'
      odd: '7'
      handicap: null
      main: null
      suspended: false
    - value: 'No'
      odd: '1.1'
      handicap: null
      main: null
      suspended: false
  - id: 56
    name: 1x2 - 70 minutes
    values:
    - value: Home
      odd: '1.055'
      handicap: null
      main: null
      suspended: false
    - value: Draw
      odd: '8.5'
      handicap: null
      main: null
      suspended: false
    - value: Away
      odd: '151'
      handicap: null
      main: null
      suspended: false
  - id: 15
    name: Last Corner
    values:
    - value: '1'
      odd: '2.5'
      handicap: null
      main: null
      suspended: false
    - value: '2'
      odd: '1.5'
      handicap: null
      main: null
      suspended: false
  - id: 53
    name: To Score 2 or More
    values:
    - value: Correa Caio Canedo
      odd: '6.5'
      handicap: null
      main: null
      suspended: false
    - value: Omar Al-Somah
      odd: '34'
      handicap: null
      main: null
      suspended: false
    - value: Omar Khrbin
      odd: '51'
      handicap: null
      main: null
      suspended: false
    - value: Ali Saleh
      odd: '101'
      handicap: null
      main: null
      suspended: false
    - value: Tahnoon Al Zaabi
      odd: '101'
      handicap: null
      main: null
      suspended: false
    - value: Mahmood Al Mawas
      odd: '101'
      handicap: null
      main: null
      suspended: false
    - value: Khalil Ibrahim
      odd: '126'
      handicap: null
      main: null
      suspended: false
    - value: Abdullah Ramadan
      odd: '151'
      handicap: null
      main: null
      suspended: false
    - value: Oliver Kass Kawo
      odd: '101'
      handicap: null
      main: null
      suspended: false
    - value: Ali Salmeen
      odd: '151'
      handicap: null
      main: null
      suspended: false
    - value: Amro Jenyat
      odd: '126'
      handicap: null
      main: null
      suspended: false
    - value: Fahd Youssef
      odd: '126'
      handicap: null
      main: null
      suspended: false
    - value: Mouhamad Anez
      odd: '126'
      handicap: null
      main: null
      suspended: false
    - value: Abdelaziz Sanqour
      odd: '251'
      handicap: null
      main: null
      suspended: false
    - value: Walid Abbas
      odd: '301'
      handicap: null
      main: null
      suspended: false
    - value: Mohamad Al Attas
      odd: '301'
      handicap: null
      main: null
      suspended: false
    - value: Tamer Haj Mohamad
      odd: '151'
      handicap: null
      main: null
      suspended: false
    - value: Moaiad Al Khouli
      odd: '251'
      handicap: null
      main: null
      suspended: false
    - value: Omar Midani
      odd: '301'
      handicap: null
      main: null
      suspended: false
    - value: Mahmoud Al Hammadi
      odd: '251'
      handicap: null
      main: null
      suspended: false
  - id: 62
    name: Last Team to Score (3 way)
    values:
    - value: '1'
      odd: '1.363'
      handicap: null
      main: null
      suspended: false
    - value: No goal
      odd: '3.4'
      handicap: null
      main: null
      suspended: true
    - value: '2'
      odd: '3'
      handicap: null
      main: null
      suspended: false
  - id: 47
    name: Away 1st Goal in Interval
    values:
    - value: 'Yes'
      odd: '7.5'
      handicap: '70'
      main: null
      suspended: false
    - value: 'No'
      odd: '1.071'
      handicap: '70'
      main: null
      suspended: false
    - value: 'Yes'
      odd: '4'
      handicap: '80'
      main: null
      suspended: false
    - value: 'No'
      odd: '1.222'
      handicap: '80'
      main: null
      suspended: false
  - id: 70
    name: Away Team Score a Goal (2nd Half)
    values:
    - value: 'Yes'
      odd: '2.5'
      handicap: null
      main: null
      suspended: false
    - value: 'No'
      odd: '1.5'
      handicap: null
      main: null
      suspended: false
  - id: 95
    name: Home 2nd Goal in Interval
    values:
    - value: 'Yes'
      odd: '8'
      handicap: '70'
      main: null
      suspended: false
    - value: 'No'
      odd: '1.062'
      handicap: '70'
      main: null
      suspended: false
    - value: 'Yes'
      odd: '4.333'
      handicap: '80'
      main: null
      suspended: false
    - value: 'No'
      odd: '1.2'
      handicap: '80'
      main: null
      suspended: false
  - id: 63
    name: Anytime Goal Scorer
    values:
    - value: Correa Caio Canedo
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Omar Al-Somah
      odd: '5'
      handicap: null
      main: null
      suspended: false
    - value: Omar Khrbin
      odd: '6'
      handicap: null
      main: null
      suspended: false
    - value: Ali Saleh
      odd: '8.5'
      handicap: null
      main: null
      suspended: false
    - value: Tahnoon Al Zaabi
      odd: '11'
      handicap: null
      main: null
      suspended: false
    - value: Mahmood Al Mawas
      odd: '9'
      handicap: null
      main: null
      suspended: false
    - value: Khalil Ibrahim
      odd: '13'
      handicap: null
      main: null
      suspended: false
    - value: Abdullah Ramadan
      odd: '17'
      handicap: null
      main: null
      suspended: false
    - value: Oliver Kass Kawo
      odd: '12'
      handicap: null
      main: null
      suspended: false
    - value: Ali Salmeen
      odd: '17'
      handicap: null
      main: null
      suspended: false
    - value: Fahd Youssef
      odd: '13'
      handicap: null
      main: null
      suspended: false
    - value: Amro Jenyat
      odd: '15'
      handicap: null
      main: null
      suspended: false
    - value: Mouhamad Anez
      odd: '15'
      handicap: null
      main: null
      suspended: false
    - value: Tamer Haj Mohamad
      odd: '19'
      handicap: null
      main: null
      suspended: false
    - value: Abdelaziz Sanqour
      odd: '26'
      handicap: null
      main: null
      suspended: false
    - value: Walid Abbas
      odd: '29'
      handicap: null
      main: null
      suspended: false
    - value: Mohamad Al Attas
      odd: '29'
      handicap: null
      main: null
      suspended: false
    - value: Moaiad Al Khouli
      odd: '26'
      handicap: null
      main: null
      suspended: false
    - value: Omar Midani
      odd: '29'
      handicap: null
      main: null
      suspended: false
    - value: No 1st Goal
      odd: '0'
      handicap: null
      main: null
      suspended: true
    - value: Mahmoud Al Hammadi
      odd: '26'
      handicap: null
      main: null
      suspended: false
    - value: No 2nd Goal
      odd: '0'
      handicap: null
      main: null
      suspended: true
  - id: 67
    name: How many goals will Home Team score?
    values:
    - value: No goal
      odd: '2'
      handicap: null
      main: null
      suspended: true
    - value: '1'
      odd: '1.444'
      handicap: null
      main: null
      suspended: false
    - value: '2'
      odd: '3.25'
      handicap: null
      main: null
      suspended: false
    - value: 3 or more
      odd: '13'
      handicap: null
      main: null
      suspended: false
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: odds parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   bug: T...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/odds/live"
params = {
    "fixture": '<fixture>',  # The id of the fixture
    "league": '<league>',  # The id of the league
    "bet": '<bet>',  # The id of the bet
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/odds/live?bet=1&league=39", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /odds/live/bets` — odds/live/bets

**Tags:** Odds (In-Play)
**Operation ID:** `get-bets`

Get all available bets for in-play odds.

All bets `id` can be used in endpoint `odds/live` as filters, **but are not compatible with endpoint `odds` for pre-match odds**.

**Update Frequency** : This endpoint is updated every 60 seconds.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `id` | query | string | no | The id of the bet name |
| `search` | query | string minLength: 3 maxLength: 3 | no | The name of the bet |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: odds/live/bets
parameters: []
errors: []
results: 137
paging:
  current: 1
  total: 1
response:
- id: 1
  name: Over/Under Extra Time
- id: 2
  name: 1x2 Extra Time
- id: 3
  name: Extra Time Asian Corners
- id: 4
  name: Extra Time Total Corners (3 Ways) (1st Half)
- id: 5
  name: Extra Time Double Result
- id: 6
  name: Which team will score the 1st goal in extra time?
- id: 7
  name: Extra Time Asian Corners (1st Half)
- id: 8
  name: Method of Victory
- id: 9
  name: Both Teams To Score (ET)
- id: 10
  name: To Qualify
- id: 11
  name: Asian Handicap Extra Time
- id: 12
  name: 1x2 Extra Time (1st Half)
- id: 13
  name: Extra Time Total Corners (3 Ways)
- id: 14
  name: Over/Under Extra Time (1st Half)
- id: 15
  name: Last Corner
- id: 16
  name: How many goals will Away Team score?
- id: 17
  name: Asian Handicap (1st Half)
- id: 18
  name: 1st Goal in Interval
- id: 19
  name: 1x2 (1st Half)
- id: 20
  name: Match Corners
- id: 21
  name: 3-Way Handicap
- id: 22
  name: 1x2 - 30 minutes
- id: 23
  name: Final Score
- id: 24
  name: Over/Under Line (1st Half)
- id: 25
  name: Match Goals
- id: 26
  name: European Handicap (1st Half)
- id: 27
  name: Home Team Score a Goal (2nd Half)
- id: 28
  name: Home Team  to Score in Both Halves
- id: 29
  name: Result / Both Teams To Score
- id: 30
  name: Both Teams To Score (1st Half)
- id: 31
  name: Total Corners (3way) (2nd Half)
- id: 32
  name: Asian Corners
- id: 33
  name: Asian Handicap
- id: 34
  name: 1x2 - 40 minutes
- id: 35
  name: To Win 2nd Half
- id: 36
  name: Over/Under Line
- id: 37
  name: Total Corners
- id: 38
  name: Away Team to Score in Both Halves
- id: 39
  name: Away Team Goals
- id: 40
  name: Total Corners (3 way) (1st Half)
- id: 41
  name: 1x2 - 50 minutes
- id: 42
  name: Race to the 3rd corner?
- id: 43
  name: Both Teams To Score (2nd Half)
- id: 44
  name: Race to the 9th corner?
- id: 45
  name: Race to the 7th corner?
- id: 46
  name: Goal Scorer
- id: 47
  name: Away 1st Goal in Interval
- id: 48
  name: Draw No Bet
- id: 49
  name: Over/Under (1st Half)
- id: 50
  name: 1x2 - 60 minutes
- id: 51
  name: Asian Corners (1st Half)
- id: 52
  name: 1x2 - 80 minutes
- id: 53
  name: To Score 2 or More
- id: 54
  name: Home 1st Goal in Interval
- id: 55
  name: Correct Score (1st Half)
- id: 56
  name: 1x2 - 70 minutes
- id: 57
  name: Away Team Clean Sheet
- id: 58
  name: Home Team Goals
- id: 59
  name: Fulltime Result
- id: 60
  name: To Score 3 or More
- id: 61
  name: Race to the 5th corner?
- id: 62
  name: Last Team to Score (3 way)
- id: 63
  name: Anytime Goal Scorer
- id: 64
  name: Half Time/Full Time
- id: 65
  name: Next 10 Minutes Total
- id: 66
  name: Home Team Clean Sheet
- id: 67
  name: How many goals will Home Team score?
- id: 68
  name: Goals Odd/Even
- id: 69
  name: Both Teams to Score
- id: 70
  name: Away Team Score a Goal (2nd Half)
- id: 71
  name: Which team will score the 4th corner? (2 Way)
- id: 72
  name: Double Chance
- id: 73
  name: Which team will score the 1st goal?
- id: 74
  name: Which team will score the 3rd corner? (2 Way)
- id: 75
  name: Which team will score the 2nd corner? (2 Way)
- id: 76
  name: Corners European Handicap
- id: 77
  name: 1x2 - 10 minutes
- id: 78
  name: Corners 1x2
- id: 79
  name: 1x2 - 20 minutes
- id: 80
  name: Method of 1st Goal
- id: 81
  name: Method of Qualification
- id: 82
  name: Game Won After Penalties Shootout
- id: 83
  name: Game Won In Extra Time
- id: 84
  name: Which team will score the 2nd goal?
- id: 85
  name: Which team will score the 2nd goal?
- id: 86
  name: Which team will score the 6th corner? (2 Way)
- id: 87
  name: Which team will score the 5th corner? (2 Way)
- id: 88
  name: Which team will score the 7th corner? (2 Way)
- id: 89
  name: Which team will score the 9th corner? (2 Way)
- id: 90
  name: 2nd Goal in Interval
- id: 91
  name: Away 2nd Goal in Interval
- id: 92
  name: Which team will score the 3rd goal?
- id: 93
  name: Which team will score the 10th corner? (2 Way)
- id: 94
  name: 3rd Goal in Interval
- id: 95
  name: Home 2nd Goal in Interval
- id: 96
  name: Asian Handicap Converted Penalties
- id: 97
  name: Sudden Death
- id: 98
  name: Away Penalty Shootout
- id: 99
  name: Home Penalty Shootout
- id: 100
  name: Home Total Converted Penalties
- id: 101
  name: Total Penalties in Shootout
- id: 102
  name: Last Penalty Score/Miss
- id: 103
  name: Correct Score in Shootouts
- id: 104
  name: Total Converted Penalties
- id: 105
  name: Total Converted Penalties - Goal Line
- id: 106
  name: Away Total Converted Penalties
- id: 107
  name: Penalties Shootout Winner
- id: 108
  name: Which team will score the 11th corner? (2 Way)
- id: 109
  name: Which team will score the 4th goal?
- id: 110
  name: Which team will score the 8th corner? (2 Way)
- id: 111
  name: Last Penalty Scorer in Shootout
- id: 112
  name: Which team will score the 5th goal?
- id: 113
  name: Method of 2nd Goal
- id: 114
  name: Which team will score the 13th corner? (2 Way)
- id: 115
  name: Player to be Booked
- id: 116
  name: Action In Next 1 Minutes
- id: 117
  name: First Action In Next 5 Minutes
- id: 118
  name: Player to be Sent Off
- id: 119
  name: Total Cards
- id: 120
  name: Which team will score the 12th corner? (2 Way)
- id: 121
  name: Which team will score the 14th corner? (2 Way)
- id: 122
  name: Which team will score the 15th corner? (2 Way)
- id: 123
  name: Which team will score the 16th corner? (2 Way)
- id: 124
  name: Which team will score the 17th corner? (2 Way)
- id: 125
  name: Home 3rd Goal in Interval
- id: 126
  name: Which team will score the 18th corner? (2 Way)
- id: 127
  name: Which team will score the 6th goal?
- id: 128
  name: Away 3rd Goal in Interval
- id: 129
  name: Which team will score the 2nd goal in extra time?
- id: 130
  name: Method of 3rd Goal
- id: 131
  name: 4th Goal in Interval
- id: 132
  name: Which team will score the 7th goal?
- id: 133
  name: Which team will score the 19th corner? (2 Way)
- id: 134
  name: Home 4th Goal in Interval
- id: 135
  name: Away 4th Goal in Interval
- id: 136
  name: 5th Goal in Interval
- id: 137
  name: Home 5th Goal in Interval
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: odds parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   bug: T...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/odds/live/bets"
params = {
    "id": '<id>',  # The id of the bet name
    "search": '<search>',  # The name of the bet
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/odds/bets", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /odds` — Odds

**Tags:** Odds (Pre-Match)
**Operation ID:** `get-odds`

Get odds from fixtures, leagues or date.

This endpoint uses a **pagination system**, you can navigate between the different pages with to the `page` parameter.

> **Pagination** : 10 results per page.

We provide pre-match odds between 1 and 14 days before the fixture.

We keep a 7-days history *(The availability of odds may vary according to the leagues, seasons, fixtures and bookmakers)*

**Update Frequency** : This endpoint is updated every 3 hours.

**Recommended Calls** : 1 call every 3 hours.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `fixture` | query | integer | no | The id of the fixture |
| `league` | query | integer | no | The id of the league |
| `season` | query | integer pattern: YYYY minLength: 4 maxLength: 4 | no | The season of the league |
| `date` | query | string pattern: YYYY-MM-DD | no | A valid date |
| `timezone` | query | string | no | A valid timezone from the endpoint `Timezone` |
| `page` | query | integer | no | Use for the pagination |
| `bookmaker` | query | integer | no | The id of the bookmaker |
| `bet` | query | integer | no | The id of the bet |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: odds
parameters:
  fixture: '326090'
  bookmaker: '6'
errors: []
results: 1
paging:
  current: 1
  total: 1
response:
- league:
    id: 116
    name: Vysshaya Liga
    country: Belarus
    logo: https://media.api-sports.io/football/leagues/116.png
    flag: https://media.api-sports.io/flags/by.svg
    season: 2020
  fixture:
    id: 326090
    timezone: UTC
    date: '2020-05-15T15:00:00+00:00'
    timestamp: 1589554800
  update: '2020-05-15T09:49:32+00:00'
  bookmakers:
  - id: 6
    name: Bwin
    bets:
    - id: 38
      name: Exact Goals Number
      values:
      - value: 4
        odd: '7.00'
      - value: 3
        odd: '4.40'
      - value: 2
        odd: '3.40'
      - value: more 8
        odd: '251.00'
      - value: 7
        odd: '101.00'
      - value: more 5
        odd: '8.00'
      - value: 6
        odd: '31.00'
      - value: 5
        odd: '14.00'
      - value: 0
        odd: '6.25'
      - value: 1
        odd: '3.90'
    - id: 20
      name: Double Chance - First Half
      values:
      - value: Home/Draw
        odd: '1.20'
      - value: Home/Away
        odd: '1.75'
      - value: Draw/Away
        odd: '1.26'
    - id: 17
      name: Total - Away
      values:
      - value: Under 2.5
        odd: '1.06'
      - value: Over 2.5
        odd: '7.25'
      - value: Under 1.5
        odd: '1.33'
      - value: Over 1.5
        odd: '3.10'
    - id: 16
      name: Total - Home
      values:
      - value: Under 2.5
        odd: '1.09'
      - value: Over 2.5
        odd: '6.25'
      - value: Under 1.5
        odd: '1.40'
      - value: Over 1.5
        odd: '2.70'
    - id: 22
      name: Odd/Even - First Half
      values:
      - value: Even
        odd: '1.60'
      - value: Odd
        odd: '2.20'
    - id: 21
      name: Odd/Even
      values:
      - value: Even
        odd: '1.80'
      - value: Odd
        odd: '1.91'
    - id: 34
      name: Both Teams Score - First Half
      values:
      - value: 'No'
        odd: '1.14'
      - value: 'Yes'
        odd: '5.00'
    - id: 32
      name: Win Both Halves
      values:
      - value: Away
        odd: '10.50'
      - value: Draw
        odd: '1.13'
      - value: Home
        odd: '8.00'
    - id: 12
      name: Double Chance
      values:
      - value: Draw/Away
        odd: '1.50'
      - value: Home/Away
        odd: '1.33'
      - value: Home/Draw
        odd: '1.36'
    - id: 10
      name: Exact Score
      values:
      - value: '3:4'
        odd: '126.00'
      - value: '2:4'
        odd: '81.00'
      - value: '2:3'
        odd: '36.00'
      - value: '1:4'
        odd: '67.00'
      - value: '1:3'
        odd: '26.00'
      - value: '1:2'
        odd: '11.50'
      - value: 0:4
        odd: '67.00'
      - value: '4:1'
        odd: '51.00'
      - value: '4:0'
        odd: '51.00'
      - value: '3:2'
        odd: '34.00'
      - value: '3:1'
        odd: '21.00'
      - value: '3:0'
        odd: '23.00'
      - value: '2:1'
        odd: '10.50'
      - value: '2:0'
        odd: '11.50'
      - value: '1:0'
        odd: '7.25'
      - value: '4:2'
        odd: '81.00'
      - value: '4:3'
        odd: '126.00'
      - value: 0:3
        odd: '31.00'
      - value: 0:2
        odd: '14.00'
      - value: 0:1
        odd: '8.25'
      - value: '4:4'
        odd: '151.00'
      - value: '3:3'
        odd: '67.00'
      - value: '2:2'
        odd: '16.00'
      - value: '1:1'
        odd: '6.25'
      - value: 0:0
        odd: '6.25'
    - id: 13
      name: First Half Winner
      values:
      - value: Home
        odd: '3.20'
      - value: Draw
        odd: '1.90'
      - value: Away
        odd: '3.70'
    - id: 15
      name: Team To Score Last
      values:
      - value: No goal
        odd: '6.25'
      - value: Away
        odd: '2.15'
      - value: Home
        odd: '1.95'
    - id: 14
      name: Team To Score First
      values:
      - value: Away
        odd: '2.15'
      - value: Draw
        odd: '6.25'
      - value: Home
        odd: '1.95'
    - id: 46
      name: Exact Goals Number - First Half
      values:
      - value: more 3
        odd: '8.25'
      - value: 0
        odd: '2.35'
      - value: 1
        odd: '2.60'
      - value: 2
        odd: '4.75'
    - id: 25
      name: Result/Total Goals
      values:
      - value: Home/Over 2.5
        odd: '4.60'
      - value: Away/Under 3.5
        odd: '3.50'
      - value: Home/Under 3.5
        odd: '3.00'
      - value: Away/Over 3.5
        odd: '12.00'
      - value: Home/Over 3.5
        odd: '9.25'
      - value: Away/Over 2.5
        odd: '5.50'
      - value: Home/Under 2.5
        odd: '4.50'
      - value: Away/Under 2.5
        odd: '5.25'
    - id: 24
      name: Results/Both Teams Score
      values:
      - value: Away/No
        odd: '4.40'
      - value: Draw/No
        odd: '6.25'
      - value: Home/No
        odd: '3.75'
      - value: Away/Yes
        odd: '6.50'
      - value: Draw/Yes
        odd: '4.50'
      - value: Home/Yes
        odd: '5.50'
    - id: 44
      name: Away Team Score a Goal
      values:
      - value: 'No'
        odd: '2.55'
      - value: 'Yes'
        odd: '1.45'
    - id: 43
      name: Home Team Score a Goal
      values:
      - value: 'No'
        odd: '2.90'
      - value: 'Yes'
        odd: '1.36'
    - id: 40
      name: Home Team Exact Goals Number
      values:
      - value: 1
        odd: '2.55'
      - value: 2
        odd: '4.20'
      - value: 0
        odd: '2.90'
      - value: more 3
        odd: '6.25'
    - id: 42
      name: Second Half Exact Goals Number
      values:
      - value: more 3
        odd: '5.50'
      - value: 0
        odd: '3.00'
      - value: 1
        odd: '2.60'
      - value: 2
        odd: '3.90'
    - id: 41
      name: Away Team Exact Goals Number
      values:
      - value: more 3
        odd: '7.25'
      - value: 0
        odd: '2.55'
      - value: 1
        odd: '2.50'
      - value: 2
        odd: '4.60'
    - id: 7
      name: HT/FT Double
      values:
      - value: Home/Home
        odd: '4.20'
      - value: Draw/Draw
        odd: '4.10'
      - value: Draw/Away
        odd: '6.75'
      - value: Home/Away
        odd: '36.00'
      - value: Home/Draw
        odd: '14.50'
      - value: Away/Away
        odd: '5.00'
      - value: Away/Draw
        odd: '14.50'
      - value: Away/Home
        odd: '31.00'
      - value: Draw/Home
        odd: '5.75'
    - id: 26
      name: Goals Over/Under - Second Half
      values:
      - value: Under 3.5
        odd: '1.01'
      - value: Over 3.5
        odd: '12.00'
      - value: Over 1.5
        odd: '2.50'
      - value: Under 1.5
        odd: '1.48'
      - value: Under 0.5
        odd: '3.00'
      - value: Over 0.5
        odd: '1.34'
      - value: Under 2.5
        odd: '1.11'
      - value: Over 2.5
        odd: '5.50'
    - id: 6
      name: Goals Over/Under First Half
      values:
      - value: Under 0.5
        odd: '2.35'
      - value: Over 0.5
        odd: '1.53'
      - value: Under 2.5
        odd: '1.04'
      - value: Over 2.5
        odd: '8.25'
      - value: Under 1.5
        odd: '1.28'
      - value: Over 1.5
        odd: '3.30'
      - value: Under 3.5
        odd: '1.01'
      - value: Over 3.5
        odd: '21.00'
    - id: 5
      name: Goals Over/Under
      values:
      - value: Under 5.5
        odd: '1.01'
      - value: Over 3.5
        odd: '4.20'
      - value: Under 3.5
        odd: '1.19'
      - value: Over 1.5
        odd: '1.44'
      - value: Over 5.5
        odd: '15.00'
      - value: Under 0.5
        odd: '6.25'
      - value: Over 0.5
        odd: '1.09'
      - value: Under 2.5
        odd: '1.55'
      - value: Over 2.5
        odd: '2.35'
      - value: Under 4.5
        odd: '1.05'
      - value: Over 4.5
        odd: '8.00'
      - value: Under 1.5
        odd: '2.60'
    - id: 3
      name: Second Half Winner
      values:
      - value: Away
        odd: '3.30'
      - value: Draw
        odd: '2.20'
      - value: Home
        odd: '2.85'
    - id: 2
      name: Home/Away
      values:
      - value: Away
        odd: '2.05'
      - value: Home
        odd: '1.70'
    - id: 1
      name: Match Winner
      values:
      - value: Away
        odd: '2.95'
      - value: Draw
        odd: '2.95'
      - value: Home
        odd: '2.50'
    - id: 9
      name: Handicap Result
      values:
      - value: Away -2
        odd: '1.13'
      - value: Draw -2
        odd: '7.00'
      - value: Home -2
        odd: '12.00'
      - value: Home -1
        odd: '5.25'
      - value: Away +2
        odd: '15.00'
      - value: Draw +2
        odd: '8.25'
      - value: Home +2
        odd: '1.09'
      - value: Draw +1
        odd: '4.40'
      - value: Away +1
        odd: '6.75'
      - value: Home +1
        odd: '1.36'
      - value: Draw -1
        odd: '4.00'
      - value: Away -1
        odd: '1.50'
    - id: 30
      name: Win to Nil - Away
      values:
      - value: 'Yes'
        odd: '4.40'
      - value: 'No'
        odd: '1.17'
    - id: 29
      name: Win to Nil - Home
      values:
      - value: 'No'
        odd: '1.22'
      - value: 'Yes'
        odd: '3.75'
    - id: 8
      name: Both Teams Score
      values:
      - value: 'No'
        odd: '1.72'
      - value: 'Yes'
        odd: '2.00'
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: odds parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   bug: T...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/odds"
params = {
    "fixture": '<fixture>',  # The id of the fixture
    "league": '<league>',  # The id of the league
    "season": '<season>',  # The season of the league
    "date": '<date>',  # A valid date
    "timezone": '<timezone>',  # A valid timezone from the endpoint `Timezone`
    "page": '<page>',  # Use for the pagination
    "bookmaker": '<bookmaker>',  # The id of the bookmaker
    "bet": '<bet>',  # The id of the bet
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/odds?season=2019&bet=1&bookmaker=6&fixture=157140&league=39", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /odds/mapping` — Mapping

**Tags:** Odds (Pre-Match)
**Operation ID:** `get-odds-mapping`

Get the list of available fixtures `id` for the endpoint odds.

All fixtures, leagues `id` and `date` can be used in endpoint odds as filters.

This endpoint uses a **pagination system**, you can navigate between the different pages with to the `page` parameter.

> **Pagination** : 100 results per page.

**Update Frequency** : This endpoint is updated every day.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `page` | query | integer | no | Use for the pagination |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: odds/mapping
parameters: []
errors: []
results: 129
paging:
  current: 1
  total: 1
response:
- league:
    id: 106
    season: 2019
  fixture:
    id: 154507
    date: '2020-05-29T18:30:00+00:00'
    timestamp: 1590777000
  update: '2020-05-15T09:52:28+00:00'
- league:
    id: 106
    season: 2019
  fixture:
    id: 154508
    date: '2020-05-29T16:00:00+00:00'
    timestamp: 1590768000
  update: '2020-05-15T09:52:28+00:00'
- league:
    id: 271
    season: 2019
  fixture:
    id: 182450
    date: '2020-05-23T13:55:00+00:00'
    timestamp: 1590242100
  update: '2020-05-15T09:51:45+00:00'
- league:
    id: 271
    season: 2019
  fixture:
    id: 182564
    date: '2020-05-27T18:00:00+00:00'
    timestamp: 1590602400
  update: '2020-05-15T09:52:17+00:00'
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: odds/mapping parameters: [] errors:   time: '2019-11-26T00:00:00+00:00' ...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/odds/mapping"
params = {
    "page": '<page>',  # Use for the pagination
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/odds/mapping", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /odds/bookmakers` — Bookmakers

**Tags:** Odds (Pre-Match)
**Operation ID:** `get-bookmakers`

Get all available bookmakers.

All bookmakers `id` can be used in endpoint odds as filters.

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `id` | query | integer | no | The id of the bookmaker |
| `search` | query | string minLength: 3 maxLength: 3 | no | The name of the bookmaker |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: odds/bookmakers
parameters: []
errors: []
results: 15
paging:
  current: 1
  total: 1
response:
- id: 1
  name: 10Bet
- id: 2
  name: Marathonbet
- id: 3
  name: Betfair
- id: 4
  name: Pinnacle
- id: 5
  name: Sport Betting Online
- id: 6
  name: Bwin
- id: 7
  name: William Hill
- id: 8
  name: Bet365
- id: 9
  name: Dafabet
- id: 10
  name: Ladbrokes
- id: 11
  name: 1xBet
- id: 12
  name: BetFred
- id: 13
  name: 188Bet
- id: 15
  name: Interwetten
- id: 16
  name: Unibet
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: odds/bookmakers parameters: [] errors:   time: '2019-11-26T00:00:00+00:0...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/odds/bookmakers"
params = {
    "id": '<id>',  # The id of the bookmaker
    "search": '<search>',  # The name of the bookmaker
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/odds/bookmakers", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---

## `GET /odds/bets` — Bets

**Tags:** Odds (Pre-Match)
**Operation ID:** `get-bets`

Get all available bets for pre-match odds.

All bets `id` can be used in endpoint odds as filters, **but are not compatible with endpoint `odds/live` for in-play odds**.

**Update Frequency** : This endpoint is updated several times a week.

**Recommended Calls** : 1 call per day.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `x-apisports-key` | header | string | yes | Your Api-Key |
| `id` | query | string | no | The id of the bet name |
| `search` | query | string minLength: 3 maxLength: 3 | no | The name of the bet |

### Response 200 — OK

**Schema:**
```
object {
  get: string
  parameters: array<  object {
      field: string
    }>
  errors: array<  object {
      field: string
    }>
  results: integer
  response: array<any>
}
```

**Example** (`All`):
```json
get: odds/bets
parameters:
  search: under
errors: []
results: 7
paging:
  current: 1
  total: 1
response:
- id: 5
  name: Goals Over/Under
- id: 6
  name: Goals Over/Under First Half
- id: 26
  name: Goals Over/Under - Second Half
- id: 45
  name: Corners Over Under
- id: 57
  name: Home Corners Over/Under
- id: 58
  name: Away Corners Over/Under
- id: 74
  name: 10 Over/Under
```

### Errors

| Code | Description | Example |
|---|---|---|
| 204 | No Content | `get: odds/bets parameters: [] errors:   time: '2019-11-26T00:00:00+00:00'   b...` |
| 499 | Time Out | `message: Something went wrong while fetching details. Try again later.` |
| 500 | Internal Server Error | `message: Something went wrong while fetching details. Try again later.` |

### Examples

**Python (requests):**
```python
import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v3.football.api-sports.io"

url = f"{BASE_URL}/odds/bets"
params = {
    "id": '<id>',  # The id of the bet name
    "search": '<search>',  # The name of the bet
}
headers = {"x-apisports-key": API_KEY}
response = requests.get(url, headers=headers, params=params)
response.raise_for_status()
data = response.json()
print(data)
```

**Python (http.client):**
```python
import http.client

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "XxXxXxXxXxXxXxXxXxXxXxXx"
    }

conn.request("GET", "/odds/bets", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
```

---
