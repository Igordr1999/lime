from data.models import Country, AircraftType, Aircraft, Pilot, Steward
from data.models import Airport as Airport_lime
from data.models import Airline as Airline_lime
from django.contrib.auth.models import User
import requests, grequests
import sys
import random


class FR24:
    base_url = "http://www.flightradar24.com"
    api_url = "http://data-live.flightradar24.com"

    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36 OPR/51.0.2830.55"
    }

    static_data = {
        'airports': '/_json/airports.php',
        'airlines': '/_json/airlines.php',
    }

    dynamic_data = {
        'radar': '/zones/fcgi/feed.js',
        'flight': '/clickhandler/'
    }

    def search_airport(self, iata):
        airports = self.get_airports()
        for airport in airports:
            if airport.iata == iata:
                return airport

        # Not found
        return False

    def search_airline(self, icao):
        airlines = self.get_airlines()
        for airline in airlines:
            if airline.icao == icao:
                return airline

        # Not found
        return False

    def get_airports(self):
        url = self.base_url + self.static_data["airports"]
        rows = self.simple_request(url=url)["rows"]
        airports = []
        for airport in rows:
            a = Airport(
                name=airport["name"],
                iata=airport["iata"],
                icao=airport["icao"],
                lat=airport["lat"],
                lon=airport["lon"],
                country=airport["country"],
                alt=airport["alt"]
            )
            airports.append(a)
        return airports

    def get_airlines(self):
        url = self.base_url + self.static_data["airlines"]
        rows = self.simple_request(url=url)["rows"]
        airlines = []
        for airline in rows:
            a = Airline(
                name=airline["Name"],
                iata=airline["Code"],
                icao=airline["ICAO"],
            )
            airlines.append(a)
        return airlines

    def get_flight(self, flight):
        version = 1.5
        url = self.api_url + self.dynamic_data["flight"]
        params = {
            'version': version,
            'flight': flight,
        }
        return self.simple_request(url=url, params=params)

    def get_flights_by_airline(self, airline):
        url = self.api_url + self.dynamic_data["radar"]
        params = {
            'airline': airline,
        }
        return self.simple_request(url=url, params=params)

    def get_flights_by_airport(self, airport):
        url = self.api_url + self.dynamic_data["radar"]
        params = {
            'airport': airport,
        }
        return self.simple_request(url=url, params=params)

    def get_flights_in_zone(self, north, south, west, east):
        url = self.api_url + self.dynamic_data["radar"]
        bounds = "{north},{south},{west},{east}".format(north=north, south=south, west=west, east=east)
        params = {
            'bounds': bounds,
        }
        return self.simple_request(url=url, params=params)

    @staticmethod
    def check_request(data):
        if data.status_code == 200:
            return data.json()
        else:
            error_text = "Error 1. Server return request with {} code.".format(data.status_code)
            print(error_text)
            sys.exit()
            # raise Exception(error_text)

    def simple_request(self, url, params={}):
        data = requests.get(url=url, headers=self.base_headers, params=params)
        data_json = self.check_request(data=data)
        return data_json

    def get_icao_airlines(self):
        c = self.get_airlines()
        mas = []
        for a in c["rows"]:
            s = a["ICAO"]
            mas.append(s)
        return mas,

    def full_url(self, url, params):
        full = self.api_url + self.dynamic_data["radar"]+"?"
        for key in params:
            full += key+"="+params[key]+"&"
        full = full[:-1]
        return full

    def clever_request(self, urls):
        rs = (grequests.get(u, headers=self.base_headers) for u in urls)
        data_json = []
        for r in grequests.imap(rs, size=1000):
            data_json.append(self.check_request(data=r))

            # print(r.status_code, r.url, r.json())
        return data_json


    @staticmethod
    def get_many_params(params):
        s = ""
        for param in params:
            s = s + param + ","
        s = s[:-1]
        return s

    def get_flights(self):
        url = self.api_url + self.dynamic_data["radar"]
        airlines = self.get_icao_airlines()

        # Max lenght URL is 2000 symbols, but this URL is >5200 symbols.
        # That's why I divide into three URLs
        a = self.get_many_params(airlines[:500])
        b = self.get_many_params(airlines[501:1000])
        c = self.get_many_params(airlines[1001:])

        urls = []
        for n in [a, b, c]:
            params = {
                'airline': n,
            }
            urls.append(self.full_url(url=url, params=params))
        answer = self.clever_request(urls)

        all_flights = []
        stop_words = ["full_count", "version"]
        for n in answer:
            for flight in n:
                if flight not in stop_words:
                    d = [flight, n[flight]]
                    all_flights.append(d)

        return all_flights

    def print_flights_by_lines(self):
        flights = self.get_flights()
        for f in flights:
            print(f)

    def print_flights_all_data(self):
        flights = self.get_flights()
        for f in flights:
            key = f[0]
            mode_s = f[1][0]
            lat = f[1][1]
            lng = f[1][2]
            track = f[1][3]
            alt = f[1][4]
            ground_spend = f[1][5]
            squawk = f[1][6]
            radar = f[1][7]
            type_aircraft = f[1][8]
            reg_code = f[1][9]
            timestamp = f[1][10]
            from_airport = f[1][11]
            to_airport = f[1][12]
            iata_flights = f[1][13]
            icao_flights = f[1][16]
            airline = f[1][18]
            print(key, mode_s, lat, lng, track, alt, ground_spend, squawk, radar, type_aircraft, reg_code,
                  timestamp, from_airport, to_airport, icao_flights, iata_flights, airline)

    def get_countries(self):
        airports = self.get_airports()
        countries = []
        for i in airports:
            if i.country in countries:
                pass
            else:
                countries.append(i.country)
        return sorted(countries)


class Airport:
    def __init__(self, name, iata, icao, lat, lon, country, alt):
        self.name = name
        self.iata = iata
        self.icao = icao
        self.lat = lat
        self.lon = lon
        self.country = country
        self.alt = alt

    def __str__(self):
        return self.name


class Airline:
    def __init__(self, name, iata, icao):
        self.name = name
        self.iata = iata
        self.icao = icao

    def __str__(self):
        return self.name


def create_countries():
    a = FR24().get_countries()
    for i in a:
        Country.objects.create(name=i.name)


def create_airports():
    a = FR24().get_airports()
    for i in a:
        country = Country.objects.get(name=i.country)
        Airport_lime.objects.get_or_create(
            name=i.name,
            defaults={
                'iata_code': i.iata,
                'icao_code': i.icao,
                'lat': i.lat,
                'lng': i.lon,
                'country': country,
            }
        )


name_man = ["Александр", "Денис", "Сергей", "Андрей", "	Дмитрий", "	Максим", "Алексей", "Артем", "Иван", "Роман",
                "Степан", "Николай", "Николай", "Владимир", "Тимофей", "Антон", "Кирилл", "Владислав",
                "Валерий", "Евгений", "Павел", "Илья", "Виктор", "Игорь"]
name_woman = ["Александра", "Татьяна", "Софья", "Кристина", "Ева", "Виктория", "Елизавета", "Анастасия",
                  "Алина", "Марина", "Юлия", "Полина", "Мария", "Екатерина", "Анна", "Диана", "Дарья", "Валерия",
                  "Ольга", "Вероника", "Наталья", "Алина", "Дана", "Арина"]
last_name = ["Смирнов", "Иванов", "Кузнецов", "Соколов", "Попов", "Лебедев", "Козлов", "Новиков", "Морозов",
            "Петров", "Волков", "Соловьёв", "Васильев", "Зайцев", "Павлов", "Семёнов", "Голубев", "Виноградов",
            "Богданов", "Воробьёв", "Фёдоров", "Михайлов", "Беляев", "Тарасов", "Белов", "Комаров", "Орлов",
            "Киселёв", "Макаров", "Андреев", "Ковалёв", "Ильин", "Гусев", "Титов", "Кузьмин", "Кудрявцев",
            "Баранов", "Куликов", "Алексеев", "Степанов", "Яковлев", "Сорокин", "Сергеев", "Романов",
            "Захаров", "Борисов", "Королёв", "Лазарев", "Медведев", "Ершов", "Никитин", "Соболев", "Рябов",
            "Поляков", "Цветков", "Данилов", "Жуков", "Фролов", "Журавлёв", "Николаев"]
patronymic_man = ["Александрович", "Николаевич", "Владимирович", "Иванович", "Петрович", "Сергеевич", "Денисович",
             "Михайлович", "Артемович", "Викторович", "Евгеньевич", "Ивановна"]
patronymic_woman = ["Владимировна", "Александровна", "Николаевна", "Сергеевна", "Николаевна", "Денисовна", "Артемовна",
               "Викторовна", "Евгеньевна", "Ивановна", "Петровна"]
types_aircrafts = [
    {
        "icaoCode": "A124",
        "iataCode": "A4F",
        "description": "Antonov AN-124 Ruslan"
    },
    {
        "icaoCode": "A140",
        "iataCode": "A40",
        "description": "Antonov AN-140"
    },
    {
        "icaoCode": "A225",
        "iataCode": "A25",
        "description": "Antonov An-225 Mriya"
    },
    {
        "icaoCode": "A306",
        "iataCode": "ABY",
        "description": "Airbus A300-600"
    },
    {
        "icaoCode": "A30B",
        "iataCode": "AB3",
        "description": "Airbus A300"
    },
    {
        "icaoCode": "A310",
        "iataCode": "310",
        "description": "Airbus A310"
    },
    {
        "icaoCode": "A318",
        "iataCode": "318",
        "description": "Airbus A318"
    },
    {
        "icaoCode": "A319",
        "iataCode": "319",
        "description": "Airbus A319"
    },
    {
        "icaoCode": "A320",
        "iataCode": "320",
        "description": "Airbus A320"
    },
    {
        "icaoCode": "A321",
        "iataCode": "321",
        "description": "Airbus A321"
    },
    {
        "icaoCode": "A330",
        "iataCode": "330",
        "description": "Airbus A330"
    },
    {
        "icaoCode": "A332",
        "iataCode": "332",
        "description": "Airbus A330-200"
    },
    {
        "icaoCode": "A333",
        "iataCode": "333",
        "description": "Airbus A330-300"
    },
    {
        "icaoCode": "A338",
        "iataCode": "338",
        "description": "Airbus A330-800"
    },
    {
        "icaoCode": "A339",
        "iataCode": "339",
        "description": "Airbus A330-900"
    },
    {
        "icaoCode": "A340",
        "iataCode": "340",
        "description": "Airbus A340"
    },
    {
        "icaoCode": "A342",
        "iataCode": "342",
        "description": "Airbus A340-200"
    },
    {
        "icaoCode": "A343",
        "iataCode": "343",
        "description": "Airbus A340-300"
    },
    {
        "icaoCode": "A345",
        "iataCode": "345",
        "description": "Airbus A340-500"
    },
    {
        "icaoCode": "A346",
        "iataCode": "346",
        "description": "Airbus A340-600"
    },
    {
        "icaoCode": "A350",
        "iataCode": "350",
        "description": "Airbus A350"
    },
    {
        "icaoCode": "A358",
        "iataCode": "358",
        "description": "Airbus A350-800"
    },
    {
        "icaoCode": "A359",
        "iataCode": "359",
        "description": "Airbus A350-900"
    },
    {
        "icaoCode": "A35K",
        "iataCode": "351",
        "description": "Airbus A350-1000[2]"
    },
    {
        "icaoCode": "A388",
        "iataCode": "380",
        "description": "Airbus A380-800"
    },
    {
        "icaoCode": "A3ST",
        "iataCode": "ABB",
        "description": "Airbus A300-600ST Beluga Freighter"
    },
    {
        "icaoCode": "A748",
        "iataCode": "HS7",
        "description": "Hawker Siddeley HS 748"
    },
    {
        "icaoCode": "AC68",
        "iataCode": "ACP",
        "description": "Gulfstream/Rockwell (Aero) Commander"
    },
    {
        "icaoCode": "AC90",
        "iataCode": "ACT",
        "description": "Gulfstream/Rockwell (Aero) Turbo Commander"
    },
    {
        "icaoCode": "AN12",
        "iataCode": "ANF",
        "description": "Antonov AN-12"
    },
    {
        "icaoCode": "AN24",
        "iataCode": "AN4",
        "description": "Antonov AN-24"
    },
    {
        "icaoCode": "AN26",
        "iataCode": "A26",
        "description": "Antonov AN-26"
    },
    {
        "icaoCode": "AN28",
        "iataCode": "A28",
        "description": "Antonov AN-28"
    },
    {
        "icaoCode": "AN30",
        "iataCode": "A30",
        "description": "Antonov AN-30"
    },
    {
        "icaoCode": "AN32",
        "iataCode": "A32",
        "description": "Antonov AN-32"
    },
    {
        "icaoCode": "AN72",
        "iataCode": "AN7",
        "description": "Antonov AN-72 / AN-74"
    },
    {
        "icaoCode": "AS32",
        "iataCode": "APH",
        "description": "Eurocopter AS332 Super Puma"
    },
    {
        "icaoCode": "AT43",
        "iataCode": "AT4",
        "description": "Aerospatiale/Alenia ATR 42-300 / 320"
    },
    {
        "icaoCode": "AT45",
        "iataCode": "AT5",
        "description": "Aerospatiale/Alenia ATR 42-500"
    },
    {
        "icaoCode": "AT46",
        "iataCode": "ATR",
        "description": "Aerospatiale/Alenia ATR 42-600"
    },
    {
        "icaoCode": "AT72",
        "iataCode": "AT7",
        "description": "Aerospatiale/Alenia ATR 72"
    },
    {
        "icaoCode": "AT73",
        "iataCode": "ATR",
        "description": "Aerospatiale/Alenia ATR 72-200 series"
    },
    {
        "icaoCode": "AT75",
        "iataCode": "ATR",
        "description": "Aerospatiale/Alenia ATR 72-500"
    },
    {
        "icaoCode": "AT76",
        "iataCode": "ATR",
        "description": "Aerospatiale/Alenia ATR 72-600"
    },
    {
        "icaoCode": "ATL",
        "iataCode": "ATL",
        "description": "Robin ATL"
    },
    {
        "icaoCode": "ATP",
        "iataCode": "ATP",
        "description": "British Aerospace ATP"
    },
    {
        "icaoCode": "B105",
        "iataCode": "MBH",
        "description": "Eurocopter (MBB) Bo.105"
    },
    {
        "icaoCode": "B190",
        "iataCode": "BEH",
        "description": "Beechcraft 1900"
    },
    {
        "icaoCode": "B212",
        "iataCode": "BH2",
        "description": "Bell 212"
    },
    {
        "icaoCode": "B412",
        "iataCode": "BH2",
        "description": "Bell 412"
    },
    {
        "icaoCode": "B429",
        "iataCode": "BH2",
        "description": "Bell 429"
    },
    {
        "icaoCode": "B461",
        "iataCode": "141",
        "description": "BAe 146-100"
    },
    {
        "icaoCode": "B462",
        "iataCode": "142",
        "description": "BAe 146-200"
    },
    {
        "icaoCode": "B463",
        "iataCode": "143",
        "description": "BAe 146-300"
    },
    {
        "icaoCode": "B703",
        "iataCode": "703",
        "description": "Boeing 707"
    },
    {
        "icaoCode": "B712",
        "iataCode": "717",
        "description": "Boeing 717"
    },
    {
        "icaoCode": "B720",
        "iataCode": "B72",
        "description": "Boeing 720B"
    },
    {
        "icaoCode": "B721",
        "iataCode": "721",
        "description": "Boeing 727-100"
    },
    {
        "icaoCode": "B722",
        "iataCode": "722",
        "description": "Boeing 727-200"
    },
    {
        "icaoCode": "B731",
        "iataCode": "731",
        "description": "Boeing 737-100"
    },
    {
        "icaoCode": "B732",
        "iataCode": "732",
        "description": "Boeing 737-200"
    },
    {
        "icaoCode": "B733",
        "iataCode": "733",
        "description": "Boeing 737-300"
    },
    {
        "icaoCode": "B734",
        "iataCode": "734",
        "description": "Boeing 737-400"
    },
    {
        "icaoCode": "B735",
        "iataCode": "735",
        "description": "Boeing 737-500"
    },
    {
        "icaoCode": "B736",
        "iataCode": "736",
        "description": "Boeing 737-600"
    },
    {
        "icaoCode": "B737",
        "iataCode": "73G",
        "description": "Boeing 737-700"
    },
    {
        "icaoCode": "B738",
        "iataCode": "738",
        "description": "Boeing 737-800"
    },
    {
        "icaoCode": "B739",
        "iataCode": "739",
        "description": "Boeing 737-900"
    },
    {
        "icaoCode": "B741",
        "iataCode": "741",
        "description": "Boeing 747-100"
    },
    {
        "icaoCode": "B742",
        "iataCode": "742",
        "description": "Boeing 747-200"
    },
    {
        "icaoCode": "B743",
        "iataCode": "743",
        "description": "Boeing 747-300"
    },
    {
        "icaoCode": "B744",
        "iataCode": "744",
        "description": "Boeing 747-400"
    },
    {
        "icaoCode": "B748",
        "iataCode": "748",
        "description": "Boeing 747-8"
    },
    {
        "icaoCode": "B74R",
        "iataCode": "74R",
        "description": "Boeing 747SR"
    },
    {
        "icaoCode": "B74S",
        "iataCode": "74L",
        "description": "Boeing 747SP"
    },
    {
        "icaoCode": "B752",
        "iataCode": "752",
        "description": "Boeing 757-200"
    },
    {
        "icaoCode": "B753",
        "iataCode": "753",
        "description": "Boeing 757-300"
    },
    {
        "icaoCode": "B762",
        "iataCode": "762",
        "description": "Boeing 767-200"
    },
    {
        "icaoCode": "B763",
        "iataCode": "763",
        "description": "Boeing 767-300"
    },
    {
        "icaoCode": "B764",
        "iataCode": "764",
        "description": "Boeing 767-400"
    },
    {
        "icaoCode": "B772",
        "iataCode": "772",
        "description": "Boeing 777-200 / Boeing 777-200ER"
    },
    {
        "icaoCode": "B77L",
        "iataCode": "77L",
        "description": "Boeing 777-200LR / Boeing 777F"
    },
    {
        "icaoCode": "B773",
        "iataCode": "773",
        "description": "Boeing 777-300"
    },
    {
        "icaoCode": "B77W",
        "iataCode": "77W",
        "description": "Boeing 777-300ER"
    },
    {
        "icaoCode": "B783",
        "iataCode": "783",
        "description": "Boeing 787-3[3]"
    },
    {
        "icaoCode": "B788",
        "iataCode": "788",
        "description": "Boeing 787-8[3]"
    },
    {
        "icaoCode": "B789",
        "iataCode": "789",
        "description": "Boeing 787-9[3]"
    },
    {
        "icaoCode": "B78J",
        "iataCode": "78J",
        "description": "Boeing 787-10[4]"
    },
    {
        "icaoCode": "BA11",
        "iataCode": "B11",
        "description": "British Aerospace (BAC) One Eleven"
    },
    {
        "icaoCode": "BCS1",
        "iataCode": "CS1",
        "description": "Bombardier CS100"
    },
    {
        "icaoCode": "BCS3",
        "iataCode": "CS3",
        "description": "Bombardier CS300"
    },
    {
        "icaoCode": "BELF",
        "iataCode": "SHB",
        "description": "Shorts SC-5 Belfast"
    },
    {
        "icaoCode": "BLCF",
        "iataCode": "74B",
        "description": "Boeing 747 LCF Dreamlifter"
    },
    {
        "icaoCode": "BN2P",
        "iataCode": "BNI",
        "description": "Pilatus Britten-Norman BN-2A/B Islander"
    },
    {
        "icaoCode": "C130",
        "iataCode": "LOH",
        "description": "Lockheed L-182 / 282 / 382 (L-100) Hercules"
    },
    {
        "icaoCode": "C162",
        "iataCode": "CN1",
        "description": "Cessna 162"
    },
    {
        "icaoCode": "C172",
        "iataCode": "CN1",
        "description": "Cessna 172"
    },
    {
        "icaoCode": "C72R",
        "iataCode": "CN1",
        "description": "Cessna 172 Cutlass RG"
    },
    {
        "icaoCode": "C77R",
        "iataCode": "CN1",
        "description": "Cessna 177 Cardinal RG"
    },
    {
        "icaoCode": "C182",
        "iataCode": "CN1",
        "description": "Cessna 182 Skylane"
    },
    {
        "icaoCode": "C208",
        "iataCode": "CN1",
        "description": "Cessna 208 Caravan"
    },
    {
        "icaoCode": "C210",
        "iataCode": "CN1",
        "description": "Cessna 210 Centurion"
    },
    {
        "icaoCode": "C212",
        "iataCode": "CS2",
        "description": "CASA / IPTN 212 Aviocar"
    },
    {
        "icaoCode": "C25A",
        "iataCode": "CNJ",
        "description": "Cessna Citation CJ2"
    },
    {
        "icaoCode": "C25B",
        "iataCode": "CNJ",
        "description": "Cessna Citation CJ3"
    },
    {
        "icaoCode": "C25C",
        "iataCode": "CNJ",
        "description": "Cessna Citation CJ4"
    },
    {
        "icaoCode": "C46",
        "iataCode": "CWC",
        "description": "Curtiss C-46 Commando"
    },
    {
        "icaoCode": "C500",
        "iataCode": "CNJ",
        "description": "Cessna Citation I"
    },
    {
        "icaoCode": "C510",
        "iataCode": "CNJ",
        "description": "Cessna Citation Mustang"
    },
    {
        "icaoCode": "C525",
        "iataCode": "CNJ",
        "description": "Cessna CitationJet"
    },
    {
        "icaoCode": "C550",
        "iataCode": "CNJ",
        "description": "Cessna Citation II"
    },
    {
        "icaoCode": "C560",
        "iataCode": "CNJ",
        "description": "Cessna Citation V"
    },
    {
        "icaoCode": "C56X",
        "iataCode": "CNJ",
        "description": "Cessna Citation Excel"
    },
    {
        "icaoCode": "C650",
        "iataCode": "CNJ",
        "description": "Cessna Citation III"
    },
    {
        "icaoCode": "C680",
        "iataCode": "CNJ",
        "description": "Cessna Citation Sovereign"
    },
    {
        "icaoCode": "C750",
        "iataCode": "CNJ",
        "description": "Cessna Citation X"
    },
    {
        "icaoCode": "CL2T",
        "iataCode": "",
        "description": "Bombardier 415"
    },
    {
        "icaoCode": "CL44",
        "iataCode": "CL4",
        "description": "Canadair CL-44"
    },
    {
        "icaoCode": "CL60",
        "iataCode": "CCJ",
        "description": "Canadair Challenger"
    },
    {
        "icaoCode": "CN35",
        "iataCode": "CS5",
        "description": "CASA/IPTN CN-235"
    },
    {
        "icaoCode": "CONC",
        "iataCode": "SSC",
        "description": "Aerospatiale/BAC Concorde"
    },
    {
        "icaoCode": "CONI",
        "iataCode": "L49",
        "description": "Lockheed L-1049 Super Constellation"
    },
    {
        "icaoCode": "COUC",
        "iataCode": "HEC",
        "description": "Helio H-250 Courier / H-295 / 385 Super Courier"
    },
    {
        "icaoCode": "CRJ1",
        "iataCode": "CR1",
        "description": "Canadair Regional Jet 100"
    },
    {
        "icaoCode": "CRJ2",
        "iataCode": "CR2",
        "description": "Canadair Regional Jet 200"
    },
    {
        "icaoCode": "CRJ7",
        "iataCode": "CR7",
        "description": "Canadair Regional Jet 700"
    },
    {
        "icaoCode": "CRJ9",
        "iataCode": "CR9",
        "description": "Canadair Regional Jet 900"
    },
    {
        "icaoCode": "CRJX",
        "iataCode": "CRK",
        "description": "Canadair Regional Jet 1000"
    },
    {
        "icaoCode": "CVLP",
        "iataCode": "CV4",
        "description": "Convair CV-240 & -440"
    },
    {
        "icaoCode": "CVLT",
        "iataCode": "CV5",
        "description": "Convair CV-580"
    },
    {
        "icaoCode": "D228",
        "iataCode": "D28",
        "description": "Fairchild Dornier Do.228"
    },
    {
        "icaoCode": "D328",
        "iataCode": "D38",
        "description": "Fairchild Dornier Do.328"
    },
    {
        "icaoCode": "DC10",
        "iataCode": "D10",
        "description": "Douglas DC-10"
    },
    {
        "icaoCode": "DC3",
        "iataCode": "D3F",
        "description": "Douglas DC-3"
    },
    {
        "icaoCode": "DC6",
        "iataCode": "D6F",
        "description": "Douglas DC-6"
    },
    {
        "icaoCode": "DC85",
        "iataCode": "D8T",
        "description": "Douglas DC-8-50"
    },
    {
        "icaoCode": "DC86",
        "iataCode": "D8L",
        "description": "Douglas DC-8-62"
    },
    {
        "icaoCode": "DC87",
        "iataCode": "D8Q",
        "description": "Douglas DC-8-72"
    },
    {
        "icaoCode": "DC9",
        "iataCode": "DC9",
        "description": "Douglas DC-9"
    },
    {
        "icaoCode": "DC91",
        "iataCode": "D91",
        "description": "Douglas DC-9-10"
    },
    {
        "icaoCode": "DC92",
        "iataCode": "D92",
        "description": "Douglas DC-9-20"
    },
    {
        "icaoCode": "DC93",
        "iataCode": "D93",
        "description": "Douglas DC-9-30"
    },
    {
        "icaoCode": "DC94",
        "iataCode": "D94",
        "description": "Douglas DC-9-40"
    },
    {
        "icaoCode": "DC95",
        "iataCode": "D95",
        "description": "Douglas DC-9-50"
    },
    {
        "icaoCode": "DH2T",
        "iataCode": "DHR",
        "description": "De Havilland Canada DHC-2 Turbo-Beaver"
    },
    {
        "icaoCode": "DH8A",
        "iataCode": "DH1",
        "description": "De Havilland Canada DHC-8-100 Dash 8 / 8Q"
    },
    {
        "icaoCode": "DH8B",
        "iataCode": "DH2",
        "description": "De Havilland Canada DHC-8-200 Dash 8 / 8Q"
    },
    {
        "icaoCode": "DH8C",
        "iataCode": "DH3",
        "description": "De Havilland Canada DHC-8-300 Dash 8 / 8Q"
    },
    {
        "icaoCode": "DH8D",
        "iataCode": "DH4",
        "description": "De Havilland Canada DHC-8-400 Dash 8Q"
    },
    {
        "icaoCode": "DHC2",
        "iataCode": "DHP",
        "description": "De Havilland Canada DHC-2 Beaver"
    },
    {
        "icaoCode": "DHC3",
        "iataCode": "DHL",
        "description": "De Havilland Canada DHC-3 Otter"
    },
    {
        "icaoCode": "DHC4",
        "iataCode": "DHC",
        "description": "De Havilland Canada DHC-4 Caribou"
    },
    {
        "icaoCode": "DHC6",
        "iataCode": "DHT",
        "description": "De Havilland Canada DHC-6 Twin Otter"
    },
    {
        "icaoCode": "DHC7",
        "iataCode": "DH7",
        "description": "De Havilland Canada DHC-7 Dash 7"
    },
    {
        "icaoCode": "DOVE",
        "iataCode": "DHD",
        "description": "De Havilland DH.104 Dove"
    },
    {
        "icaoCode": "E110",
        "iataCode": "EMB",
        "description": "Embraer EMB 110 Bandeirante"
    },
    {
        "icaoCode": "E120",
        "iataCode": "EM2",
        "description": "Embraer EMB 120 Brasilia"
    },
    {
        "icaoCode": "E145",
        "iataCode": "ER4",
        "description": "Embraer RJ145"
    },
    {
        "icaoCode": "E170",
        "iataCode": "E70",
        "description": "Embraer 170"
    },
    {
        "icaoCode": "E175",
        "iataCode": "E75",
        "description": "Embraer 175"
    },
    {
        "icaoCode": "E190",
        "iataCode": "E90",
        "description": "Embraer 190"
    },
    {
        "icaoCode": "E545",
        "iataCode": "",
        "description": "Embraer Legacy 450"
    },
    {
        "icaoCode": "E50P",
        "iataCode": "EP1",
        "description": "Embraer Phenom 100"
    },
    {
        "icaoCode": "E55P",
        "iataCode": "EP3",
        "description": "Embraer Phenom 300"
    },
    {
        "icaoCode": "EC25",
        "iataCode": "",
        "description": "Eurocopter EC225 Super Puma"
    },
    {
        "icaoCode": "EC45",
        "iataCode": "",
        "description": "Eurocopter EC145"
    },
    {
        "icaoCode": "EXPL",
        "iataCode": "MD9",
        "description": "MD Helicopters MD900 Explorer"
    },
    {
        "icaoCode": "F100",
        "iataCode": "100",
        "description": "Fokker 100"
    },
    {
        "icaoCode": "F27",
        "iataCode": "F27",
        "description": "Fokker F27 Friendship"
    },
    {
        "icaoCode": "F28",
        "iataCode": "F21",
        "description": "Fokker F28 Fellowship"
    },
    {
        "icaoCode": "F2TH",
        "iataCode": "D20",
        "description": "Dassault Falcon 2000"
    },
    {
        "icaoCode": "F50",
        "iataCode": "F50",
        "description": "Fokker 50"
    },
    {
        "icaoCode": "F70",
        "iataCode": "F70",
        "description": "Fokker 70"
    },
    {
        "icaoCode": "G159",
        "iataCode": "GRS",
        "description": "Gulfstream Aerospace G-159 Gulfstream I"
    },
    {
        "icaoCode": "G21",
        "iataCode": "GRG",
        "description": "Grumman G-21 Goose"
    },
    {
        "icaoCode": "G73T",
        "iataCode": "GRM",
        "description": "Grumman G-73 Turbo Mallard"
    },
    {
        "icaoCode": "GLEX",
        "iataCode": "CCX",
        "description": "Canadair Global Express"
    },
    {
        "icaoCode": "GLF4",
        "iataCode": "GJ4",
        "description": "Gulfstream IV"
    },
    {
        "icaoCode": "GLF5",
        "iataCode": "GJ5",
        "description": "Gulfstream V"
    },
    {
        "icaoCode": "GLF6",
        "iataCode": "GJ6",
        "description": "Gulfstream G650"
    },
    {
        "icaoCode": "HERN",
        "iataCode": "DHH",
        "description": "De Havilland DH.114 Heron"
    },
    {
        "icaoCode": "H25B",
        "iataCode": "H25",
        "description": "British Aerospace 125 series / Hawker/Raytheon 700/800/800XP/850/900"
    },
    {
        "icaoCode": "H25C",
        "iataCode": "H25",
        "description": "British Aerospace 125-1000 series / Hawker/Raytheon 1000"
    },
    {
        "icaoCode": "I114",
        "iataCode": "I14",
        "description": "Ilyushin IL114"
    },
    {
        "icaoCode": "IL18",
        "iataCode": "IL8",
        "description": "Ilyushin IL18"
    },
    {
        "icaoCode": "IL62",
        "iataCode": "IL6",
        "description": "Ilyushin IL62"
    },
    {
        "icaoCode": "IL76",
        "iataCode": "IL7",
        "description": "Ilyushin IL76"
    },
    {
        "icaoCode": "IL86",
        "iataCode": "ILW",
        "description": "Ilyushin IL86"
    },
    {
        "icaoCode": "IL96",
        "iataCode": "I93",
        "description": "Ilyushin IL96"
    },
    {
        "icaoCode": "J328",
        "iataCode": "FRJ",
        "description": "Fairchild Dornier 328JET"
    },
    {
        "icaoCode": "JS31",
        "iataCode": "J31",
        "description": "British Aerospace Jetstream 31"
    },
    {
        "icaoCode": "JS32",
        "iataCode": "J32",
        "description": "British Aerospace Jetstream 32"
    },
    {
        "icaoCode": "JS41",
        "iataCode": "J41",
        "description": "British Aerospace Jetstream 41"
    },
    {
        "icaoCode": "JU52",
        "iataCode": "JU5",
        "description": "Junkers Ju52/3M"
    },
    {
        "icaoCode": "L101",
        "iataCode": "L10",
        "description": "Lockheed L-1011 Tristar"
    },
    {
        "icaoCode": "L188",
        "iataCode": "LOE",
        "description": "Lockheed L-188 Electra"
    },
    {
        "icaoCode": "L410",
        "iataCode": "L4T",
        "description": "LET 410"
    },
    {
        "icaoCode": "LOAD",
        "iataCode": "ALM",
        "description": "Ayres LM200 Loadmaster"
    },
    {
        "icaoCode": "MD11",
        "iataCode": "M11",
        "description": "McDonnell Douglas MD-11"
    },
    {
        "icaoCode": "MD81",
        "iataCode": "M81",
        "description": "McDonnell Douglas MD-81"
    },
    {
        "icaoCode": "MD82",
        "iataCode": "M82",
        "description": "McDonnell Douglas MD-82"
    },
    {
        "icaoCode": "MD83",
        "iataCode": "M83",
        "description": "McDonnell Douglas MD-83"
    },
    {
        "icaoCode": "MD87",
        "iataCode": "M87",
        "description": "McDonnell Douglas MD-87"
    },
    {
        "icaoCode": "MD88",
        "iataCode": "M88",
        "description": "McDonnell Douglas MD-88"
    },
    {
        "icaoCode": "MD90",
        "iataCode": "M90",
        "description": "McDonnell Douglas MD-90"
    },
    {
        "icaoCode": "MI8",
        "iataCode": "MIH",
        "description": "MIL Mi-8 / Mi-17 / Mi-171 / Mil-172"
    },
    {
        "icaoCode": "MU2",
        "iataCode": "MU2",
        "description": "Mitsubishi Mu-2"
    },
    {
        "icaoCode": "N262",
        "iataCode": "ND2",
        "description": "Aerospatiale (Nord) 262"
    },
    {
        "icaoCode": "NOMA",
        "iataCode": "CD2",
        "description": "Government Aircraft Factories N22B / N24A Nomad"
    },
    {
        "icaoCode": "P68",
        "iataCode": "PN6",
        "description": "Partenavia P.68"
    },
    {
        "icaoCode": "PA31",
        "iataCode": "PA2",
        "description": "Piper PA-31 Navajo"
    },
    {
        "icaoCode": "PA46",
        "iataCode": "PAG",
        "description": "Piper PA-46"
    },
    {
        "icaoCode": "PC12",
        "iataCode": "PL2",
        "description": "Pilatus PC-12"
    },
    {
        "icaoCode": "PC6T",
        "iataCode": "PL6",
        "description": "Pilatus PC-6 Turbo Porter"
    },
    {
        "icaoCode": "RJ1H",
        "iataCode": "AR1",
        "description": "Avro RJ100"
    },
    {
        "icaoCode": "R200",
        "iataCode": "",
        "description": "Robin HR200/R2000 series, Alpha160A"
    },
    {
        "icaoCode": "RJ70",
        "iataCode": "AR7",
        "description": "Avro RJ70"
    },
    {
        "icaoCode": "RJ85",
        "iataCode": "AR8",
        "description": "Avro RJ85"
    },
    {
        "icaoCode": "RX1H",
        "iataCode": "AX1",
        "description": "Avro RJX100"
    },
    {
        "icaoCode": "RX85",
        "iataCode": "AX8",
        "description": "Avro RJX85"
    },
    {
        "icaoCode": "S210",
        "iataCode": "CRV",
        "description": "Aerospatiale (Sud Aviation) Se.210 Caravelle"
    },
    {
        "icaoCode": "S58T",
        "iataCode": "S58",
        "description": "Sikorsky S-58T"
    },
    {
        "icaoCode": "S601",
        "iataCode": "NDC",
        "description": "Aerospatiale SN.601 Corvette"
    },
    {
        "icaoCode": "S61",
        "iataCode": "S61",
        "description": "Sikorsky S-61"
    },
    {
        "icaoCode": "S65C",
        "iataCode": "NDH",
        "description": "Eurocopter (Aerospatiale) SA365C / SA365N Dauphin 2"
    },
    {
        "icaoCode": "S76",
        "iataCode": "S76",
        "description": "Sikorsky S-76"
    },
    {
        "icaoCode": "S92",
        "iataCode": "S92",
        "description": "Sikorsky S-92"
    },
    {
        "icaoCode": "SB20",
        "iataCode": "S20",
        "description": "Saab 2000"
    },
    {
        "icaoCode": "SC7",
        "iataCode": "SHS",
        "description": "Shorts SC-7 Skyvan"
    },
    {
        "icaoCode": "SF34",
        "iataCode": "SF3",
        "description": "Saab SF340A/B"
    },
    {
        "icaoCode": "SH33",
        "iataCode": "SH3",
        "description": "Shorts SD.330"
    },
    {
        "icaoCode": "SH36",
        "iataCode": "SH6",
        "description": "Shorts SD.360"
    },
    {
        "icaoCode": "SU95",
        "iataCode": "",
        "description": "Sukhoi Superjet 100"
    },
    {
        "icaoCode": "T134",
        "iataCode": "TU3",
        "description": "Tupolev Tu-134"
    },
    {
        "icaoCode": "T144",
        "iataCode": "",
        "description": "Tupolev Tu-144"
    },
    {
        "icaoCode": "T154",
        "iataCode": "TU5",
        "description": "Tupolev Tu-154"
    },
    {
        "icaoCode": "T204",
        "iataCode": "T20",
        "description": "Tupolev Tu-204 / Tu-214"
    },
    {
        "icaoCode": "TB20",
        "iataCode": "",
        "description": "Socata TB-20 Trinidad"
    },
    {
        "icaoCode": "TRIS",
        "iataCode": "BNT",
        "description": "Pilatus Britten-Norman BN-2A Mk III Trislander"
    },
    {
        "icaoCode": "VISC",
        "iataCode": "VCV",
        "description": "Vickers Viscount"
    },
    {
        "icaoCode": "WW24",
        "iataCode": "WWP",
        "description": "Israel Aircraft Industries 1124 Westwind"
    },
    {
        "icaoCode": "Y12",
        "iataCode": "YN2",
        "description": "Harbin Yunshuji Y12"
    },
    {
        "icaoCode": "YK40",
        "iataCode": "YK4",
        "description": "Yakovlev Yak-40"
    },
    {
        "icaoCode": "YK42",
        "iataCode": "YK2",
        "description": "Yakovlev Yak-42"
    },
    {
        "icaoCode": "YS11",
        "iataCode": "YS1",
        "description": "NAMC YS-11"
    }
]


def generate_person_steward(count_man, count_woman, code_hub="DME", iata_code="U6"):
    for i in range(count_man):
        name = random.choice(name_man)
        last = random.choice(last_name)
        par = random.choice(patronymic_man)

        hub = Airport_lime.objects.get(iata_code=code_hub)
        airline = Airline_lime.objects.get(iata_code=iata_code)
        Steward.objects.create(
            first_name=name,
            last_name=last,
            patronymic=par,
            sex="M",
            hub=hub,
            airline=airline
        )

    for i in range(count_woman):
        name = random.choice(name_woman)
        last = random.choice(last_name)+"а"
        par = random.choice(patronymic_woman)

        hub = Airport_lime.objects.get(iata_code=code_hub)
        Steward.objects.create(
            first_name=name,
            last_name=last,
            patronymic=par,
            sex="W",
            hub=hub,
            airline=airline
        )


def create_type_aircraft():
    for i in types_aircrafts:
        AircraftType.objects.update_or_create(
            model=i['description'],
            defaults={
                'icao_code': i['icaoCode']
            }
        )


def generate_person_pilot(count_man, count_woman, code_hub="DME", iata_code="U6", type_pilot="C", ratings=["A319", "A320"]):
    for i in range(count_man):
        name = random.choice(name_man)
        last = random.choice(last_name)
        par = random.choice(patronymic_man)

        hub = Airport_lime.objects.get(iata_code=code_hub)
        airline = Airline_lime.objects.get(iata_code=iata_code)

        a = Pilot.objects.create(
            first_name=name,
            last_name=last,
            patronymic=par,
            sex="M",
            hub=hub,
            airline=airline,
            type_pilot=type_pilot,
        )
        for t in ratings:
            aircraft_type = AircraftType.objects.get(icao_code=t)
            a.ratings.add(aircraft_type)

    for i in range(count_man):
        name = random.choice(name_woman)
        last = random.choice(last_name)+"а"
        par = random.choice(patronymic_woman)

        hub = Airport_lime.objects.get(iata_code=code_hub)
        airline = Airline_lime.objects.get(iata_code=iata_code)

        a = Pilot.objects.create(
            first_name=name,
            last_name=last,
            patronymic=par,
            sex="W",
            hub=hub,
            airline=airline,
            type_pilot=type_pilot,
        )
        for t in ratings:
            aircraft_type = AircraftType.objects.get(icao_code=t)
            a.ratings.add(aircraft_type)


# Потом подправить эту функцию
def create_airlines():
    airlines = FR24().get_airlines()
    kol = 0
    for i in airlines:
        if len(i.iata) or len(i.icao) < 1:
            s = "AirCompany"+str(kol)
            kol += 1

            try:
                foo = Airline_lime.objects.get(iata_code=i.iata)
            except Airline_lime.DoesNotExist:
                foo = None

            try:
                foo1 = Airline_lime.objects.get(name=i.name)
            except Airline_lime.DoesNotExist:
                foo1 = None

            if foo is None and foo1 is None:
                Airline_lime.objects.update_or_create(
                    iata_code=i.iata,
                    defaults={
                        'name': i.name,
                        'icao_code': i.icao,
                        'account': User.objects.get(username=s),
                    }
                )


def generate_users():
    kol = 0
    for i in range(1325):
        s = "AirCompany"+str(kol)
        kol += 1
        user = User.objects.create_user(username=s, email="qq@qq.ru", password="password")
        user.save()


def generate_aircraft(code, model, airline="U6", hub="DME", status=True):
    Aircraft.objects.create(
        reg=code,
        model=AircraftType.objects.get(icao_code=model),
        airline=Airline_lime.objects.get(iata_code=airline),
        hub=Airport_lime.objects.get(iata_code=hub),
        status=status
    )



