#!/usr/bin/env python3

import argparse
import requests
import json
from dataclasses import dataclass
from typing import List
from datetime import datetime
import time
from zoneinfo import ZoneInfo

api_key = "YOUR_API_KEY"

parser = argparse.ArgumentParser(description="Chicago CTA L Train Tracker")
parser.add_argument('-l', '--line', type=str, choices=['Red', 'Blue', 'Brown', 'Green', 'Orange', 'Purple', 'Pink', 'Yellow'], default='Red', help='Line to track (default: Red)')
args = parser.parse_args()

line_to_route_id = {
    'Red': 'red',
    'Blue': 'blue',
    'Brown': 'brn',
    'Green': 'g',
    'Orange': 'org',
    'Purple': 'p',
    'Pink': 'pink',
    'Yellow': 'y'
}
directions = {
    'Red': (0, -1),
    'Blue': (0, -1),
    'Brown': (0, -1),
    'Green': (0, -1),
    'Orange': (0, -1),
    'Purple': (0, -1),
    'Pink': (0, -1),
    'Yellow': (0, -1)
}
colors = {
    'Red': '\033[1;38;2;255;255;255;48;2;198;12;48m',
    'Blue': '\033[1;38;2;255;255;255;48;2;0;161;222m',
    'Brown': '\033[1;38;2;255;255;255;48;2;98;54;27m',
    'Green': '\033[1;38;2;255;255;255;48;2;0;155;58m',
    'Orange': '\033[1;38;2;255;255;255;48;2;249;70;28m',
    'Purple': '\033[1;38;2;255;255;255;48;2;82;35;152m',
    'Pink': '\033[1;38;2;255;255;255;48;2;226;126;166m',
    'Yellow': '\033[1;38;2;0;0;0;48;2;249;227;0m'
}

route_id = line_to_route_id[args.line]
url = f"https://lapi.transitchicago.com/api/1.0/ttpositions.aspx?key={api_key}&rt={route_id}&outputType=JSON"

@dataclass
class Train():
    id: str
    vehicle_id: str
    direction: str
    next_station_index: int
    next_station: str
    time_until: float
    leg_total: float
    pct_distance_along_trip: float

    def __str__(self):
        return f"""
{ "\033[1;41m" + self.direction + "\033[0m" } { "\033[1;44m" + str(self.vehicle_id) + "\033[0m" }
{ "\033[1;33m" + self.next_station } in {round(self.time_until)}s\033[0m"""

class TrainGetter():
    def __init__(self) -> None:
        self.stop_id_to_name = {}
        match args.line:
            case 'Red':
                self.name_to_index = {
                    "95th/Dan Ryan": 0,
                    "87th": 1,
                    "79th": 2,
                    "69th": 3,
                    "63rd": 4,
                    "Garfield (Red)": 5,
                    "47th (Red)": 6,
                    "Sox-35th": 7,
                    "Cermak-Chinatown": 8,
                    "Roosevelt": 9,
                    "Harrison": 10,
                    "Jackson (Red)": 11,
                    "Monroe (Red)": 12,
                    "Lake (Subway)": 13,
                    "Grand (Red)": 14,
                    "Chicago (Red)": 15,
                    "Clark/Division": 16,
                    "North/Clybourn": 17,
                    "Fullerton": 18,
                    "Belmont (Red/Brown/Purple)": 19,
                    "Addison (Red)": 20,
                    "Sheridan": 21,
                    "Wilson": 22,
                    "Lawrence": 23,
                    "Argyle": 24,
                    "Berwyn": 25,
                    "Bryn Mawr": 26,
                    "Thorndale": 27,
                    "Granville": 28,
                    "Loyola": 29,
                    "Morse": 30,
                    "Jarvis": 31,
                    "Howard": 32,
                }
            case 'Blue':
                self.name_to_index = {
                    "Forest Park": 0,
                    "Harlem (Blue - Forest Park Branch)": 1,
                    "Oak Park (Blue)": 2,
                    "Austin (Blue)": 3,
                    "Cicero (Blue)": 4,
                    "Pulaski (Blue)": 5,
                    "Kedzie-Homan": 6,
                    "Western (Blue - Forest Park Branch)": 7,
                    "Illinois Medical District": 8,
                    "Racine": 9,
                    "UIC-Halsted": 10,
                    "Clinton (Blue)": 11,
                    "LaSalle": 12,
                    "Jackson (Blue)": 13,
                    "Monroe (Blue)": 14,
                    "Washington": 15,
                    "Clark/Lake": 16,
                    "Grand (Blue)": 17,
                    "Chicago (Blue)": 18,
                    "Division": 19,
                    "Damen (Blue)": 20,
                    "Western (Blue - O'Hare Branch)": 21,
                    "California (Blue)": 22,
                    "Logan Square": 23,
                    "Belmont (Blue)": 24,
                    "Addison (Blue)": 25,
                    "Irving Park (Blue)": 26,
                    "Montrose (Blue)": 27,
                    "Jefferson Park Transit Center": 28,
                    "Harlem (Blue - O'Hare Branch)": 29,
                    "Cumberland": 30,
                    "Rosemont": 31,
                    "O'Hare": 32,
                }
            case 'Brown':
                self.name_to_index = {                     
                    "Clark/Lake": 0,
                    "State/Lake (Loop 'L')": 1,
                    "Washington/Wabash": 2,
                    "Adams/Wabash": 3,
                    "Harold Washington Library-State/Van Buren": 4,
                    "LaSalle/Van Buren": 5,
                    "Quincy": 6,
                    "Washington/Wells": 7,
                    "Merchandise Mart (Brown/Purple)": 8,
                    "Chicago (Brown/Purple)": 9,
                    "Sedgwick (Brown/Purple)": 10,
                    "Armitage (Brown/Purple)": 11,
                    "Fullerton": 12,
                    "Diversey (Brown/Purple)": 13,
                    "Wellington (Brown/Purple)": 14,
                    "Belmont (Red/Brown/Purple)": 15,
                    "Southport": 16,
                    "Paulina": 17,
                    "Addison (Brown)": 18,
                    "Irving Park (Brown)": 19,
                    "Montrose (Brown)": 20,
                    "Damen (Brown)": 21,
                    "Western (Brown)": 22,
                    "Rockwell": 23,
                    "Francisco": 24,
                    "Kedzie (Brown)": 25,
                    "Kimball": 26,
                }
            case 'Green':
                self.name_to_index = {
                    "Ashland/63rd": 0,
                    "Halsted (Green)": 1,
                    "Cottage Grove": 2,
                    "King Drive": 3,
                    "Garfield (Green)": 4,
                    "51st": 5,
                    "47th (Green)": 6,
                    "43rd": 7,
                    "Indiana": 8,
                    "35th-Bronzeville-IIT": 9,
                    "Cermak-McCormick Place": 10,
                    "Roosevelt": 11,
                    "Adams/Wabash": 12,
                    "Washington/Wabash": 13,
                    "State/Lake (Loop 'L')": 14,
                    "Clark/Lake": 15,
                    "Clinton (Green/Pink)": 16,
                    "Morgan (Green/Pink)": 17,
                    "Ashland (Green/Pink)": 18,
                    "Damen (Green)": 19,
                    "California (Green)": 20,
                    "Kedzie (Green)": 21,
                    "Conservatory-Central Park Drive": 22,
                    "Pulaski (Green)": 23,
                    "Cicero (Green)": 24,
                    "Laramie": 25,
                    "Central (Green)": 26,
                    "Austin (Green)": 27,
                    "Ridgeland": 28,
                    "Oak Park (Green)": 29,
                    "Harlem/Lake": 30,
                }
            case 'Orange':
                self.name_to_index = {
                    "Midway": 0,
                    "Pulaski (Orange)": 1,
                    "Kedzie (Orange)": 2,
                    "Western (Orange)": 3,
                    "35th/Archer": 4,
                    "Ashland (Green/Pink)": 5,
                    "Halsted (Orange)": 6,
                    "Roosevelt": 7,
                    "Harold Washington Library-State/Van Buren": 8,
                    "LaSalle/Van Buren": 9,
                    "Quincy": 10,
                    "Washington/Wells": 11,
                    "Clark/Lake": 12,
                    "State/Lake (Loop 'L')": 13,
                    "Washington/Wabash": 14,
                    "Adams/Wabash": 15,
                }
            case 'Purple':
                self.name_to_index = {
                    "Washington/Wells": 0,
                    "Quincy": 1,
                    "LaSalle/Van Buren": 2,
                    "Harold Washington Library-State/Van Buren": 3,
                    "Adams/Wabash": 4,
                    "Washington/Wabash": 5,
                    "State/Lake (Loop 'L')": 6,
                    "Clark/Lake": 7,
                    "Merchandise Mart (Brown/Purple)": 8,
                    "Chicago (Brown/Purple)": 9,
                    "Sedgwick (Brown/Purple)": 10,
                    "Armitage (Brown/Purple)": 11,
                    "Fullerton": 12,
                    "Diversey (Brown/Purple)": 13,
                    "Wellington (Brown/Purple)": 14,
                    "Belmont (Red/Brown/Purple)": 15,
                    "Wilson": 16,
                    "Howard": 17,
                    "South Boulevard": 18,
                    "Main": 19,
                    "Dempster": 20,
                    "Davis": 21,
                    "Foster": 22,
                    "Noyes": 23,
                    "Central (Purple)": 24,
                    "Linden": 25,
                }
            case 'Pink':
                self.name_to_index = {
                    "54th/Cermak": 0,
                    "Cicero (Pink)": 1,
                    "Kostner": 2,
                    "Pulaski (Pink)": 3,
                    "Central Park": 4,
                    "Kedzie (Pink)": 5,
                    "California (Pink)": 6,
                    "Western (Pink)": 7,
                    "Damen (Pink)": 8,
                    "18th": 9,
                    "Polk": 10,
                    "Ashland (Green/Pink)": 11,
                    "Morgan (Green/Pink)": 12,
                    "Clinton (Green/Pink)": 13,
                    "Clark/Lake": 14,
                    "State/Lake (Loop 'L')": 15,
                    "Washington/Wabash": 16,
                    "Adams/Wabash": 17,
                    "Harold Washington Library-State/Van Buren": 18,
                    "LaSalle/Van Buren": 19,
                    "Quincy": 20,
                    "Washington/Wells": 21,
                }
            case 'Yellow':
                self.name_to_index = {
                    "Howard": 0,
                    "Oakton-Skokie": 1,
                    "Dempster-Skokie": 2,
                }

        # precompute helpers used frequently to avoid repeated work
        self.station_names = list(self.name_to_index.keys())
        self.line_directions = directions[args.line]
        self.endpoint_name = (max(self.name_to_index, key=self.name_to_index.get)
                              if isinstance(self.line_directions[1], int)
                              else self.line_directions[1])
        # trip-direction map is built once per API response in get_direction()
        self._trip_direction_map = None

    def station_id_to_name(self, id):
        return self.stop_id_to_name.get(id)

    def station_name_to_index(self, name):
        return self.name_to_index[name]

    def get_direction(self, trip_id, api_dict):
        # Build a trip-id -> direction-name map once per response (cached)
        if self._trip_direction_map is None:
            ld0, ld1 = self.line_directions
            tmap = {}
            for trip in api_dict["data"]["references"]["trips"]:
                if trip["directionId"] == "0":
                    tmap[trip["id"]] = (self.station_names[ld0] if isinstance(ld0, int) else ld0)
                else:
                    tmap[trip["id"]] = (self.station_names[ld1] if isinstance(ld1, int) else ld1)
            self._trip_direction_map = tmap

        try:
            return self._trip_direction_map[trip_id]
        except KeyError:
            raise ValueError(f"Trip id {trip_id} not found")

    def get_next_station(self, trip_dict):
        # be tolerant if status or nextStop missing
        status = trip_dict.get("status") or {}
        next_stop_id = status.get("nextStop")
        if not next_stop_id:
            return "(no next stop)", -1
        name = self.station_id_to_name(next_stop_id)
        if not name:
            return "(unknown stop)", -1
        index = self.station_name_to_index(name)
        return name, index

    def _find_station_index_tolerant(self, station_name: str) -> int:
        # exact match
        if station_name in self.name_to_index:
            return self.name_to_index[station_name]
        # try matching keys without parenthesis e.g. "Garfield (Red)" -> "Garfield"
        name_no_paren = station_name.split(" (")[0]
        for k in self.name_to_index:
            if k.split(" (")[0] == name_no_paren:
                return self.name_to_index[k]
        # substring match (fallback)
        for k in self.name_to_index:
            if station_name in k or k in station_name:
                return self.name_to_index[k]
        # unknown
        raise KeyError(f"unknown station: {station_name}")

    def _seconds_until_arrival(self, prdt_str: str, arrt_str: str) -> float:
        # CTA timestamps are local Chicago times (no zone). Make them timezone-aware
        # using America/Chicago before converting to epoch so comparisons with
        # time.time() are correct regardless of system timezone.
        try:
            tz = ZoneInfo("America/Chicago")
            prd = datetime.fromisoformat(prdt_str)
            arr = datetime.fromisoformat(arrt_str)
            # if timestamps are naive, assume Chicago local time
            if prd.tzinfo is None:
                prd = prd.replace(tzinfo=tz)
            if arr.tzinfo is None:
                arr = arr.replace(tzinfo=tz)
            # remaining seconds until arrival relative to now
            now = time.time()
            remaining = arr.timestamp() - now
            if remaining < 0:
                return 0.0
            return remaining
        except Exception:
            return 0.0

    def get_trains(self, json_str) -> List[Train]:
        api_dict = json.loads(json_str)
        out = []
        # Navigate CTA cached format: ctatt -> route[0] -> train
        try:
            route = api_dict["ctatt"]["route"][0]
            trains = route.get("train", [])
        except Exception as e:
            print(f"Unexpected json structure: {e}")
            return out

        for t in trains:
            try:
                # CTA fields: rn (run/number), destNm (destination), nextStaNm (next station),
                # prdt (prediction timestamp), arrT (arrival timestamp)
                train_id = t.get("rn", "")
                vehicle_id = t.get("rn", "")
                direction = t.get("destNm", "(unknown)")
                next_station_name = t.get("nextStaNm", "(no next stop)")
                next_idx = self._find_station_index_tolerant(next_station_name)
                secs_until = self._seconds_until_arrival(t.get("prdt", ""), t.get("arrT", ""))
                # leg_total and pct_distance_along_trip not available in this feed -> default 0
                tr = Train(
                    id=train_id,
                    vehicle_id=vehicle_id,
                    direction=direction,
                    next_station_index=next_idx,
                    next_station=next_station_name,
                    time_until=secs_until,
                    leg_total=0.0,
                    pct_distance_along_trip=0.0
                )
                out.append(tr)
            except Exception as e:
                print(f"Error processing train {t.get('rn','?')}: {e}")
                continue

        print(colors[args.line] + f"{args.line} Line" + "\033[0m")
        endpoint = self.endpoint_name
        # sort: similar approach to original code; trains heading to endpoint will be ordered accordingly
        for t_sorted in sorted(out, key=lambda x: (-x.next_station_index + (1 if x.direction == endpoint else 0), x.pct_distance_along_trip)):
            print(t_sorted)
        return out

if __name__ == "__main__":
    response = requests.get(url)
    
    if response.status_code == 200:
        traingetter = TrainGetter()
        traingetter.get_trains(json_str=response.text)
        
    else:
        print("Request failed")
        exit()
