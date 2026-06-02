-- 1. CZYSZCZENIE STARYCH TABEL

DROP TABLE IF EXISTS odejscia CASCADE;
DROP TABLE IF EXISTS historia_kariery CASCADE;
DROP TABLE IF EXISTS pracownicy CASCADE;

-- 2. TWORZENIE TABEL

CREATE TABLE pracownicy (
    id_pracownika INT PRIMARY KEY,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    plec VARCHAR(10),
    miasto VARCHAR(50),
    data_urodzenia DATE NOT NULL,
    data_zatrudnienia DATE NOT NULL
);

CREATE TABLE historia_kariery (
    id_wpisu INT PRIMARY KEY,
    id_pracownika INT NOT NULL,
    dzial VARCHAR(50) NOT NULL,
    stanowisko VARCHAR(50) NOT NULL,
    zarobki NUMERIC(10,2),
    ocena_roczna INT CHECK (ocena_roczna BETWEEN 1 AND 5),
    liczba_awansow INT DEFAULT 0,
    dni_zwolnienia_lekarskiego INT DEFAULT 0,

    CONSTRAINT fk_pracownik
        FOREIGN KEY (id_pracownika)
        REFERENCES pracownicy(id_pracownika)
);

CREATE TABLE odejscia (
    id_pracownika INT PRIMARY KEY,
    czy_odszedl BOOLEAN NOT NULL,
    data_odejscia DATE,

    CONSTRAINT fk_odejscia_pracownik
        FOREIGN KEY (id_pracownika)
        REFERENCES pracownicy(id_pracownika),

    CONSTRAINT chk_data_odejscia
        CHECK (
            (czy_odszedl = TRUE AND data_odejscia IS NOT NULL)
            OR
            (czy_odszedl = FALSE AND data_odejscia IS NULL)
        )
);
