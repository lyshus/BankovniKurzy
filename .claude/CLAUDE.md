nikdy nemaž databázi/branch bez výslovného svolení
u destruktivních DB operací se vždy zeptej
produkční data zálohuj před migrací tak, aby se k tomu následně dalo uživatelsky (bez promptů) snadno dostat a snadno to pak i obnovit, ideálně u zálohy udržuj nějaký textový soubor s krátkým návodem, jak data obnovit, něco jako návod_na_obnovu_nazevMIGRACNIHOsouboru.txt
