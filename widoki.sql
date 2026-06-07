DROP VIEW IF EXISTS vw_ryzyko_pracownikow;
DROP VIEW IF EXISTS vw_ryzyko_dzial;


CREATE VIEW vw_ryzyko_pracownikow AS
SELECT
    p.id_pracownika,
    p.imie,
    p.nazwisko,
    h.dzial,
    h.stanowisko,
    h.ocena_roczna,
    w.ryzyko_odejscia,

    CASE
        WHEN w.ryzyko_odejscia < 30 THEN 'Niskie ryzyko'
        WHEN w.ryzyko_odejscia < 70 THEN 'Średnie ryzyko'
        ELSE 'Wysokie ryzyko'
    END AS poziom_ryzyka

FROM pracownicy p
JOIN historia_kariery h
    ON p.id_pracownika = h.id_pracownika
JOIN wyniki_predykcji_ai w
    ON p.id_pracownika = w.id_pracownika;






CREATE OR REPLACE VIEW vw_ryzyko_dzial AS
SELECT
    h.dzial,
    COUNT(*) AS liczba_pracownikow,
    ROUND(AVG(w.ryzyko_odejscia)::numeric, 2) AS srednie_ryzyko

FROM historia_kariery h
JOIN wyniki_predykcji_ai w
    ON h.id_pracownika = w.id_pracownika
GROUP BY h.dzial;