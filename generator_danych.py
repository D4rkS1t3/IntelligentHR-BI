#!/bin/python3

import pandas as pd
import random
from datetime import date, timedelta
from sqlalchemy import create_engine

#połączenie z bazą

engine = create_engine(
    "postgresql+psycopg2://moj_user:mojeHaslo@localhost:5432/hr_db"
)



random.seed(40)

n_pracownikow = 1000


def losowa_data(start, end):
    dni = (end - start).days
    return start + timedelta(days=random.randint(0, dni))


imiona_meskie = [
    "Jan", "Piotr", "Paweł", "Marek", "Tomasz",
    "Andrzej", "Krzysztof", "Adam", "Michał", "Jakub"
]

imiona_zenskie = [
    "Anna", "Katarzyna", "Agnieszka", "Monika", "Magdalena",
    "Joanna", "Ewa", "Aleksandra", "Karolina", "Natalia"
]

nazwiska = [
    "Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk",
    "Kamiński", "Lewandowski", "Zieliński", "Szymański", "Woźniak"
]

miasta = [
    "Warszawa", "Kraków", "Wrocław", "Poznań", "Gdańsk",
    "Łódź", "Szczecin", "Lublin", "Katowice", "Białystok"
]

plec = random.choices(["m", "k"], k=n_pracownikow)

imiona = [
    random.choice(imiona_meskie)
    if p == "m"
    else random.choice(imiona_zenskie)
    for p in plec
]

daty_urodzenia = []
daty_zatrudnienia = []

for _ in range(n_pracownikow):

    ur = losowa_data(date(1960, 1, 1), date(2005, 12, 31))

    try:
        min_data_zatr = ur.replace(year=ur.year + 18)
    except ValueError:
    # 29 lutego
        min_data_zatr = ur.replace(year=ur.year + 18,day=28)

    if min_data_zatr < date(2015, 1, 1):
        min_data_zatr = date(2015, 1, 1)

    koniec = date(2026, 6, 2)

    if min_data_zatr > koniec:
        min_data_zatr = koniec

    zatr = losowa_data(min_data_zatr,koniec)

    daty_urodzenia.append(ur)
    daty_zatrudnienia.append(zatr)

pracownicy = pd.DataFrame({
    "id_pracownika": range(1, n_pracownikow + 1),
    "imie": imiona,
    "nazwisko": random.choices(nazwiska, k=n_pracownikow),
    "plec": plec,
    "miasto": random.choices(miasta, k=n_pracownikow),
    "data_urodzenia": daty_urodzenia,
    "data_zatrudnienia": daty_zatrudnienia
})

dzialy = [
    "IT",
    "HR",
    "Finanse",
    "Sprzedaz",
    "Marketing",
    "Produkcja"
]

stanowiska = [
    "Junior",
    "Mid",
    "Senior",
    "Lead",
    "Manager"
]

widełki = {
    "Junior": (6000, 9000),
    "Mid": (9000, 14000),
    "Senior": (14000, 22000),
    "Lead": (22000, 30000),
    "Manager": (25000, 40000)
}

stanowiska_los = random.choices(
    stanowiska,
    weights=[30, 35, 20, 10, 5],
    k=n_pracownikow
)

zarobki = []

for stanowisko in stanowiska_los:
    min_p, max_p = widełki[stanowisko]
    zarobki.append(
        round(random.uniform(min_p, max_p), 2)
    )


def liczba_awansow(stanowisko):

    mapping = {
        "Junior": (0, 1),
        "Mid": (0, 2),
        "Senior": (1, 4),
        "Lead": (2, 6),
        "Manager": (3, 8)
    }

    mn, mx = mapping[stanowisko]
    return random.randint(mn, mx)


awanse = [
    liczba_awansow(s)
    for s in stanowiska_los
]

historia_kariery = pd.DataFrame({
    "id_wpisu": range(1, n_pracownikow + 1),
    "id_pracownika": range(1, n_pracownikow + 1),
    "dzial": random.choices(dzialy, k=n_pracownikow),
    "stanowisko": stanowiska_los,
    "zarobki": zarobki,
    "ocena_roczna": random.choices(
        [1, 2, 3, 4, 5],
        weights=[5, 10, 25, 35, 25],
        k=n_pracownikow
    ),
    "liczba_awansow": awanse,
    "dni_zwolnienia_lekarskiego": random.choices(
        range(31),
        k=n_pracownikow
    )
})

srednia_w_dziale = (
    historia_kariery
    .groupby("dzial")["zarobki"]
    .mean()
    .to_dict()
)


def czy_odszedl(wiersz):

    prawd_odejscia = 0.10

    if wiersz["ocena_roczna"] == 1:
        prawd_odejscia = 0.80

    elif (
        wiersz["zarobki"] <
        srednia_w_dziale[wiersz["dzial"]]
        and wiersz["liczba_awansow"] == 0
        ):
            prawd_odejscia = 0.60

    elif (
        wiersz["ocena_roczna"] >= 4
        and wiersz["zarobki"] >
        srednia_w_dziale[wiersz["dzial"]]
        ):
            prawd_odejscia = 0.05

    return random.random() < prawd_odejscia


odejscia = pd.DataFrame({
    "id_pracownika": range(1, n_pracownikow + 1)
})

odejscia["czy_odszedl"] = (
    historia_kariery
    .apply(czy_odszedl, axis=1)
)


def data_odejscia(wiersz):

    if wiersz["czy_odszedl"] == 0:
        return pd.NaT

    data_zatrudnienia = (
        pracownicy.loc[
            pracownicy["id_pracownika"]
            == wiersz["id_pracownika"],
            "data_zatrudnienia"
        ]
        .iloc[0]
    )

    return losowa_data(
        data_zatrudnienia,
        date(2026, 6, 2)
    )


odejscia["data_odejscia"] = (
    odejscia.apply(
        data_odejscia,
        axis=1
    )
)

pracownicy.to_sql(
    "pracownicy",
    engine,
    if_exists="append",
    index=False
)

historia_kariery.to_sql(
    "historia_kariery",
    engine,
    if_exists="append",
    index=False
)

odejscia.to_sql(
    "odejscia",
    engine,
    if_exists="append",
    index=False
)

print("Wygenerowano i dodano dane do bazy PostgreSQL.")
