SQLite format 3   @     �   	         I                                                 � .v�   �    �	�����                                                                                                                                                         �)'�3triggerPrijsBoorgatenofferte_prijsCREATE TRIGGER PrijsBoorgaten
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
BEGIN
    UPDATE offert�p)'�triggerPrijsBoorgatenofferte_prijsCREATE TRIGGER PrijsBoorgaten
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Boorgaten = 5 * NEW.Boorgaten
    WHERE ID = NEW.ID 
    AND NEW.Boorgaten IS NOT NULL
    AND (SELECT 1 FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort AND Boorgaten = 'mogelijk') IS NOT NULL;
END�+'�;triggerPrijsAchterwandofferte_prijsCREATE TRIGGER PrijsAchterwand
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
WHEN NEW.m2 IS NOT NULL AND NEW.Materiaalsoort IS NOT NULL AND NEW.Achterwand IS NOT NULL
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Achterwand = (SELECT `Achterwand_p/m` FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) * NEW.m2
    WHERE ID = NEW.ID;
END�k'�triggerPrijsWCDofferte_prijsCREATE TRIGGER PrijsWCD
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
BEGIN
    UPDATE offerte_prijs
    SET Prijs_WCD = 13.50
    WHERE ID = NEW.ID 
    AND NEW.WCD IS NOT NULL
    AND NEW.Materiaalsoort IS NOT NULL
    AND (SELECT WCD_Wandcontactdoos FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) = 'mogelijk';
END�d
1'�{triggerPrijsZeepdispenserofferte_prijsCREATE TRIGGER PrijsZeepdispenser
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
WHEN NEW.Zeepdispenser IS NOT NULL
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Zeepdispenser =10.70 ;
END�	1'�StriggerPrijsRandafwerkingofferte_prijsCREATE TRIGGER PrijsRandafwerking
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
WHEN NEW.m2 IS NOT NULL AND NEW.Materiaalsoort IS NOT NULL AND NEW.Randafwerking IS NOT NULL
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Randafwerking = (SELECT `Randafwerking_p/m` FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) * NEW.m2
    WHERE ID = NEW.ID;
END�l3'�	triggerPrijsMateriaalsoortofferte_prijsCREATE TRIGGER PrijsMateriaalsoort
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
WHEN NEW.m2 IS NOT NULL AND NEW.Materiaalsoort IS NOT NULL
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Materiaalsoort = (SELECT `Prijs_per_m2` FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) * NEW.m2
    WHERE ID = NEW.ID;
END�M'�#triggerBerekenPrijsMateriaalsoortupdateofferte_prijsCREATE TRIGGER BerekenPrijsMateriaalsoortupdate
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
WHEN NEW.m2 IS NOT NULL AND NEW.Materiaalsoort IS NOT NULL
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Materiaalsoort = (SELECT `Prijs_per_m2` FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) * NEW.m2
    WHERE ID = NEW.ID;
END�o''�tableofferte_prijsofferte_prijsCREATE TABLE offerte_prijs (
    ID INTEGER PRIMARY KEY,
    Materiaalsoort TEXT,
    Prijs_Materiaalsoort REAL,
    Randafwerking TEXT,
    Prijs_Randafwerking REAL,
    Spatrand TEXT,
    Prijs_Spatrand REAL,
    Vensterbank TEXT,
    Prijs_Vensterbank REAL,
    Zeepdispenser TEXT,
    Prijs_Zeepdispenser REAL,
    Boorgaten TEXT,
    Prijs_Boorgaten REAL,
    WCD TEXT,
    Prijs_WCD REAL,
    Achterwand TEXT,
    Prijs_Achterwand REAL,
    m2 REAL
)�?%%�AtableBladenmatrixBladenmatrixCREATE TABLE "Bladenmatrix" (
"Materiaalsoort" TEXT,
  "Spatrand" TEXT,
  "Vensterbank" TEXT,
  "Boorgaten_per_stuk" TEXT,
  "WCD_Wandcontactdoos" TEXT,
  "Randafwerking" TEXT,
  "Prijs_per_m2" REAL,
  "Randafwerking_p/m" INTEGER,
  "Spatrand_p/m" TEXT,
  "Vensterbank_p/m" REAL,
  "Uitsparing_onderbouw" REAL,
  "Uitsparing_inleg" REAL,
  "Uitsparing_ruw" INTEGER,
  "Kraangat" REAL,
  "Zeepdispenser" REAL,
  "Boorgaten_per_stuk.1" INTEGER,
  "WCD" REAL,
  "Achterwand_p/m" REAL,
  "Randafwerking_p/m.1" INTEGER
, Randafwerking_pm REAL)P++Ytablesqlite_sequencesqlite_sequenceCREATE TABLE sqlite_sequence(name   
    �lz	�����                                                                                                                                                                                                                                                                                                                                                                                                         e)'�triggerPrijsBoorgatenofferte_prijsCREATE TRIGGER PrijsBoorgaten
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Boorgaten = 5 * NEW.Boorgaten
    WHERE ID = NEW.ID 
    AND NEW.Boorgaten IS NOT NULL
    AND (SELECT 1 FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort AND Boorgaten = 'mogelijk') IS NOT NULL;
END�+'�;triggerPrijsAchterwandofferte_prijsCREATE TRIGGER PrijsAchterwand
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
WHEN NEW.m2 IS NOT NULL AND NEW.Materiaalsoort IS NOT NULL AND NEW.Achterwand IS NOT NULL
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Achterwand = (SELECT `Achterwand_p/m` FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) * NEW.m2
    WHERE ID = NEW.ID;
END�k'�triggerPrijsWCDofferte_prijsCREATE TRIGGER PrijsWCD
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
BEGIN
    UPDATE offerte_prijs
    SET Prijs_WCD = 13.50
    WHERE ID = NEW.ID 
    AND NEW.WCD IS NOT NULL
    AND NEW.Materiaalsoort IS NOT NULL
    AND (SELECT WCD_Wandcontactdoos FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) = 'mogelijk';
END�d
1'�{triggerPrijsZeepdispenserofferte_prijsCREATE TRIGGER PrijsZeepdispenser
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
WHEN NEW.Zeepdispenser IS NOT NULL
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Zeepdispenser =10.70 ;
END�	1'�StriggerPrijsRandafwerkingofferte_prijsCREATE TRIGGER PrijsRandafwerking
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
WHEN NEW.m2 IS NOT NULL AND NEW.Materiaalsoort IS NOT NULL AND NEW.Randafwerking IS NOT NULL
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Randafwerking = (SELECT `Randafwerking_p/m` FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) * NEW.m2
    WHERE ID = NEW.ID;
END�l3'�	triggerPrijsMateriaalsoortofferte_prijsCREATE TRIGGER PrijsMateriaalsoort
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
WHEN NEW.m2 IS NOT NULL AND NEW.Materiaalsoort IS NOT NULL
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Materiaalsoort = (SELECT `Prijs_per_m2` FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) * NEW.m2
    WHERE ID = NEW.ID;
END�M'�#triggerBerekenPrijsMateriaalsoortupdateofferte_prijsCREATE TRIGGER BerekenPrijsMateriaalsoortupdate
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
WHEN NEW.m2 IS NOT NULL AND NEW.Materiaalsoort IS NOT NULL
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Materiaalsoort = (SELECT `Prijs_per_m2` FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) * NEW.m2
    WHERE ID = NEW.ID;
END�o''�tableofferte_prijsofferte_prijsCREATE TABLE offerte_prijs (
    ID INTEGER PRIMARY KEY,
    Materiaalsoort TEXT,
    Prijs_Materiaalsoort REAL,
    Randafwerking TEXT,
    Prijs_Randafwerking REAL,
    Spatrand TEXT,
    Prijs_Spatrand REAL,
    Vensterbank TEXT,
    Prijs_Vensterbank REAL,
    Zeepdispenser TEXT,
    Prijs_Zeepdispenser REAL,
    Boorgaten TEXT,
    Prijs_Boorgaten REAL,
    WCD TEXT,
    Prijs_WCD REAL,
    Achterwand TEXT,
    Prijs_Achterwand REAL,
    m2 REAL
)�?%%�AtableBladenmatrixBladenmatrixCREATE TABLE "Bladenmatrix" (
"Materiaalsoort" TEXT,
  "Spatrand" TEXT,
  "Vensterbank" TEXT,
  "Boorgaten_per_stuk" TEXT,
  "WCD_Wandcontactdoos" TEXT,
  "Randafwerking" TEXT,
  "Prijs_per_m2" REAL,
  "Randafwerking_p/m" INTEGER,
  "Spatrand_p/m" TEXT,
  "Vensterbank_p/m" REAL,
  "Uitsparing_onderbouw" REAL,
  "Uitsparing_inleg" REAL,
  "Uitsparing_ruw" INTEGER,
  "Kraangat" REAL,
  "Zeepdispenser" REAL,
  "Boorgaten_per_stuk.1" INTEGER,
  "WCD" REAL,
  "Achterwand_p/m" REAL,
  "Randafwerking_p/m.1" INTEGER
, Randafwerking_pm REAL)P++Ytablesqlite_sequencesqlite_sequenceCREATE TABLE sqlite_sequence(name,seq)� C Ci�'}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 �;'Noble Desiree Grey Matt0-150 mm150 mm+mogelijkmogelijkniet mogelijk@n��
=qW35@sVfffff@b�     @X`     F@%ffffff@%ffffff@+      @sVfffffW   �+)''Glencoe Verzoet0-150; 150 mm+150 mm+niet mogelijkniet mogelijkmogelijk@s     _40; 350@uH     @b�     @X`     F@%ffffff@%ffffff@�'+)''Glencoe Verzoet0-150; 150 mm+150 mm+niet mogelijkniet mogelijkmogelijk@s     _40; 350@uH     @b�     @X`     F@%ffffff@%ffffff@+      @s������_�5Taurus Terazzo Black150 mm+150 mm+mogelijkmogelijkmogelijk@l�     O309.4@sVfffff@b�     @X`     F@%ffffff@%ffffff@+      @r     O�#E''Taurus Terazzo White Verzoet0-150 mm0-150 mmniet mogelijkniet mogelijkmogelijk@m������O35#@b�     @X`     F@%ffffff@%ffffff@+      @r�     O�7Noble Carrara Verzoet150 mm+0-150 mmmogelijkmogelijkmogelijk@p&fffffW309.4#@b�     @X`     F@%ffffff@%ffffff@+      @s������W      ��|||f                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     materiaalsoorten
� 	glencoe_verzoet� 	taurus_terazzo_black   W	taurus_terazzo_white_verzoet   6	noble_carrara_verzoet;	noble_desiree_grey_matt   � ��                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            k;    d;    %  Noble Des     DE       :E   5;  + +% +              Glencoe Verzoet�             	         	                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              � 7Noble Carrara Verzoet150 mm+0-150 mmmogelijkmogelijkmogelijk@p&fffffW309.4#@b�     @X`     F@%ffffff@%ffffff@+      @s������   � ����                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 �I'�%triggerResetValuesAfterMaterialChangeofferte_prijsCREATE TRIGGER ResetValuesAfterMaterialChange
AFTER UPDATE OF Materiaalsoort ON offerte_prijs
FOR EACH ROW
WHEN OLD.Materiaalsoort != NEW.Materiaalsoort
BEGIN
    UPDATE offerte_prijs
    SET
        Prijs_Materiaalsoort = NULL,
        Randafwerking = NULL, 
        Prijs_Randafwerking = NULL,
        Spatrand = NULL, 
        Prijs_Spatrand = NULL,
        Vensterbank = NULL,
        Prijs_Vensterbank = NULL,
        Zeepdispenser = NULL,
        Prijs_Zeepdispenser = NULL,
        Boorgaten = NULL,
        Prijs_Boorgaten = NULL,
        WCD = NULL,
        Prijs_WCD = NULL,
        Achterwand = NULL,
        Prijs_Achterwand = NULL,
        m2 = 0  -- Gewijzigd van NULL naar 0
    WHERE ID = NEW.ID;
END�/'�otriggerResetPrijsAlsNullofferte_prijsCREATE TRIGGER ResetPrijsAlsNull
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
BEGIN
    -- Reset Prijs_Randafwerking als Randafwerking NULL is
    UPDATE offerte_prijs SET Prijs_Randafwerking = NULL WHERE ID = NEW.ID AND NEW.Randafwerking IS NULL;
    -- Reset Prijs_Spatrand als Spatrand NULL is
    UPDATE offerte_prijs SET Prijs_Spatrand = NULL WHERE ID = NEW.ID AND NEW.Spatrand IS NULL;
    -- Reset Prijs_Vensterbank als Vensterbank NULL is
    UPDATE offerte_prijs SET Prijs_Vensterbank = NULL WHERE ID = NEW.ID AND NEW.Vensterbank IS NULL;
    -- Reset Prijs_Zeepdispenser als Zeepdispenser NULL is
    UPDATE offerte_prijs SET Prijs_Zeepdispenser = NULL WHERE ID = NEW.ID AND NEW.Zeepdispenser IS NULL;
    -- Reset Prijs_Boorgaten als Boorgaten NULL is
    UPDATE offerte_prijs SET Prijs_Boorgaten = NULL WHERE ID = NEW.ID AND NEW.Boorgaten IS NULL;
    -- Reset Prijs_WCD als WCD NULL is
    UPDATE offerte_prijs SET Prijs_WCD = NULL WHERE ID = NEW.ID AND NEW.WCD IS NULL;
    -- Reset Prijs_Achterwand als Achterwand NULL is
    UPDATE offerte_prijs SET Prijs_Achterwand = NULL WHERE ID = NEW.ID AND NEW.Achterwand IS NULL;
END�p)'�triggerPrijsBoorgatenofferte_prijsCREATE TRIGGER PrijsBoorgaten
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Boorgaten = 5 * NEW.Boorgaten
    WHERE ID = NEW.ID 
    AND NEW.Boorgaten IS NOT NULL
    AND (SELECT 1 FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort AND Boorgaten = 'mogelijk') IS NOT NULL;
END�+'�;triggerPrijsAchterwandofferte_prijsCREATE TRIGGER PrijsAchterwand
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
WHEN NEW.m2 IS NOT NULL AND NEW.Materiaalsoort IS NOT NULL AND NEW.Achterwand IS NOT NULL
BEGIN
    UPDATE offerte_prijs
    SET Prijs_Achterwand = (SELECT `Achterwand_p/m` FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) * NEW.m2
    WHERE ID = NEW.ID;
END�k'�triggerPrijsWCDofferte_prijsCREATE TRIGGER PrijsWCD
AFTER UPDATE ON offerte_prijs
FOR EACH ROW
BEGIN
    UPDATE offerte_prijs
    SET Prijs_WCD = 13.50
    WHERE ID = NEW.ID 
    AND NEW.WCD IS NOT NULL
    AND NEW.Materiaalsoort IS NOT NULL
    AND (SELECT WCD_Wandcontactdoos FROM Bladenmatrix WHERE Materiaalsoort = NEW.Materiaalsoort) = 'mogelijk';
END   e e                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           � 5Taurus Terazzo Black150 mm+150 mm+mogelijkmogelijkmogelijk@l�     O309.4@sVfffff@b�     @X`     F@%ffffff@%ffffff@+      @r        � `�'��`F%�                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         �%+)''Glencoe Verzoet0-150; 150 mm+150 mm+niet mogelijkniet mogelijkmogelijk@s     _40; 350@uH     @b�     @X`     F@%ffffff@%ffffff@+      @s�������5Taurus Terazzo Black150 mm+150 mm+mogelijkmogelijkmogelijk@l�     O309.4@sVfffff@b�     @X`     F@%ffffff@%ffffff@+      @r     �!E''Taurus Terazzo White Verzoet0-150 mm0-150 mmniet mogelijkniet mogelijkmogelijk@m������O35#@b�     @X`     F@%ffffff@%ffffff@+      @r�     �7Noble Carrara Verzoet150 mm+0-150 mmmogelijkmogelijkmogelijk@p&fffffW309.4#@b�     @X`     F@%ffffff@%ffffff@+      @s�������;'Noble Desiree Grey Matt0-150 mm150 mm+mogelijkmogelijkniet mogelijk@n��
=qW35@sVfffff@b�     @X`     F@%ffffff@%ffffff@+      @sVfffff