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
    direction_id: int
    next_station_index: int
    next_station: str
    time_until: float

    def __str__(self):
        return f"""
{ colors[args.line] + self.direction + "\033[0m" } { "\033[1;44m" + str(self.vehicle_id) + "\033[0m" }
{ "\033[1;33m" + self.next_station } in {round(self.time_until)}s\033[0m"""

class TrainGetter():
    def __init__(self) -> None:
        self.stop_id_to_name = {}
        match args.line:
            case 'Red':
                self.stop_id_to_index = {
                    40450: [0, "95th/Dan Ryan"],
                    41430: [1, "87th"],
                    40240: [2, "79th"],
                    40990: [3, "69th"],
                    40910: [4, "63rd"],
                    41170: [5, "Garfield (Red)"],
                    41230: [6, "47th (Red)"],
                    40190: [7, "Sox-35th"],
                    41000: [8, "Cermak-Chinatown"],
                    41400: [9, "Roosevelt"],
                    41490: [10, "Harrison"],
                    40560: [11, "Jackson (Red)"],
                    41090: [12, "Monroe (Red)"],
                    41660: [13, "Lake (Subway)"],
                    40330: [14, "Grand (Red)"],
                    41450: [15, "Chicago (Red)"],
                    40630: [16, "Clark/Division"],
                    40650: [17, "North/Clybourn"],
                    41220: [18, "Fullerton"],
                    41320: [19, "Belmont (Red/Brown/Purple)"],
                    41420: [20, "Addison (Red)"],
                    40080: [21, "Sheridan"],
                    40540: [22, "Wilson"],
                    40770: [23, "Lawrence"],
                    41200: [24, "Argyle"],
                    40340: [25, "Berwyn"],
                    41380: [26, "Bryn Mawr"],
                    40880: [27, "Thorndale"],
                    40760: [28, "Granville"],
                    41300: [29, "Loyola"],
                    40100: [30, "Morse"],
                    41190: [31, "Jarvis"],
                    40900: [32, "Howard"]
                }
            case 'Blue':
                self.stop_id_to_index = {
                    40390: [0, "Forest Park"],
                    40980: [1, "Harlem (Blue - Forest Park Branch)"],
                    40180: [2, "Oak Park (Blue)"],
                    40010: [3, "Austin (Blue)"],
                    40970: [4, "Cicero (Blue)"],
                    40920: [5, "Pulaski (Blue)"],
                    40250: [6, "Kedzie-Homan"],
                    40220: [7, "Western (Blue - Forest Park Branch)"],
                    40810: [8, "Illinois Medical District"],
                    40470: [9, "Racine"],
                    40350: [10, "UIC-Halsted"],
                    40430: [11, "Clinton (Blue)"],
                    41340: [12, "LaSalle"],
                    40070: [13, "Jackson (Blue)"],
                    40790: [14, "Monroe (Blue)"],
                    40370: [15, "Washington"],
                    40380: [16, "Clark/Lake"],
                    40490: [17, "Grand (Blue)"],
                    41410: [18, "Chicago (Blue)"],
                    40320: [19, "Division"],
                    40590: [20, "Damen (Blue)"],
                    40670: [21, "Western (Blue - O'Hare Branch)"],
                    40570: [22, "California (Blue)"],
                    41020: [23, "Logan Square"],
                    40060: [24, "Belmont (Blue)"],
                    41240: [25, "Addison (Blue)"],
                    40550: [26, "Irving Park (Blue)"],
                    41330: [27, "Montrose (Blue)"],
                    41280: [28, "Jefferson Park Transit Center"],
                    40750: [29, "Harlem (Blue - O'Hare Branch)"],
                    40230: [30, "Cumberland"],
                    40820: [31, "Rosemont"],
                    40890: [32, "O'Hare"]
                }
            case 'Brown':
                self.stop_id_to_index = {
                    40380: [0, "Clark/Lake"],
                    40260: [1, "State/Lake (Loop 'L')"],
                    41700: [2, "Washington/Wabash"],
                    40680: [3, "Adams/Wabash"],
                    40850: [4, "Harold Washington Library-State/Van Buren"],
                    40160: [5, "LaSalle/Van Buren"],
                    40040: [6, "Quincy"],
                    40730: [7, "Washington/Wells"],
                    40460: [8, "Merchandise Mart (Brown/Purple)"],
                    40710: [9, "Chicago (Brown/Purple)"],
                    40800: [10, "Sedgwick (Brown/Purple)"],
                    40660: [11, "Armitage (Brown/Purple)"],
                    41220: [12, "Fullerton"],
                    40530: [13, "Diversey (Brown/Purple)"],
                    41210: [14, "Wellington (Brown/Purple)"],
                    41320: [15, "Belmont (Red/Brown/Purple)"],
                    40360: [16, "Southport"],
                    41310: [17, "Paulina"],
                    41440: [18, "Addison (Brown)"],
                    41460: [19, "Irving Park (Brown)"],
                    41500: [20, "Montrose (Brown)"],
                    40090: [21, "Damen (Brown)"],
                    41480: [22, "Western (Brown)"],
                    41010: [23, "Rockwell"],
                    40870: [24, "Francisco"],
                    41180: [25, "Kedzie (Brown)"],
                    41290: [26, "Kimball"]
                }
            case 'Green':
                self.stop_id_to_index = {
                    40290: [0, "Ashland/63rd"],
                    40940: [1, "Halsted (Green)"],
                    40720: [2, "Cottage Grove"],
                    41140: [3, "King Drive"],
                    40510: [4, "Garfield (Green)"],
                    40130: [5, "51st"],
                    41080: [6, "47th (Green)"],
                    41270: [7, "43rd"],
                    40300: [8, "Indiana"],
                    41120: [9, "35th-Bronzeville-IIT"],
                    41690: [10, "Cermak-McCormick Place"],
                    41400: [11, "Roosevelt"],
                    40680: [12, "Adams/Wabash"],
                    41700: [13, "Washington/Wabash"],
                    40260: [14, "State/Lake (Loop 'L')"],
                    40380: [15, "Clark/Lake"],
                    41160: [16, "Clinton (Green/Pink)"],
                    41510: [17, "Morgan (Green/Pink)"],
                    40170: [18, "Ashland (Green/Pink)"],
                    41710: [19, "Damen (Green)"],
                    41360: [20, "California (Green)"],
                    41070: [21, "Kedzie (Green)"],
                    41670: [22, "Conservatory-Central Park Drive"],
                    40030: [23, "Pulaski (Green)"],
                    40480: [24, "Cicero (Green)"],
                    40700: [25, "Laramie"],
                    40280: [26, "Central (Green)"],
                    41260: [27, "Austin (Green)"],
                    40610: [28, "Ridgeland"],
                    41350: [29, "Oak Park (Green)"],
                    40020: [30, "Harlem/Lake"]
                }
            case 'Orange':
                self.stop_id_to_index = {
                    40930: [0, "Midway"],
                    40960: [1, "Pulaski (Orange)"],
                    41150: [2, "Kedzie (Orange)"],
                    40310: [3, "Western (Orange)"],
                    40120: [4, "35th/Archer"],
                    41060: [5, "Ashland (Orange)"],
                    41130: [6, "Halsted (Orange)"],
                    41400: [7, "Roosevelt"],
                    40850: [8, "Harold Washington Library-State/Van Buren"],
                    40160: [9, "LaSalle/Van Buren"],
                    40040: [10, "Quincy"],
                    40730: [11, "Washington/Wells"],
                    40380: [12, "Clark/Lake"],
                    40260: [13, "State/Lake (Loop 'L')"],
                    41700: [14, "Washington/Wabash"],
                    40680: [15, "Adams/Wabash"]
                }
            case 'Purple':
                self.stop_id_to_index = {
                    40730: [0, "Washington/Wells"],
                    40040: [1, "Quincy"],
                    40160: [2, "LaSalle/Van Buren"],
                    40850: [3, "Harold Washington Library-State/Van Buren"],
                    40680: [4, "Adams/Wabash"],
                    41700: [5, "Washington/Wabash"],
                    40260: [6, "State/Lake (Loop 'L')"],
                    40380: [7, "Clark/Lake"],
                    40460: [8, "Merchandise Mart (Brown/Purple)"],
                    40710: [9, "Chicago (Brown/Purple)"],
                    40800: [10, "Sedgwick (Brown/Purple)"],
                    40660: [11, "Armitage (Brown/Purple)"],
                    41220: [12, "Fullerton"],
                    40530: [13, "Diversey (Brown/Purple)"],
                    41210: [14, "Wellington (Brown/Purple)"],
                    41320: [15, "Belmont (Red/Brown/Purple)"],
                    40540: [16, "Wilson"],
                    40900: [17, "Howard"],
                    40840: [18, "South Boulevard"],
                    40270: [19, "Main"],
                    40690: [20, "Dempster"],
                    40050: [21, "Davis"],
                    40520: [22, "Foster"],
                    40400: [23, "Noyes"],
                    41250: [24, "Central (Purple)"],
                    41050: [25, "Linden"]
                }
            case 'Pink':
                self.stop_id_to_index = {
                    40580: [0, "54th/Cermak"],
                    40420: [1, "Cicero (Pink)"],
                    40600: [2, "Kostner"],
                    40150: [3, "Pulaski (Pink)"],
                    40780: [4, "Central Park"],
                    41040: [5, "Kedzie (Pink)"],
                    40440: [6, "California (Pink)"],
                    40740: [7, "Western (Pink)"],
                    40210: [8, "Damen (Pink)"],
                    40830: [9, "18th"],
                    41030: [10, "Polk"],
                    40170: [11, "Ashland (Green/Pink)"],
                    41510: [12, "Morgan (Green/Pink)"],
                    41160: [13, "Clinton (Green/Pink)"],
                    40380: [14, "Clark/Lake"],
                    40260: [15, "State/Lake (Loop 'L')"],
                    41700: [16, "Washington/Wabash"],
                    40680: [17, "Adams/Wabash"],
                    40850: [18, "Harold Washington Library-State/Van Buren"],
                    40160: [19, "LaSalle/Van Buren"],
                    40040: [20, "Quincy"],
                    40730: [21, "Washington/Wells"]
                }
            case 'Yellow':
                self.stop_id_to_index = {
                    40900: [0, "Howard"],
                    41680: [1, "Oakton-Skokie"],
                    40140: [2, "Dempster-Skokie"]
                }

    def station_id_to_index(self, id):
        res = self.stop_id_to_index.get(id, None)
        if res is not None:
            return res[0]
        return None
    
    def station_id_to_name(self, id):
        res = self.stop_id_to_index.get(id, None)
        if res is not None:
            return res[1]
        return None

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
                # nextStaId (next station ID), prdt (prediction timestamp), arrT (arrival timestamp)
                train_id = t.get("rn", "")
                vehicle_id = t.get("rn", "")
                direction = t.get("destNm", "(unknown)")
                direction_id = t.get("trDr", -1)
                next_station_name = t.get("nextStaNm", "(no next stop)")
                next_idx = int(t.get("nextStaId", -1))
                secs_until = self._seconds_until_arrival(t.get("prdt", ""), t.get("arrT", ""))

                tr = Train(
                    id=train_id,
                    vehicle_id=vehicle_id,
                    direction=direction,
                    direction_id=direction_id,
                    next_station_index=next_idx,
                    next_station=next_station_name,
                    time_until=secs_until
                )
                out.append(tr)
            except Exception as e:
                print(f"Error processing train {t.get('rn','?')}: {e}")
                continue

        print(colors[args.line] + f"{args.line} Line" + "\033[0m")
        for t_sorted in sorted(out, key=lambda x: ((-self.stop_id_to_index[x.next_station_index][0] + (1 if x.direction_id == "1" else 0), ((-1 if x.direction_id == "1" else 1)) * x.time_until))):
            print(t_sorted)
            # print((-self.stop_id_to_index[t_sorted.next_station_index][0] + (1 if t_sorted.direction_id == "1" else 0), ((-1 if t_sorted.direction_id == "1" else 1)) * t_sorted.time_until))
        return out

if __name__ == "__main__":
    response = requests.get(url)
    
    if response.status_code == 200:
        traingetter = TrainGetter()
        traingetter.get_trains(json_str=response.text)
        
    else:
        print("Request failed")
        exit()
