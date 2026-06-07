import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression


#pobieramy dane
engine = create_engine(
    "postgresql+psycopg2://moj_user:mojeHaslo@localhost:5432/hr_db"
)


#łączymy tabele
df = pd.read_sql("""
SELECT
    p.id_pracownika,
    p.plec,
    p.data_zatrudnienia,
    h.dzial,
    h.stanowisko,
    h.zarobki,
    h.ocena_roczna,
    h.liczba_awansow,
    h.dni_zwolnienia_lekarskiego,
    o.czy_odszedl
FROM pracownicy p
JOIN historia_kariery h
    ON p.id_pracownika = h.id_pracownika
JOIN odejscia o
    ON p.id_pracownika = o.id_pracownika
""", engine)

# wyliczamy staż
dzis = pd.Timestamp.now()

df["staz_miesiace"] = (
    (dzis - pd.to_datetime(df["data_zatrudnienia"])).dt.days // 30
)
# ================================================
# model ml
# ================================================

#przygotowanie danych

enc_dzial = LabelEncoder()
enc_stanowisko = LabelEncoder()
enc_plec = LabelEncoder()

df["dzial"] = enc_dzial.fit_transform(df["dzial"])
df["stanowisko"] = enc_stanowisko.fit_transform(df["stanowisko"])
df["plec"] = enc_plec.fit_transform(df["plec"])

# x i y
X = df[
    [
        "zarobki",
        "ocena_roczna",
        "liczba_awansow",
        "dni_zwolnienia_lekarskiego",
        "staz_miesiace",
        "dzial",
        "stanowisko",
        "plec"
    ]
]

y = df["czy_odszedl"]

# trenowanie

model = LogisticRegression(max_iter=1000)

model.fit(X, y)

# predykcja dla aktywnych pracownikow

aktywni = df[df["czy_odszedl"] == 0].copy()

X_aktywni = aktywni[X.columns]

aktywni["ryzyko_odejscia"] = (model.predict_proba(X_aktywni)[:, 1] * 100).round(2) # zwraca prawdopodobienstwo dla aktywnych, np (zostaje, odejdzie) (0.2, 0.8) i wybieramy wszystkie wiersze ale 1 kolumne czyli p. czy odejdzie i mnożymy przez 100 zeby miec % np 80%

# rekomendacje

def ustal_ryzyko(ryzyko):

    if ryzyko < 20:
        return "Niskie ryzyko"
    elif ryzyko < 50:
        return "Średnie ryzyko"
    elif ryzyko < 75:
        return "Wysokie ryzyko"
    else:
        return "Krytyczne ryzyko"

aktywni["ryzyko"] = (aktywni["ryzyko_odejscia"].apply(ustal_ryzyko))

wyniki = aktywni[["id_pracownika", "ryzyko_odejscia", "ryzyko"]]


wyniki.to_sql(
    "wyniki_predykcji_ai",
    engine,
    if_exists="replace",
    index = False
)
    
print( "Zapisano wynik predykcji do tabeli wyniki_predykcji_ai")


print(aktywni["ryzyko_odejscia"].describe())


























