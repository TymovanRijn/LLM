import sqlite3
connection = sqlite3.connect('./data/Offerte.sql')
cursor = connection.cursor()

def calc(materiaalsoort, qm2, mRandafwerking, mSpatrand, mVensterbank, uOnderbouw, uInleg, uRuw, Kraangat, Zeepdispenser, qBoorgaten, WCD, mAchterwand):
    totale_prijs = 0
    qm2Prijs = cursor.execute("SELECT Prijs_per_m2 FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    mRandafwerkingPrijs = cursor.execute("SELECT Randafwerking_p/m FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    mSpatrandPrijs = cursor.execute("SELECT Spatrand_p/m FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    mVensterbankPrijs = cursor.execute("SELECT Vensterbank_p/m FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    uOnderbouwPrijs = cursor.execute("SELECT Uitsparing_onderbouw FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    uInlegPrijs = cursor.execute("SELECT Uitsparing_inleg FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    uRuwPrijs = cursor.execute("SELECT Uitsparing_ruw FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    KraangatPrijs = cursor.execute("SELECT Kraangat FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    ZeepdispenserPrijs = cursor.execute("SELECT Zeepdispenser FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    qBoorgatenPrijs = cursor.execute("SELECT Boorgaten_per_stuk.1 FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    WCDPrijs = cursor.execute("SELECT WCD FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    mAchterwandPrijs = cursor.execute("SELECT Achterwand_p/m FROM Bladenmatrix WHERE Materiaalsoort = ?", (materiaalsoort,)).fetchone()[0]
    toale_prijs += qm2 * qm2Prijs
    totale_prijs += mRandafwerking * mRandafwerkingPrijs
    totale_prijs += mSpatrand * mSpatrandPrijs
    totale_prijs += mVensterbank * mVensterbankPrijs
    if uOnderbouw:
        totale_prijs += uOnderbouwPrijs
    if uInleg:
        totale_prijs += uInlegPrijs
    if uRuw:
        totale_prijs += uRuwPrijs
    if Kraangat:
        totale_prijs += KraangatPrijs
    if Zeepdispenser:
        totale_prijs += ZeepdispenserPrijs
    totale_prijs += qBoorgaten * qBoorgatenPrijs
    if WCD:
        totale_prijs += WCDPrijs
    totale_prijs += mAchterwand * mAchterwandPrijs
    return totale_prijs

calc("Noble Desiree Grey Matt", 2, 3, 4 ,5, 6, 7, 8, 9, 10, 11, 12, 13)