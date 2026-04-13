import unicodedata


ALL_LANGUAGE_OPTIONS = [
    ("en", "English"),
    ("it", "Italiano"),
    ("es", "Español"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("zh", "中文（简体）"),
    ("ru", "Русский"),
]

UI_TEXTS = {
    "en": {
        "title": "PERIODIC TABLE OF ELEMENTS",
        "search_placeholder": "Search by name, symbol or atomic number...",
        "search_button": "Search",
        "first_element": "First element (e.g. H)",
        "second_element": "Second element (e.g. O)",
        "reset": "Reset",
        "calculate_formula": "Calculate formula",
        "builder_title": "Formula and nomenclature",
        "right_info": "Info",
        "right_diagram": "Electron config.",
        "right_compound": "Formula and nomenclature",
        "right_molar": "Molar mass",
        "right_stoichiometry": "Stoichiometry",
        "molar_title": "Molar mass calculator",
        "molar_prompt": "Enter a chemical formula (e.g. H2O, Ca(OH)2) to calculate its molar mass.",
        "molar_calculate": "Calculate",
        "molar_error": "Error",
        "stoichiometry_title": "Equation balancer",
        "stoichiometry_prompt": "Enter a chemical equation (e.g. Fe + O2 -> Fe2O3) to balance it.",
        "stoichiometry_balance": "Balance",
        "stoichiometry_calc_masses": "Calculate masses",
        "stoichiometry_mass_section": "Enter mass for a compound:",
        "stoichiometry_error": "Error",
        "selected_none": "No element selected",
        "transition_metals": "TRANSITION METALS",
        "search_found": "Found: {name} ({symbol})",
        "search_not_found": "No element found.",
        "builder_status": "A: {a} | B: {b}",
        "not_selected": "not selected",
        "trend_button_normal": "Normal view",
        "trend_button_macroclass": "Macro-class",
        "trend_button_metallic": "Metallic character",
        "trend_button_nonmetallic": "Nonmetallic character",
        "current_view_normal": "Current view: normal",
        "current_view_macro": "Current view: macro-class (Metals / Metalloids / Nonmetals)",
        "current_view_metric": "Current view: {name} (low = blue, high = yellow)",
        "current_view_metallic": "Current view: metallic character",
        "current_view_nonmetallic": "Current view: nonmetallic character",
        "info_prompt": "Select an element to see its details.",
        "compound_prompt": "Select A and B, choose the oxidation states, then click 'Calculate formula'.",
        "diagram_prompt": "Select an element to display the orbital diagram.",
        "diagram_switch_prompt": (
            "Select the 'Electron configuration' view to display the orbital diagram "
            "of the selected element."
        ),
        "diagram_title": "Electron configuration",
        "diagram_title_symbol": "Electron configuration - {symbol}",
        "diagram_not_available": "Electron configuration not available.",
        "formula_title": "Formula and nomenclature",
        "formula_label": "Formula",
        "stock_name": "Stock name",
        "traditional_name": "Traditional name",
        "oxidation_first": "Ox. #1",
        "oxidation_second": "Ox. #2",
        "first_selected": "First: {name} ({symbol})",
        "second_selected": "Second: {name} ({symbol})",
        "common_compounds": "Common compounds",
        "no_common_compounds": "No common compounds stored for this pair yet.",
        "pair_ready_prompt": (
            "Select oxidation states to calculate one formula, or read the common "
            "compounds listed below."
        ),
        "must_select_ab": "You must select both A and B before combining the elements.",
        "same_element": "The current builder does not support combining an element with itself yet.",
        "select_oxidation": "Select oxidation states for both elements.",
        "opposite_sign": "The current builder only supports combinations with opposite-sign oxidation states.",
        "traditional_na": "n/a",
        "more_info": "Overview based on the data currently available for this element.",
        "metallic_arrow": "Metallic character ↙",
        "nonmetallic_arrow": "Nonmetallic character ↗",
        "name": "Name",
        "symbol": "Symbol",
        "atomic_number": "Atomic number",
        "atomic_mass": "Molar mass",
        "macro_class": "Macro-class",
        "category": "Category",
        "period": "Period",
        "group": "Group",
        "standard_state": "Standard state",
        "electronegativity": "Electronegativity",
        "atomic_radius": "Atomic radius",
        "ionization_energy": "Ionization energy",
        "electron_affinity": "Electron affinity",
        "oxidation_states": "Oxidation states",
        "melting_point": "Melting point",
        "boiling_point": "Boiling point",
        "density": "Density",
        "year_discovered": "Year discovered",
        "info_section_identity": "Identity",
        "info_section_chemical_properties": "Chemical properties",
        "info_section_physical_properties": "Physical properties",
    },
    "it": {
        "title": "TAVOLA PERIODICA DEGLI ELEMENTI",
        "search_placeholder": "Cerca per nome, simbolo o numero atomico...",
        "search_button": "Cerca",
        "first_element": "Primo elemento (es. H)",
        "second_element": "Secondo elemento (es. O)",
        "reset": "Reset",
        "calculate_formula": "Calcola formula",
        "builder_title": "Formula e nomenclatura",
        "right_info": "Info",
        "right_diagram": "Config. elettronica",
        "right_compound": "Formula e nomenclatura",
        "right_molar": "Massa molare",
        "right_stoichiometry": "Stechiometria",
        "molar_title": "Calcolatrice massa molare",
        "molar_prompt": "Inserisci una formula chimica (es. H2O, Ca(OH)2) per calcolarne la massa molare.",
        "molar_calculate": "Calcola",
        "molar_error": "Errore",
        "stoichiometry_title": "Bilanciamento equazioni",
        "stoichiometry_prompt": "Inserisci un'equazione chimica (es. Fe + O2 -> Fe2O3) per bilanciarla.",
        "stoichiometry_balance": "Bilancia",
        "stoichiometry_calc_masses": "Calcola masse",
        "stoichiometry_mass_section": "Inserisci la massa per un composto:",
        "stoichiometry_error": "Errore",
        "selected_none": "Nessun elemento selezionato",
        "transition_metals": "METALLI DI TRANSIZIONE",
        "search_found": "Trovato: {name} ({symbol})",
        "search_not_found": "Nessun elemento trovato.",
        "builder_status": "A: {a} | B: {b}",
        "not_selected": "non selezionato",
        "trend_button_normal": "Vista normale",
        "trend_button_macroclass": "Macro-classe",
        "trend_button_metallic": "Carattere metallico",
        "trend_button_nonmetallic": "Carattere non metallico",
        "current_view_normal": "Vista attiva: normale",
        "current_view_macro": "Vista attiva: macro-classe (Metalli / Semi-metalli / Non-metalli)",
        "current_view_metric": "Vista attiva: {name} (basso = blu, alto = giallo)",
        "current_view_metallic": "Vista attiva: carattere metallico",
        "current_view_nonmetallic": "Vista attiva: carattere non metallico",
        "info_prompt": "Seleziona un elemento per vedere i dettagli.",
        "compound_prompt": "Seleziona A e B, imposta i numeri di ossidazione e premi 'Calcola formula'.",
        "diagram_prompt": "Seleziona un elemento per visualizzare il diagramma orbitale.",
        "diagram_switch_prompt": (
            "Seleziona la vista 'Configurazione elettronica' per visualizzare il diagramma "
            "orbitale dell'elemento selezionato."
        ),
        "diagram_title": "Configurazione elettronica",
        "diagram_title_symbol": "Configurazione elettronica - {symbol}",
        "diagram_not_available": "Configurazione elettronica non disponibile.",
        "formula_title": "Formula e nomenclatura",
        "formula_label": "Formula",
        "stock_name": "Nomenclatura di Stock",
        "traditional_name": "Nomenclatura tradizionale",
        "oxidation_first": "Ox. #1",
        "oxidation_second": "Ox. #2",
        "first_selected": "Primo: {name} ({symbol})",
        "second_selected": "Secondo: {name} ({symbol})",
        "common_compounds": "Combinazioni comuni",
        "no_common_compounds": "Nessuna combinazione comune salvata per questa coppia.",
        "pair_ready_prompt": (
            "Seleziona gli stati di ossidazione per calcolare una formula, oppure consulta "
            "le combinazioni comuni qui sotto."
        ),
        "must_select_ab": "Devi selezionare sia A sia B prima di unire gli elementi.",
        "same_element": "Per ora il builder non gestisce l'unione di un elemento con se stesso.",
        "select_oxidation": "Seleziona i numeri di ossidazione per entrambi gli elementi.",
        "opposite_sign": "Per ora il builder gestisce solo combinazioni con numeri di ossidazione di segno opposto.",
        "traditional_na": "n.d.",
        "more_info": "Panoramica basata sui dati attualmente disponibili per questo elemento.",
        "metallic_arrow": "Carattere metallico ↙",
        "nonmetallic_arrow": "Carattere non metallico ↗",
        "name": "Nome",
        "symbol": "Simbolo",
        "atomic_number": "Numero atomico",
        "atomic_mass": "Massa molare",
        "macro_class": "Macro-classe",
        "category": "Categoria",
        "period": "Periodo",
        "group": "Gruppo",
        "standard_state": "Stato standard",
        "electronegativity": "Elettronegatività",
        "atomic_radius": "Raggio atomico",
        "ionization_energy": "Energia di ionizzazione",
        "electron_affinity": "Affinità elettronica",
        "oxidation_states": "Stati di ossidazione",
        "melting_point": "Punto di fusione",
        "boiling_point": "Punto di ebollizione",
        "density": "Densità",
        "year_discovered": "Anno di scoperta",
        "info_section_identity": "Identità",
        "info_section_chemical_properties": "Proprietà chimiche",
        "info_section_physical_properties": "Proprietà fisiche",
    },
    "es": {
        "title": "TABLA PERIÓDICA DE LOS ELEMENTOS",
        "search_placeholder": "Busca por nombre, simbolo o numero atomico...",
        "search_button": "Buscar",
        "first_element": "Primer elemento (p. ej. H)",
        "second_element": "Segundo elemento (p. ej. O)",
        "reset": "Reiniciar",
        "calculate_formula": "Calcular formula",
        "builder_title": "Formula y nomenclatura",
        "right_info": "Info",
        "right_diagram": "Config. electronica",
        "right_compound": "Formula y nomenclatura",
        "right_molar": "Masa molar",
        "right_stoichiometry": "Estequiometría",
        "molar_title": "Calculadora de masa molar",
        "molar_prompt": "Introduce una fórmula química (ej. H2O, Ca(OH)2) para calcular su masa molar.",
        "molar_calculate": "Calcular",
        "molar_error": "Error",
        "stoichiometry_title": "Balanceo de ecuaciones",
        "stoichiometry_prompt": "Introduce una ecuación química (ej. Fe + O2 -> Fe2O3) para balancearla.",
        "stoichiometry_balance": "Balancear",
        "stoichiometry_calc_masses": "Calcular masas",
        "stoichiometry_mass_section": "Introduce la masa para un compuesto:",
        "stoichiometry_error": "Error",
        "selected_none": "Ningun elemento seleccionado",
        "transition_metals": "METALES DE TRANSICION",
        "search_found": "Encontrado: {name} ({symbol})",
        "search_not_found": "No se encontro ningun elemento.",
        "builder_status": "A: {a} | B: {b}",
        "not_selected": "no seleccionado",
        "trend_button_normal": "Vista normal",
        "trend_button_macroclass": "Macroclase",
        "trend_button_metallic": "Caracter metalico",
        "trend_button_nonmetallic": "Caracter no metalico",
        "current_view_normal": "Vista activa: normal",
        "current_view_macro": "Vista activa: macroclase (Metales / Metaloides / No metales)",
        "current_view_metric": "Vista activa: {name} (bajo = azul, alto = amarillo)",
        "current_view_metallic": "Vista activa: caracter metalico",
        "current_view_nonmetallic": "Vista activa: caracter no metalico",
        "info_prompt": "Selecciona un elemento para ver sus detalles.",
        "compound_prompt": "Selecciona A y B, elige los estados de oxidacion y pulsa 'Calcular formula'.",
        "diagram_prompt": "Selecciona un elemento para mostrar el diagrama orbital.",
        "diagram_switch_prompt": (
            "Selecciona la vista 'Configuracion electronica' para mostrar el diagrama "
            "orbital del elemento seleccionado."
        ),
        "diagram_title": "Configuracion electronica",
        "diagram_title_symbol": "Configuracion electronica - {symbol}",
        "diagram_not_available": "Configuracion electronica no disponible.",
        "formula_title": "Formula y nomenclatura",
        "formula_label": "Formula",
        "stock_name": "Nomenclatura de Stock",
        "traditional_name": "Nomenclatura tradicional",
        "oxidation_first": "Ox. #1",
        "oxidation_second": "Ox. #2",
        "first_selected": "Primero: {name} ({symbol})",
        "second_selected": "Segundo: {name} ({symbol})",
        "common_compounds": "Compuestos comunes",
        "no_common_compounds": "Todavia no hay compuestos comunes guardados para esta pareja.",
        "pair_ready_prompt": (
            "Selecciona estados de oxidacion para calcular una formula, o consulta "
            "los compuestos comunes que aparecen abajo."
        ),
        "must_select_ab": "Debes seleccionar A y B antes de combinar los elementos.",
        "same_element": "Por ahora el generador no admite combinar un elemento consigo mismo.",
        "select_oxidation": "Selecciona los estados de oxidacion de ambos elementos.",
        "opposite_sign": "Por ahora el generador solo admite combinaciones con estados de oxidacion de signo opuesto.",
        "traditional_na": "n/d.",
        "more_info": "Resumen basado en los datos actualmente disponibles para este elemento.",
        "metallic_arrow": "Caracter metalico ↙",
        "nonmetallic_arrow": "Caracter no metalico ↗",
        "name": "Nombre",
        "symbol": "Simbolo",
        "atomic_number": "Numero atomico",
        "atomic_mass": "Masa molar",
        "macro_class": "Macroclase",
        "category": "Categoria",
        "period": "Periodo",
        "group": "Grupo",
        "standard_state": "Estado estandar",
        "electronegativity": "Electronegatividad",
        "atomic_radius": "Radio atomico",
        "ionization_energy": "Energia de ionizacion",
        "electron_affinity": "Afinidad electronica",
        "oxidation_states": "Estados de oxidacion",
        "melting_point": "Punto de fusion",
        "boiling_point": "Punto de ebullicion",
        "density": "Densidad",
        "year_discovered": "Ano de descubrimiento",
        "info_section_identity": "Identidad",
        "info_section_chemical_properties": "Propiedades quimicas",
        "info_section_physical_properties": "Propiedades fisicas",
    },
    "fr": {
        "title": "TABLEAU PÉRIODIQUE DES ÉLÉMENTS",
        "search_placeholder": "Rechercher par nom, symbole ou numéro atomique...",
        "search_button": "Rechercher",
        "first_element": "Premier élément (ex. H)",
        "second_element": "Deuxième élément (ex. O)",
        "reset": "Réinitialiser",
        "calculate_formula": "Calculer la formule",
        "builder_title": "Formule et nomenclature",
        "right_info": "Infos",
        "right_diagram": "Config. électronique",
        "right_compound": "Formule et nomenclature",
        "right_molar": "Masse molaire",
        "right_stoichiometry": "Stœchiométrie",
        "molar_title": "Calculateur de masse molaire",
        "molar_prompt": "Entrez une formule chimique (ex. H2O, Ca(OH)2) pour calculer sa masse molaire.",
        "molar_calculate": "Calculer",
        "molar_error": "Erreur",
        "stoichiometry_title": "Équilibrage d'équations",
        "stoichiometry_prompt": "Entrez une équation chimique (ex. Fe + O2 -> Fe2O3) pour l'équilibrer.",
        "stoichiometry_balance": "Équilibrer",
        "stoichiometry_calc_masses": "Calculer les masses",
        "stoichiometry_mass_section": "Entrez la masse pour un composé :",
        "stoichiometry_error": "Erreur",
        "selected_none": "Aucun élément sélectionné",
        "transition_metals": "MÉTAUX DE TRANSITION",
        "search_found": "Trouvé : {name} ({symbol})",
        "search_not_found": "Aucun élément trouvé.",
        "builder_status": "A : {a} | B : {b}",
        "not_selected": "non sélectionné",
        "trend_button_normal": "Vue normale",
        "trend_button_macroclass": "Macro-classe",
        "trend_button_metallic": "Caractère métallique",
        "trend_button_nonmetallic": "Caractère non métallique",
        "current_view_normal": "Vue actuelle : normale",
        "current_view_macro": "Vue actuelle : macro-classe (Métaux / Métalloïdes / Non-métaux)",
        "current_view_metric": "Vue actuelle : {name} (faible = bleu, élevé = jaune)",
        "current_view_metallic": "Vue actuelle : caractère métallique",
        "current_view_nonmetallic": "Vue actuelle : caractère non métallique",
        "info_prompt": "Sélectionnez un élément pour voir ses détails.",
        "compound_prompt": "Sélectionnez A et B, choisissez les états d'oxydation puis cliquez sur 'Calculer la formule'.",
        "diagram_prompt": "Sélectionnez un élément pour afficher le diagramme orbital.",
        "diagram_switch_prompt": (
            "Sélectionnez la vue 'Configuration électronique' pour afficher le diagramme "
            "orbital de l'élément sélectionné."
        ),
        "diagram_title": "Configuration électronique",
        "diagram_title_symbol": "Configuration électronique - {symbol}",
        "diagram_not_available": "Configuration électronique non disponible.",
        "formula_title": "Formule et nomenclature",
        "formula_label": "Formule",
        "stock_name": "Nom de Stock",
        "traditional_name": "Nom traditionnel",
        "oxidation_first": "Ox. n°1",
        "oxidation_second": "Ox. n°2",
        "first_selected": "Premier : {name} ({symbol})",
        "second_selected": "Deuxième : {name} ({symbol})",
        "common_compounds": "Composés courants",
        "no_common_compounds": "Aucun composé courant n'est encore enregistré pour cette paire.",
        "pair_ready_prompt": (
            "Sélectionnez les états d'oxydation pour calculer une formule, ou consultez "
            "les composés courants ci-dessous."
        ),
        "must_select_ab": "Vous devez sélectionner A et B avant de combiner les éléments.",
        "same_element": "Le constructeur actuel ne gère pas encore la combinaison d'un élément avec lui-même.",
        "select_oxidation": "Sélectionnez les états d'oxydation pour les deux éléments.",
        "opposite_sign": "Le constructeur actuel ne gère que les combinaisons avec des états d'oxydation de signe opposé.",
        "traditional_na": "n/d.",
        "more_info": "Aperçu basé sur les données actuellement disponibles pour cet élément.",
        "metallic_arrow": "Caractère métallique ↙",
        "nonmetallic_arrow": "Caractère non métallique ↗",
        "name": "Nom",
        "symbol": "Symbole",
        "atomic_number": "Numéro atomique",
        "atomic_mass": "Masse molaire",
        "macro_class": "Macro-classe",
        "category": "Catégorie",
        "period": "Période",
        "group": "Groupe",
        "standard_state": "État standard",
        "electronegativity": "Électronégativité",
        "atomic_radius": "Rayon atomique",
        "ionization_energy": "Énergie d'ionisation",
        "electron_affinity": "Affinité électronique",
        "oxidation_states": "États d'oxydation",
        "melting_point": "Point de fusion",
        "boiling_point": "Point d'ébullition",
        "density": "Densité",
        "year_discovered": "Année de découverte",
        "info_section_identity": "Identité",
        "info_section_chemical_properties": "Propriétés chimiques",
        "info_section_physical_properties": "Propriétés physiques",
    },
    "de": {
        "title": "PERIODENSYSTEM DER ELEMENTE",
        "search_placeholder": "Nach Name, Symbol oder Ordnungszahl suchen...",
        "search_button": "Suchen",
        "first_element": "Erstes Element (z. B. H)",
        "second_element": "Zweites Element (z. B. O)",
        "reset": "Zurücksetzen",
        "calculate_formula": "Formel berechnen",
        "builder_title": "Formel und Nomenklatur",
        "right_info": "Info",
        "right_diagram": "Elektronenkonf.",
        "right_compound": "Formel und Nomenklatur",
        "right_molar": "Molare Masse",
        "right_stoichiometry": "Stöchiometrie",
        "molar_title": "Molmassenrechner",
        "molar_prompt": "Geben Sie eine chemische Formel ein (z.B. H2O, Ca(OH)2), um die Molmasse zu berechnen.",
        "molar_calculate": "Berechnen",
        "molar_error": "Fehler",
        "stoichiometry_title": "Gleichungsausgleich",
        "stoichiometry_prompt": "Geben Sie eine chemische Gleichung ein (z.B. Fe + O2 -> Fe2O3), um sie auszugleichen.",
        "stoichiometry_balance": "Ausgleichen",
        "stoichiometry_calc_masses": "Massen berechnen",
        "stoichiometry_mass_section": "Masse für eine Verbindung eingeben:",
        "stoichiometry_error": "Fehler",
        "selected_none": "Kein Element ausgewählt",
        "transition_metals": "ÜBERGANGSMETALLE",
        "search_found": "Gefunden: {name} ({symbol})",
        "search_not_found": "Kein Element gefunden.",
        "builder_status": "A: {a} | B: {b}",
        "not_selected": "nicht ausgewählt",
        "trend_button_normal": "Normale Ansicht",
        "trend_button_macroclass": "Makroklasse",
        "trend_button_metallic": "Metallischer Charakter",
        "trend_button_nonmetallic": "Nichtmetallischer Charakter",
        "current_view_normal": "Aktuelle Ansicht: normal",
        "current_view_macro": "Aktuelle Ansicht: Makroklasse (Metalle / Halbmetalle / Nichtmetalle)",
        "current_view_metric": "Aktuelle Ansicht: {name} (niedrig = blau, hoch = gelb)",
        "current_view_metallic": "Aktuelle Ansicht: metallischer Charakter",
        "current_view_nonmetallic": "Aktuelle Ansicht: nichtmetallischer Charakter",
        "info_prompt": "Wählen Sie ein Element aus, um Details zu sehen.",
        "compound_prompt": "Wählen Sie A und B, wählen Sie die Oxidationszahlen und klicken Sie dann auf 'Formel berechnen'.",
        "diagram_prompt": "Wählen Sie ein Element aus, um das Orbitaldiagramm anzuzeigen.",
        "diagram_switch_prompt": (
            "Wählen Sie die Ansicht 'Elektronenkonfiguration', um das Orbitaldiagramm "
            "des ausgewählten Elements anzuzeigen."
        ),
        "diagram_title": "Elektronenkonfiguration",
        "diagram_title_symbol": "Elektronenkonfiguration - {symbol}",
        "diagram_not_available": "Elektronenkonfiguration nicht verfügbar.",
        "formula_title": "Formel und Nomenklatur",
        "formula_label": "Formel",
        "stock_name": "Stock-Name",
        "traditional_name": "Traditioneller Name",
        "oxidation_first": "Ox. #1",
        "oxidation_second": "Ox. #2",
        "first_selected": "Erstes: {name} ({symbol})",
        "second_selected": "Zweites: {name} ({symbol})",
        "common_compounds": "Häufige Verbindungen",
        "no_common_compounds": "Für dieses Paar sind noch keine häufigen Verbindungen gespeichert.",
        "pair_ready_prompt": (
            "Wählen Sie Oxidationszahlen aus, um eine Formel zu berechnen, oder lesen "
            "Sie die unten aufgeführten häufigen Verbindungen."
        ),
        "must_select_ab": "Sie müssen sowohl A als auch B auswählen, bevor Sie die Elemente kombinieren.",
        "same_element": "Der aktuelle Generator unterstützt die Kombination eines Elements mit sich selbst noch nicht.",
        "select_oxidation": "Wählen Sie für beide Elemente Oxidationszahlen aus.",
        "opposite_sign": "Der aktuelle Generator unterstützt nur Kombinationen mit entgegengesetzten Vorzeichen der Oxidationszahlen.",
        "traditional_na": "k.A.",
        "more_info": "Überblick auf Basis der aktuell für dieses Element verfügbaren Daten.",
        "metallic_arrow": "Metallischer Charakter ↙",
        "nonmetallic_arrow": "Nichtmetallischer Charakter ↗",
        "name": "Name",
        "symbol": "Symbol",
        "atomic_number": "Ordnungszahl",
        "atomic_mass": "Molare Masse",
        "macro_class": "Makroklasse",
        "category": "Kategorie",
        "period": "Periode",
        "group": "Gruppe",
        "standard_state": "Standardzustand",
        "electronegativity": "Elektronegativität",
        "atomic_radius": "Atomradius",
        "ionization_energy": "Ionisierungsenergie",
        "electron_affinity": "Elektronenaffinität",
        "oxidation_states": "Oxidationszahlen",
        "melting_point": "Schmelzpunkt",
        "boiling_point": "Siedepunkt",
        "density": "Dichte",
        "year_discovered": "Entdeckungsjahr",
        "info_section_identity": "Identität",
        "info_section_chemical_properties": "Chemische Eigenschaften",
        "info_section_physical_properties": "Physikalische Eigenschaften",
    },
    "zh": {
        "title": "元素周期表",
        "search_placeholder": "按名称、符号或原子序数搜索...",
        "search_button": "搜索",
        "first_element": "第一个元素（例如 H）",
        "second_element": "第二个元素（例如 O）",
        "reset": "重置",
        "calculate_formula": "计算化学式",
        "builder_title": "化学式和命名法",
        "right_info": "信息",
        "right_diagram": "电子排布",
        "right_compound": "化学式和命名法",
        "right_molar": "摩尔质量",
        "right_stoichiometry": "化学计量",
        "molar_title": "摩尔质量计算器",
        "molar_prompt": "输入化学式（如 H2O、Ca(OH)2）以计算其摩尔质量。",
        "molar_calculate": "计算",
        "molar_error": "错误",
        "stoichiometry_title": "方程式配平",
        "stoichiometry_prompt": "输入化学方程式（如 Fe + O2 -> Fe2O3）进行配平。",
        "stoichiometry_balance": "配平",
        "stoichiometry_calc_masses": "计算质量",
        "stoichiometry_mass_section": "输入某化合物的质量：",
        "stoichiometry_error": "错误",
        "selected_none": "未选择元素",
        "transition_metals": "过渡金属",
        "search_found": "找到：{name} ({symbol})",
        "search_not_found": "未找到元素。",
        "builder_status": "A：{a} | B：{b}",
        "not_selected": "未选择",
        "trend_button_normal": "普通视图",
        "trend_button_macroclass": "大类",
        "trend_button_metallic": "金属性",
        "trend_button_nonmetallic": "非金属性",
        "current_view_normal": "当前视图：普通",
        "current_view_macro": "当前视图：大类（金属 / 类金属 / 非金属）",
        "current_view_metric": "当前视图：{name}（低 = 蓝，高 = 黄）",
        "current_view_metallic": "当前视图：金属性",
        "current_view_nonmetallic": "当前视图：非金属性",
        "info_prompt": "选择一个元素以查看详细信息。",
        "compound_prompt": "选择 A 和 B，选择氧化数，然后点击“计算化学式”。",
        "diagram_prompt": "选择一个元素以显示轨道图。",
        "diagram_switch_prompt": "选择“电子排布”视图以显示所选元素的轨道图。",
        "diagram_title": "电子排布",
        "diagram_title_symbol": "电子排布 - {symbol}",
        "diagram_not_available": "电子排布不可用。",
        "formula_title": "化学式和命名法",
        "formula_label": "化学式",
        "stock_name": "Stock 命名",
        "traditional_name": "传统名称",
        "oxidation_first": "氧化数 1",
        "oxidation_second": "氧化数 2",
        "first_selected": "第一个：{name} ({symbol})",
        "second_selected": "第二个：{name} ({symbol})",
        "common_compounds": "常见化合物",
        "no_common_compounds": "该元素对暂未收录常见化合物。",
        "pair_ready_prompt": "选择氧化数来计算一个化学式，或阅读下方列出的常见化合物。",
        "must_select_ab": "在组合元素之前，必须同时选择 A 和 B。",
        "same_element": "当前构建器暂不支持元素与自身组合。",
        "select_oxidation": "请为两个元素选择氧化数。",
        "opposite_sign": "当前构建器仅支持氧化数符号相反的组合。",
        "traditional_na": "无",
        "more_info": "当前显示的是此元素在数据集中可用的关键信息。",
        "metallic_arrow": "金属性 ↙",
        "nonmetallic_arrow": "非金属性 ↗",
        "name": "名称",
        "symbol": "符号",
        "atomic_number": "原子序数",
        "atomic_mass": "摩尔质量",
        "macro_class": "大类",
        "category": "类别",
        "period": "周期",
        "group": "族",
        "standard_state": "标准状态",
        "electronegativity": "电负性",
        "atomic_radius": "原子半径",
        "ionization_energy": "电离能",
        "electron_affinity": "电子亲和能",
        "oxidation_states": "氧化数",
        "melting_point": "熔点",
        "boiling_point": "沸点",
        "density": "密度",
        "year_discovered": "发现年份",
        "info_section_identity": "基本信息",
        "info_section_chemical_properties": "化学性质",
        "info_section_physical_properties": "物理性质",
    },
    "ru": {
        "title": "ПЕРИОДИЧЕСКАЯ ТАБЛИЦА ЭЛЕМЕНТОВ",
        "search_placeholder": "Поиск по названию, символу или атомному номеру...",
        "search_button": "Поиск",
        "first_element": "Первый элемент (напр. H)",
        "second_element": "Второй элемент (напр. O)",
        "reset": "Сброс",
        "calculate_formula": "Вычислить формулу",
        "builder_title": "Формула и номенклатура",
        "right_info": "Инфо",
        "right_diagram": "Эл. конф.",
        "right_compound": "Формула и номенклатура",
        "right_molar": "Молярная масса",
        "right_stoichiometry": "Стехиометрия",
        "molar_title": "Калькулятор молярной массы",
        "molar_prompt": "Введите химическую формулу (напр. H2O, Ca(OH)2) для расчёта молярной массы.",
        "molar_calculate": "Рассчитать",
        "molar_error": "Ошибка",
        "stoichiometry_title": "Уравнивание уравнений",
        "stoichiometry_prompt": "Введите химическое уравнение (напр. Fe + O2 -> Fe2O3) для уравнивания.",
        "stoichiometry_balance": "Уравнять",
        "stoichiometry_calc_masses": "Рассчитать массы",
        "stoichiometry_mass_section": "Введите массу для соединения:",
        "stoichiometry_error": "Ошибка",
        "selected_none": "Элемент не выбран",
        "transition_metals": "ПЕРЕХОДНЫЕ МЕТАЛЛЫ",
        "search_found": "Найдено: {name} ({symbol})",
        "search_not_found": "Элемент не найден.",
        "builder_status": "A: {a} | B: {b}",
        "not_selected": "не выбрано",
        "trend_button_normal": "Обычный вид",
        "trend_button_macroclass": "Макрокласс",
        "trend_button_metallic": "Металлический характер",
        "trend_button_nonmetallic": "Неметаллический характер",
        "current_view_normal": "Текущий вид: обычный",
        "current_view_macro": "Текущий вид: макрокласс (Металлы / Металлоиды / Неметаллы)",
        "current_view_metric": "Текущий вид: {name} (низкое = синий, высокое = жёлтый)",
        "current_view_metallic": "Текущий вид: металлический характер",
        "current_view_nonmetallic": "Текущий вид: неметаллический характер",
        "info_prompt": "Выберите элемент, чтобы увидеть подробности.",
        "compound_prompt": "Выберите A и B, задайте степени окисления и нажмите 'Вычислить формулу'.",
        "diagram_prompt": "Выберите элемент, чтобы показать орбитальную диаграмму.",
        "diagram_switch_prompt": (
            "Выберите вид 'Электронная конфигурация', чтобы показать орбитальную "
            "диаграмму выбранного элемента."
        ),
        "diagram_title": "Электронная конфигурация",
        "diagram_title_symbol": "Электронная конфигурация - {symbol}",
        "diagram_not_available": "Электронная конфигурация недоступна.",
        "formula_title": "Формула и номенклатура",
        "formula_label": "Формула",
        "stock_name": "Название по Стоку",
        "traditional_name": "Традиционное название",
        "oxidation_first": "Ox. #1",
        "oxidation_second": "Ox. #2",
        "first_selected": "Первый: {name} ({symbol})",
        "second_selected": "Второй: {name} ({symbol})",
        "common_compounds": "Распространённые соединения",
        "no_common_compounds": "Для этой пары пока нет сохранённых распространённых соединений.",
        "pair_ready_prompt": (
            "Выберите степени окисления, чтобы вычислить формулу, или прочитайте "
            "список распространённых соединений ниже."
        ),
        "must_select_ab": "Перед объединением элементов нужно выбрать и A, и B.",
        "same_element": "Текущий модуль пока не поддерживает объединение элемента с самим собой.",
        "select_oxidation": "Выберите степени окисления для обоих элементов.",
        "opposite_sign": "Текущий модуль поддерживает только комбинации с противоположными знаками степеней окисления.",
        "traditional_na": "н/д",
        "more_info": "Сейчас показаны ключевые данные, доступные для этого элемента в наборе данных.",
        "metallic_arrow": "Металлический характер ↙",
        "nonmetallic_arrow": "Неметаллический характер ↗",
        "name": "Название",
        "symbol": "Символ",
        "atomic_number": "Атомный номер",
        "atomic_mass": "Молярная масса",
        "macro_class": "Макрокласс",
        "category": "Категория",
        "period": "Период",
        "group": "Группа",
        "standard_state": "Стандартное состояние",
        "electronegativity": "Электроотрицательность",
        "atomic_radius": "Атомный радиус",
        "ionization_energy": "Энергия ионизации",
        "electron_affinity": "Сродство к электрону",
        "oxidation_states": "Степени окисления",
        "melting_point": "Температура плавления",
        "boiling_point": "Температура кипения",
        "density": "Плотность",
        "year_discovered": "Год открытия",
        "info_section_identity": "Идентичность",
        "info_section_chemical_properties": "Химические свойства",
        "info_section_physical_properties": "Физические свойства",
    },
}


VISIBLE_LANGUAGE_CODES = tuple(code for code, _ in ALL_LANGUAGE_OPTIONS)

LANGUAGE_READINESS_REQUIRED_TEXT_KEYS = (
    "about_button",
    "about_description",
    "about_dialog_title",
    "about_version",
    "atomic_mass",
    "atomic_number",
    "atomic_radius",
    "boiling_point",
    "builder_scope_note",
    "builder_selection_current",
    "builder_selection_empty",
    "builder_selection_hint",
    "builder_selection_title",
    "builder_status",
    "builder_slot_a_title",
    "builder_slot_b_title",
    "builder_title",
    "builder_use_selected_a",
    "builder_use_selected_b",
    "calculate_formula",
    "category",
    "close_dialog",
    "common_compounds",
    "compound_prompt",
    "compound_scope_note",
    "current_limits_body",
    "current_limits_title",
    "current_view_macro",
    "current_view_metallic",
    "current_view_metric",
    "current_view_nonmetallic",
    "current_view_normal",
    "density",
    "diagram_not_available",
    "diagram_prompt",
    "diagram_switch_prompt",
    "diagram_title",
    "diagram_title_symbol",
    "electron_affinity",
    "electronegativity",
    "first_element",
    "first_selected",
    "formula_label",
    "formula_title",
    "group",
    "info_prompt",
    "info_section_chemical_properties",
    "info_section_identity",
    "info_section_physical_properties",
    "ionization_energy",
    "macro_class",
    "melting_point",
    "metallic_arrow",
    "molar_calculate",
    "molar_error",
    "molar_prompt",
    "molar_title",
    "more_info",
    "must_select_ab",
    "name",
    "no_common_compounds",
    "nonmetallic_arrow",
    "not_selected",
    "opposite_sign",
    "oxidation_first",
    "oxidation_second",
    "oxidation_states",
    "pair_ready_prompt",
    "period",
    "quick_help_body",
    "quick_help_title",
    "reset",
    "right_compound",
    "right_diagram",
    "right_info",
    "right_molar",
    "right_stoichiometry",
    "same_element",
    "scientific_data_partial_note",
    "scientific_data_partial_note_more",
    "search_button",
    "search_found",
    "search_helper",
    "search_not_found",
    "search_placeholder",
    "search_title",
    "second_element",
    "second_selected",
    "select_oxidation",
    "selected_none",
    "standard_state",
    "stoichiometry_balance",
    "stoichiometry_calc_masses",
    "stoichiometry_error",
    "stoichiometry_mass_section",
    "stoichiometry_prompt",
    "stoichiometry_title",
    "stock_name",
    "symbol",
    "title",
    "traditional_na",
    "traditional_name",
    "transition_metals",
    "trend_button_macroclass",
    "trend_button_radius",
    "trend_button_ionization",
    "trend_button_affinity",
    "trend_button_electronegativity",
    "trend_button_metallic",
    "trend_button_nonmetallic",
    "trend_button_normal",
    "year_discovered",
)

LANGUAGE_OPTIONS = [
    (code, label)
    for code, label in ALL_LANGUAGE_OPTIONS
    if code in VISIBLE_LANGUAGE_CODES
]

UI_TEXTS["en"].update(
    {
        "builder_title": "Simple compounds",
        "about_button": "About",
        "about_dialog_title": "About {app_name}",
        "about_version": "Version: {version}",
        "about_description": (
            "Desktop reference app for exploring element data, electron "
            "configuration, and a limited binary compound builder."
        ),
        "builder_scope_note": (
            "Beta: simple binary compounds only."
        ),
        "search_title": "Find an element",
        "search_helper": "Search by name, symbol, or atomic number.",
        "builder_selection_title": "Current selection",
        "builder_selection_hint": "Pick one element at a time, then send it to A or B.",
        "builder_selection_empty": "No element selected yet.",
        "builder_selection_current": "{name} ({symbol})",
        "builder_slot_a_title": "1. Fill A",
        "builder_slot_b_title": "2. Fill B",
        "builder_use_selected_a": "Use for A",
        "builder_use_selected_b": "Use for B",
        "trend_button_normal": "Normal",
        "trend_button_macroclass": "Macro",
        "trend_button_radius": "Radius",
        "trend_button_ionization": "Ionization",
        "trend_button_affinity": "Affinity",
        "trend_button_electronegativity": "Electroneg.",
        "trend_button_metallic": "Metallic",
        "trend_button_nonmetallic": "Nonmetallic",
        "right_compound": "Compounds",
        "quick_help_title": "Quick help",
        "quick_help_body": (
            "- Search by name, symbol, or atomic number, then press Enter or pick "
            "a suggestion.\n"
            "- Use the language selector to switch the UI language.\n"
            "- Use the Info, Electron config., and Compounds panels to inspect "
            "the selected element.\n"
            "- In the compound builder, select two elements, choose one oxidation "
            "state for each, then calculate one simple binary formula."
        ),
        "current_limits_title": "Current limits",
        "current_limits_body": (
            "- The compound builder is limited to simple binary compounds with "
            "opposite-sign oxidation states, and the nomenclature shown only "
            "covers the currently implemented paths.\n"
            "- Some scientific fields can still be missing or incomplete for some "
            "elements.\n"
            "- Visible UI languages follow the audited localizations currently "
            "bundled with the app."
        ),
        "close_dialog": "Close",
        "formula_title": "Simple compounds",
        "compound_prompt": (
            "Choose one element at a time, send it to A or B, then choose the "
            "oxidation states and calculate one simple binary formula."
        ),
        "compound_scope_note": (
            "Scope: simple binary compounds only. Same-element pairs and same-sign "
            "oxidation states are not supported yet."
        ),
        "no_common_compounds": "No curated common compounds are stored for this pair yet.",
        "pair_ready_prompt": (
            "A and B are ready. Select oxidation states to calculate one simple "
            "binary formula, or read the curated compounds listed below."
        ),
        "scientific_data_partial_note": (
            "Dataset note: some scientific values are currently unavailable for this "
            "element: {fields}."
        ),
        "scientific_data_partial_note_more": (
            "Dataset note: some scientific values are currently unavailable for this "
            "element, including {fields}, and {count} more."
        ),
        "metallic_arrow": "Metallic character (towards bottom-left)",
        "nonmetallic_arrow": "Nonmetallic character (towards top-right)",
    }
)

UI_TEXTS["it"].update(
    {
        "builder_title": "Composti semplici",
        "about_button": "Informazioni",
        "about_dialog_title": "Informazioni su {app_name}",
        "about_version": "Versione: {version}",
        "about_description": (
            "App desktop di consultazione per esplorare i dati degli elementi, la "
            "configurazione elettronica e un builder attualmente limitato ai "
            "composti binari."
        ),
        "builder_scope_note": (
            "Beta: solo composti binari semplici."
        ),
        "search_title": "Trova un elemento",
        "search_helper": "Cerca per nome, simbolo o numero atomico.",
        "builder_selection_title": "Selezione corrente",
        "builder_selection_hint": "Scegli un elemento alla volta, poi assegnalo ad A o B.",
        "builder_selection_empty": "Nessun elemento selezionato.",
        "builder_selection_current": "{name} ({symbol})",
        "builder_slot_a_title": "1. Imposta A",
        "builder_slot_b_title": "2. Imposta B",
        "builder_use_selected_a": "Usa per A",
        "builder_use_selected_b": "Usa per B",
        "trend_button_normal": "Normale",
        "trend_button_macroclass": "Macro",
        "trend_button_radius": "Raggio",
        "trend_button_ionization": "Ionizzazione",
        "trend_button_affinity": "Affinità",
        "trend_button_electronegativity": "Elettroneg.",
        "trend_button_metallic": "Metallico",
        "trend_button_nonmetallic": "Non metallico",
        "right_compound": "Composti",
        "quick_help_title": "Aiuto rapido",
        "quick_help_body": (
            "- Cerca per nome, simbolo o numero atomico, poi premi Invio oppure "
            "scegli un suggerimento.\n"
            "- Usa il selettore della lingua per cambiare la lingua "
            "dell'interfaccia.\n"
            "- Usa i pannelli Info, Config. elettronica e Composti per consultare "
            "l'elemento selezionato.\n"
            "- Nel builder dei composti, seleziona due elementi, scegli uno stato "
            "di ossidazione per ciascuno e calcola una sola formula binaria "
            "semplice."
        ),
        "current_limits_title": "Limiti correnti",
        "current_limits_body": (
            "- Il builder dei composti è limitato ai composti binari semplici con "
            "numeri di ossidazione di segno opposto e la nomenclatura mostrata "
            "copre solo i casi attualmente implementati.\n"
            "- Alcuni campi scientifici possono ancora essere mancanti o incompleti "
            "per certi elementi.\n"
            "- Le lingue visibili dell'interfaccia seguono le localizzazioni "
            "attualmente verificate e incluse nell'app."
        ),
        "close_dialog": "Chiudi",
        "formula_title": "Composti semplici",
        "compound_prompt": (
            "Scegli un elemento alla volta, assegnalo ad A o B, poi imposta gli "
            "stati di ossidazione e calcola una formula binaria semplice."
        ),
        "compound_scope_note": (
            "Ambito: solo composti binari semplici. Le coppie con lo stesso "
            "elemento e le combinazioni con numeri di ossidazione dello stesso "
            "segno non sono ancora supportate."
        ),
        "no_common_compounds": "Nessun composto comune già curato per questa coppia.",
        "pair_ready_prompt": (
            "A e B sono pronti. Seleziona gli stati di ossidazione per calcolare una "
            "formula binaria semplice, oppure consulta i composti curati qui sotto."
        ),
        "scientific_data_partial_note": (
            "Nota dataset: alcuni valori scientifici non sono al momento "
            "disponibili per questo elemento: {fields}."
        ),
        "scientific_data_partial_note_more": (
            "Nota dataset: alcuni valori scientifici non sono al momento "
            "disponibili per questo elemento, inclusi {fields}, e altri {count}."
        ),
        "metallic_arrow": "Carattere metallico (verso il basso a sinistra)",
        "nonmetallic_arrow": "Carattere non metallico (verso l'alto a destra)",
    }
)

UI_TEXTS["es"].update(
    {
        "title": "TABLA PERIÓDICA DE LOS ELEMENTOS",
        "search_placeholder": "Busca por nombre, símbolo o número atómico...",
        "search_button": "Buscar",
        "calculate_formula": "Calcular fórmula",
        "builder_title": "Compuestos simples",
        "right_info": "Información",
        "right_diagram": "Config. electrónica",
        "right_compound": "Compuestos",
        "selected_none": "Ningún elemento seleccionado",
        "transition_metals": "METALES DE TRANSICIÓN",
        "trend_button_normal": "Normal",
        "trend_button_macroclass": "Macro",
        "trend_button_radius": "Radio",
        "trend_button_ionization": "Ionización",
        "trend_button_affinity": "Afinidad",
        "trend_button_electronegativity": "Electroneg.",
        "trend_button_metallic": "Metálico",
        "trend_button_nonmetallic": "No metálico",
        "current_view_metallic": "Vista activa: carácter metálico",
        "current_view_nonmetallic": "Vista activa: carácter no metálico",
        "compound_prompt": (
            "Elige un elemento cada vez, asígnalo a A o B, luego selecciona los "
            "estados de oxidación y calcula una fórmula binaria simple."
        ),
        "formula_title": "Compuestos simples",
        "formula_label": "Fórmula",
        "stock_name": "Nombre de Stock",
        "pair_ready_prompt": (
            "A y B están listos. Selecciona los estados de oxidación para calcular "
            "una fórmula binaria simple o consulta los compuestos revisados que "
            "aparecen abajo."
        ),
        "traditional_na": "n/d.",
        "metallic_arrow": "Carácter metálico (hacia abajo a la izquierda)",
        "nonmetallic_arrow": "Carácter no metálico (hacia arriba a la derecha)",
        "symbol": "Símbolo",
        "atomic_number": "Número atómico",
        "atomic_mass": "Masa atómica",
        "category": "Categoría",
        "period": "Período",
        "standard_state": "Estado estándar",
        "atomic_radius": "Radio atómico",
        "ionization_energy": "Energía de ionización",
        "electron_affinity": "Afinidad electrónica",
        "oxidation_states": "Estados de oxidación",
        "melting_point": "Punto de fusión",
        "year_discovered": "Año de descubrimiento",
        "info_section_identity": "Datos básicos",
        "info_section_chemical_properties": "Propiedades químicas",
        "info_section_physical_properties": "Propiedades físicas",
        "about_button": "Acerca de",
        "about_dialog_title": "Acerca de {app_name}",
        "about_version": "Versión: {version}",
        "about_description": (
            "Aplicación de consulta de escritorio para explorar datos de los "
            "elementos, la configuración electrónica y un generador actualmente "
            "limitado a compuestos binarios."
        ),
        "builder_scope_note": "Beta: solo compuestos binarios simples.",
        "search_title": "Buscar un elemento",
        "search_helper": "Busca por nombre, símbolo o número atómico.",
        "builder_selection_title": "Selección actual",
        "builder_selection_hint": (
            "Elige un elemento cada vez y asígnalo a A o B."
        ),
        "builder_selection_empty": "Aún no hay ningún elemento seleccionado.",
        "builder_selection_current": "{name} ({symbol})",
        "builder_slot_a_title": "1. Completa A",
        "builder_slot_b_title": "2. Completa B",
        "builder_use_selected_a": "Usar para A",
        "builder_use_selected_b": "Usar para B",
        "quick_help_title": "Ayuda rápida",
        "quick_help_body": (
            "- Busca por nombre, símbolo o número atómico, luego pulsa Intro o "
            "elige una sugerencia.\n"
            "- Usa el selector de idioma para cambiar la lengua de la interfaz.\n"
            "- Usa los paneles Información, Config. electrónica y Compuestos para "
            "revisar el elemento seleccionado.\n"
            "- En el generador de compuestos, selecciona dos elementos, elige un "
            "estado de oxidación para cada uno y calcula una sola fórmula binaria "
            "simple."
        ),
        "current_limits_title": "Límites actuales",
        "current_limits_body": (
            "- El generador de compuestos está limitado a compuestos binarios "
            "simples con estados de oxidación de signo opuesto, y la nomenclatura "
            "mostrada solo cubre los casos implementados por ahora.\n"
            "- Algunos campos científicos todavía pueden faltar o estar incompletos "
            "para ciertos elementos.\n"
            "- Las lenguas visibles de la interfaz siguen las localizaciones "
            "auditadas que hoy están incluidas en la aplicación."
        ),
        "close_dialog": "Cerrar",
        "compound_scope_note": (
            "Alcance: solo compuestos binarios simples. Las parejas del mismo "
            "elemento y las combinaciones con números de oxidación del mismo signo "
            "todavía no están disponibles."
        ),
        "no_common_compounds": (
            "Todavía no hay compuestos comunes revisados para esta pareja."
        ),
        "scientific_data_partial_note": (
            "Nota del conjunto de datos: algunos valores científicos no están "
            "disponibles por ahora para este elemento: {fields}."
        ),
        "scientific_data_partial_note_more": (
            "Nota del conjunto de datos: algunos valores científicos no están "
            "disponibles por ahora para este elemento, incluidos {fields}, y "
            "{count} más."
        ),
    }
)

UI_TEXTS["fr"].update(
    {
        "builder_title": "Composés simples",
        "about_button": "À propos",
        "about_dialog_title": "À propos de {app_name}",
        "about_version": "Version : {version}",
        "about_description": (
            "Application de bureau de référence pour explorer les données des "
            "éléments, la configuration électronique et un constructeur "
            "actuellement limité aux composés binaires."
        ),
        "builder_scope_note": "Bêta : composés binaires simples uniquement.",
        "search_title": "Trouver un élément",
        "search_helper": "Recherchez par nom, symbole ou numéro atomique.",
        "builder_selection_title": "Sélection actuelle",
        "builder_selection_hint": (
            "Choisissez un élément à la fois, puis affectez-le à A ou B."
        ),
        "builder_selection_empty": "Aucun élément sélectionné pour le moment.",
        "builder_selection_current": "{name} ({symbol})",
        "builder_slot_a_title": "1. Remplir A",
        "builder_slot_b_title": "2. Remplir B",
        "builder_use_selected_a": "Utiliser pour A",
        "builder_use_selected_b": "Utiliser pour B",
        "trend_button_normal": "Normal",
        "trend_button_macroclass": "Macro",
        "trend_button_radius": "Rayon",
        "trend_button_ionization": "Ionisation",
        "trend_button_affinity": "Affinité",
        "trend_button_electronegativity": "Électronég.",
        "trend_button_metallic": "Métallique",
        "trend_button_nonmetallic": "Non métallique",
        "right_compound": "Composés",
        "quick_help_title": "Aide rapide",
        "quick_help_body": (
            "- Recherchez par nom, symbole ou numéro atomique, puis appuyez sur "
            "Entrée ou choisissez une suggestion.\n"
            "- Utilisez le sélecteur de langue pour changer la langue de "
            "l'interface.\n"
            "- Utilisez les panneaux Infos, Config. électronique et Composés pour "
            "examiner l'élément sélectionné.\n"
            "- Dans le constructeur de composés, sélectionnez deux éléments, "
            "choisissez un état d'oxydation pour chacun, puis calculez une seule "
            "formule binaire simple."
        ),
        "current_limits_title": "Limites actuelles",
        "current_limits_body": (
            "- Le constructeur de composés est limité aux composés binaires simples "
            "avec des états d'oxydation de signe opposé, et la nomenclature "
            "affichée ne couvre que les cas actuellement implémentés.\n"
            "- Certains champs scientifiques peuvent encore manquer ou rester "
            "incomplets pour certains éléments.\n"
            "- Les langues visibles de l'interface suivent les localisations "
            "auditées actuellement incluses dans l'application."
        ),
        "close_dialog": "Fermer",
        "formula_title": "Composés simples",
        "compound_prompt": (
            "Choisissez un élément à la fois, affectez-le à A ou B, puis "
            "sélectionnez les états d'oxydation et calculez une formule binaire "
            "simple."
        ),
        "compound_scope_note": (
            "Portée : composés binaires simples uniquement. Les paires formées du "
            "même élément et les combinaisons avec des états d'oxydation de même "
            "signe ne sont pas encore prises en charge."
        ),
        "stock_name": "Nom selon Stock",
        "no_common_compounds": (
            "Aucun composé courant vérifié n'est encore enregistré pour cette "
            "paire."
        ),
        "pair_ready_prompt": (
            "A et B sont prêts. Sélectionnez les états d'oxydation pour calculer "
            "une formule binaire simple, ou consultez les composés vérifiés "
            "ci-dessous."
        ),
        "scientific_data_partial_note": (
            "Note du jeu de données : certaines valeurs scientifiques ne sont pas "
            "encore disponibles pour cet élément : {fields}."
        ),
        "scientific_data_partial_note_more": (
            "Note du jeu de données : certaines valeurs scientifiques ne sont pas "
            "encore disponibles pour cet élément, notamment {fields}, ainsi que "
            "{count} autres."
        ),
        "metallic_arrow": "Caractère métallique (vers le bas à gauche)",
        "nonmetallic_arrow": "Caractère non métallique (vers le haut à droite)",
        "info_section_identity": "Identification",
    }
)

UI_TEXTS["de"].update(
    {
        "builder_title": "Einfache Verbindungen",
        "about_button": "Über",
        "about_dialog_title": "Über {app_name}",
        "about_version": "Version: {version}",
        "about_description": (
            "Desktop-Nachschlagewerk zum Erkunden von Elementdaten, "
            "Elektronenkonfigurationen und einem derzeit auf binäre Verbindungen "
            "begrenzten Generator."
        ),
        "builder_scope_note": "Beta: nur einfache binäre Verbindungen.",
        "search_title": "Element finden",
        "search_helper": "Suche nach Name, Symbol oder Ordnungszahl.",
        "builder_selection_title": "Aktuelle Auswahl",
        "builder_selection_hint": (
            "Wählen Sie jeweils ein Element aus und weisen Sie es dann A oder B zu."
        ),
        "builder_selection_empty": "Noch kein Element ausgewählt.",
        "builder_selection_current": "{name} ({symbol})",
        "builder_slot_a_title": "1. A füllen",
        "builder_slot_b_title": "2. B füllen",
        "builder_use_selected_a": "Für A verwenden",
        "builder_use_selected_b": "Für B verwenden",
        "trend_button_normal": "Normal",
        "trend_button_macroclass": "Makro",
        "trend_button_radius": "Radius",
        "trend_button_ionization": "Ionisierung",
        "trend_button_affinity": "Affinität",
        "trend_button_electronegativity": "Elektroneg.",
        "trend_button_metallic": "Metallisch",
        "trend_button_nonmetallic": "Nichtmetallisch",
        "right_compound": "Verbindungen",
        "quick_help_title": "Schnellhilfe",
        "quick_help_body": (
            "- Suchen Sie nach Name, Symbol oder Ordnungszahl und drücken Sie dann "
            "Enter oder wählen Sie einen Vorschlag aus.\n"
            "- Verwenden Sie den Sprachumschalter, um die Sprache der Oberfläche zu "
            "wechseln.\n"
            "- Nutzen Sie die Bereiche Info, Elektronenkonf. und Verbindungen, um "
            "das ausgewählte Element zu prüfen.\n"
            "- Wählen Sie im Verbindungs-Generator zwei Elemente, setzen Sie je "
            "einen Oxidationszustand und berechnen Sie eine einfache binäre Formel."
        ),
        "current_limits_title": "Aktuelle Grenzen",
        "current_limits_body": (
            "- Der Verbindungs-Generator ist auf einfache binäre Verbindungen mit "
            "entgegengesetzten Vorzeichen der Oxidationszahlen begrenzt, und die "
            "angezeigte Nomenklatur deckt nur die derzeit implementierten Pfade "
            "ab.\n"
            "- Einige wissenschaftliche Felder können für bestimmte Elemente noch "
            "fehlen oder unvollständig sein.\n"
            "- Die sichtbaren UI-Sprachen folgen den aktuell geprüften "
            "Lokalisierungen in der App."
        ),
        "close_dialog": "Schließen",
        "formula_title": "Einfache Verbindungen",
        "compound_prompt": (
            "Wählen Sie jeweils ein Element, weisen Sie es A oder B zu, wählen Sie "
            "dann die Oxidationszahlen und berechnen Sie eine einfache binäre "
            "Formel."
        ),
        "compound_scope_note": (
            "Umfang: nur einfache binäre Verbindungen. Paare desselben Elements und "
            "Kombinationen mit Oxidationszahlen gleichen Vorzeichens werden noch "
            "nicht unterstützt."
        ),
        "no_common_compounds": (
            "Für dieses Paar sind noch keine kuratierten häufigen Verbindungen "
            "gespeichert."
        ),
        "pair_ready_prompt": (
            "A und B sind bereit. Wählen Sie Oxidationszahlen aus, um eine einfache "
            "binäre Formel zu berechnen, oder lesen Sie die geprüften Verbindungen "
            "unten."
        ),
        "scientific_data_partial_note": (
            "Datensatzhinweis: Einige wissenschaftliche Werte sind für dieses "
            "Element derzeit nicht verfügbar: {fields}."
        ),
        "scientific_data_partial_note_more": (
            "Datensatzhinweis: Einige wissenschaftliche Werte sind für dieses "
            "Element derzeit nicht verfügbar, darunter {fields}, sowie {count} "
            "weitere."
        ),
        "metallic_arrow": "Metallischer Charakter (Richtung unten links)",
        "nonmetallic_arrow": "Nichtmetallischer Charakter (Richtung oben rechts)",
        "info_section_identity": "Grunddaten",
    }
)

UI_TEXTS["zh"].update(
    {
        "builder_title": "简单化合物",
        "about_button": "关于",
        "about_dialog_title": "关于 {app_name}",
        "about_version": "版本：{version}",
        "about_description": (
            "用于查阅元素数据、电子排布和当前仅支持简单二元化合物构建的桌面参考应用。"
        ),
        "builder_scope_note": "测试版：仅支持简单二元化合物。",
        "search_title": "查找元素",
        "search_helper": "按名称、符号或原子序数搜索。",
        "builder_selection_title": "当前选择",
        "builder_selection_hint": "每次选择一个元素，然后把它分配给 A 或 B。",
        "builder_selection_empty": "尚未选择任何元素。",
        "builder_selection_current": "{name} ({symbol})",
        "builder_slot_a_title": "1. 设置 A",
        "builder_slot_b_title": "2. 设置 B",
        "builder_use_selected_a": "用于 A",
        "builder_use_selected_b": "用于 B",
        "trend_button_normal": "普通",
        "trend_button_macroclass": "大类",
        "trend_button_radius": "半径",
        "trend_button_ionization": "电离",
        "trend_button_affinity": "亲和",
        "trend_button_electronegativity": "电负性",
        "trend_button_metallic": "金属性",
        "trend_button_nonmetallic": "非金属性",
        "right_compound": "化合物",
        "quick_help_title": "快速帮助",
        "quick_help_body": (
            "- 按名称、符号或原子序数搜索，然后按回车或选择建议项。\n"
            "- 使用语言选择器切换界面语言。\n"
            "- 使用信息、电子排布和化合物面板查看当前选中的元素。\n"
            "- 在化合物构建器中选择两个元素，分别设置一个氧化数，然后计算一个简单的二元化学式。"
        ),
        "current_limits_title": "当前限制",
        "current_limits_body": (
            "- 化合物构建器目前仅支持氧化数符号相反的简单二元化合物，显示的命名也只覆盖当前已经实现的路径。\n"
            "- 某些元素的科学字段仍可能缺失或不完整。\n"
            "- 当前界面中可见的语言以应用内已审校的本地化为准。"
        ),
        "close_dialog": "关闭",
        "formula_title": "简单化合物",
        "compound_prompt": (
            "依次选择元素并分配给 A 或 B，然后选择氧化数并计算一个简单的二元化学式。"
        ),
        "compound_scope_note": (
            "范围：仅支持简单二元化合物。暂不支持同元素配对和氧化数同号的组合。"
        ),
        "stock_name": "斯托克命名法",
        "traditional_name": "传统命名法",
        "oxidation_first": "氧化数 #1",
        "oxidation_second": "氧化数 #2",
        "no_common_compounds": "这对元素暂未收录经过校对的常见化合物。",
        "pair_ready_prompt": (
            "A 和 B 已就绪。请选择氧化数来计算一个简单的二元化学式，或查看下方收录的化合物。"
        ),
        "scientific_data_partial_note": (
            "数据集说明：此元素当前缺少以下科学数值：{fields}。"
        ),
        "scientific_data_partial_note_more": (
            "数据集说明：此元素当前缺少以下科学数值：{fields}，以及另外 {count} 项。"
        ),
        "metallic_arrow": "金属性（朝左下）",
        "nonmetallic_arrow": "非金属性（朝右上）",
    }
)

UI_TEXTS["ru"].update(
    {
        "builder_title": "Простые соединения",
        "about_button": "О программе",
        "about_dialog_title": "О программе {app_name}",
        "about_version": "Версия: {version}",
        "about_description": (
            "Настольное справочное приложение для просмотра данных об элементах, "
            "электронной конфигурации и конструктора, пока ограниченного простыми "
            "бинарными соединениями."
        ),
        "builder_scope_note": "Бета: только простые бинарные соединения.",
        "search_title": "Найти элемент",
        "search_helper": "Поиск по названию, символу или атомному номеру.",
        "builder_selection_title": "Текущий выбор",
        "builder_selection_hint": (
            "Выбирайте по одному элементу и затем отправляйте его в A или B."
        ),
        "builder_selection_empty": "Элемент ещё не выбран.",
        "builder_selection_current": "{name} ({symbol})",
        "builder_slot_a_title": "1. Заполнить A",
        "builder_slot_b_title": "2. Заполнить B",
        "builder_use_selected_a": "Использовать для A",
        "builder_use_selected_b": "Использовать для B",
        "trend_button_normal": "Обычный",
        "trend_button_macroclass": "Макро",
        "trend_button_radius": "Радиус",
        "trend_button_ionization": "Ионизация",
        "trend_button_affinity": "Сродство",
        "trend_button_electronegativity": "Электроотр.",
        "trend_button_metallic": "Металлич.",
        "trend_button_nonmetallic": "Неметаллич.",
        "right_info": "Сведения",
        "right_compound": "Соединения",
        "quick_help_title": "Краткая помощь",
        "quick_help_body": (
            "- Ищите по названию, символу или атомному номеру, затем нажмите Enter "
            "или выберите подсказку.\n"
            "- Используйте переключатель языка, чтобы менять язык интерфейса.\n"
            "- Используйте панели Сведения, Эл. конф. и Соединения, чтобы "
            "просматривать выбранный элемент.\n"
            "- В конструкторе соединений выберите два элемента, задайте по одной "
            "степени окисления для каждого и вычислите одну простую бинарную "
            "формулу."
        ),
        "current_limits_title": "Текущие ограничения",
        "current_limits_body": (
            "- Конструктор соединений ограничен простыми бинарными соединениями с "
            "противоположными знаками степеней окисления, а показанная номенклатура "
            "охватывает только уже реализованные сценарии.\n"
            "- Для части элементов некоторые научные поля всё ещё могут быть "
            "неполными или отсутствовать.\n"
            "- Видимые языки интерфейса соответствуют локализациям, прошедшим "
            "аудит и включённым в приложение."
        ),
        "close_dialog": "Закрыть",
        "formula_title": "Простые соединения",
        "compound_prompt": (
            "Выбирайте элементы по одному, отправляйте их в A или B, затем задавайте "
            "степени окисления и вычисляйте одну простую бинарную формулу."
        ),
        "compound_scope_note": (
            "Область: только простые бинарные соединения. Пары одного и того же "
            "элемента и сочетания с одинаковым знаком степеней окисления пока не "
            "поддерживаются."
        ),
        "oxidation_first": "Ст. ок. #1",
        "oxidation_second": "Ст. ок. #2",
        "no_common_compounds": (
            "Для этой пары пока нет проверенных распространённых соединений."
        ),
        "pair_ready_prompt": (
            "A и B готовы. Выберите степени окисления, чтобы вычислить одну простую "
            "бинарную формулу, или просмотрите проверенные соединения ниже."
        ),
        "scientific_data_partial_note": (
            "Примечание к набору данных: некоторые научные значения сейчас "
            "недоступны для этого элемента: {fields}."
        ),
        "scientific_data_partial_note_more": (
            "Примечание к набору данных: некоторые научные значения сейчас "
            "недоступны для этого элемента, включая {fields}, и ещё {count}."
        ),
        "metallic_arrow": "Металлический характер (к нижнему левому углу)",
        "nonmetallic_arrow": "Неметаллический характер (к верхнему правому углу)",
        "info_section_identity": "Основные сведения",
    }
)

LOCALIZED_CATEGORY_TEXTS = {
    "en": {
        "actinide": "Actinide",
        "alkali metal": "Alkali Metal",
        "alkaline earth metal": "Alkaline Earth Metal",
        "halogen": "Halogen",
        "lanthanide": "Lanthanide",
        "metalloid": "Metalloid",
        "noble gas": "Noble Gas",
        "nonmetal": "Nonmetal",
        "post-transition metal": "Post-Transition Metal",
        "transition metal": "Transition Metal",
    },
    "it": {
        "actinide": "Attinide",
        "alkali metal": "Metallo alcalino",
        "alkaline earth metal": "Metallo alcalino-terroso",
        "halogen": "Alogeno",
        "lanthanide": "Lantanide",
        "metalloid": "Semimetallo",
        "noble gas": "Gas nobile",
        "nonmetal": "Non metallo",
        "post-transition metal": "Metallo post-transizione",
        "transition metal": "Metallo di transizione",
    },
    "es": {
        "actinide": "Actínido",
        "alkali metal": "Metal alcalino",
        "alkaline earth metal": "Metal alcalinotérreo",
        "halogen": "Halógeno",
        "lanthanide": "Lantánido",
        "metalloid": "Metaloide",
        "noble gas": "Gas noble",
        "nonmetal": "No metal",
        "post-transition metal": "Metal postransición",
        "transition metal": "Metal de transición",
    },
    "fr": {
        "actinide": "Actinide",
        "alkali metal": "Métal alcalin",
        "alkaline earth metal": "Métal alcalino-terreux",
        "halogen": "Halogène",
        "lanthanide": "Lanthanide",
        "metalloid": "Métalloïde",
        "noble gas": "Gaz noble",
        "nonmetal": "Non-métal",
        "post-transition metal": "Métal post-transition",
        "transition metal": "Métal de transition",
    },
    "de": {
        "actinide": "Actinoid",
        "alkali metal": "Alkalimetall",
        "alkaline earth metal": "Erdalkalimetall",
        "halogen": "Halogen",
        "lanthanide": "Lanthanoid",
        "metalloid": "Halbmetall",
        "noble gas": "Edelgas",
        "nonmetal": "Nichtmetall",
        "post-transition metal": "Post-Übergangsmetall",
        "transition metal": "Übergangsmetall",
    },
    "zh": {
        "actinide": "锕系元素",
        "alkali metal": "碱金属",
        "alkaline earth metal": "碱土金属",
        "halogen": "卤素",
        "lanthanide": "镧系元素",
        "metalloid": "类金属",
        "noble gas": "稀有气体",
        "nonmetal": "非金属",
        "post-transition metal": "后过渡金属",
        "transition metal": "过渡金属",
    },
    "ru": {
        "actinide": "Актиноид",
        "alkali metal": "Щелочной металл",
        "alkaline earth metal": "Щёлочноземельный металл",
        "halogen": "Галоген",
        "lanthanide": "Лантаноид",
        "metalloid": "Металлоид",
        "noble gas": "Благородный газ",
        "nonmetal": "Неметалл",
        "post-transition metal": "Постпереходный металл",
        "transition metal": "Переходный металл",
    },
}

LOCALIZED_STANDARD_STATE_TEXTS = {
    "en": {
        "Expected to be a Gas": "Expected to be a gas",
        "Expected to be a Solid": "Expected to be a solid",
        "Gas": "Gas",
        "Liquid": "Liquid",
        "Solid": "Solid",
    },
    "it": {
        "Expected to be a Gas": "Previsto gassoso",
        "Expected to be a Solid": "Previsto solido",
        "Gas": "Gas",
        "Liquid": "Liquido",
        "Solid": "Solido",
    },
    "es": {
        "Expected to be a Gas": "Previsto como gas",
        "Expected to be a Solid": "Previsto como sólido",
        "Gas": "Gas",
        "Liquid": "Líquido",
        "Solid": "Sólido",
    },
    "fr": {
        "Expected to be a Gas": "Présumé gazeux",
        "Expected to be a Solid": "Présumé solide",
        "Gas": "Gaz",
        "Liquid": "Liquide",
        "Solid": "Solide",
    },
    "de": {
        "Expected to be a Gas": "Voraussichtlich gasförmig",
        "Expected to be a Solid": "Voraussichtlich fest",
        "Gas": "Gasförmig",
        "Liquid": "Flüssig",
        "Solid": "Fest",
    },
    "zh": {
        "Expected to be a Gas": "预计为气体",
        "Expected to be a Solid": "预计为固体",
        "Gas": "气体",
        "Liquid": "液体",
        "Solid": "固体",
    },
    "ru": {
        "Expected to be a Gas": "Предположительно газ",
        "Expected to be a Solid": "Предположительно твёрдое",
        "Gas": "Газ",
        "Liquid": "Жидкость",
        "Solid": "Твёрдое",
    },
}

LOCALIZED_MACRO_CLASS_TEXTS = {
    "en": {"Metal": "Metal", "Metalloid": "Metalloid", "Nonmetal": "Nonmetal"},
    "it": {"Metal": "Metallo", "Metalloid": "Semimetallo", "Nonmetal": "Non metallo"},
    "es": {"Metal": "Metal", "Metalloid": "Metaloide", "Nonmetal": "No metal"},
    "fr": {"Metal": "Métal", "Metalloid": "Métalloïde", "Nonmetal": "Non-métal"},
    "de": {"Metal": "Metall", "Metalloid": "Halbmetall", "Nonmetal": "Nichtmetall"},
    "zh": {"Metal": "金属", "Metalloid": "类金属", "Nonmetal": "非金属"},
    "ru": {"Metal": "Металл", "Metalloid": "Металлоид", "Nonmetal": "Неметалл"},
}

RUSSIAN_GENITIVE_EXCEPTIONS = {
    "медь": "меди",
    "ртуть": "ртути",
}


def _normalize_language_code(language_code):
    return language_code or "en"


def _get_localized_lookup_text(lookup, key, language_code, traditional_na="n/a"):
    if not key:
        return traditional_na

    code = _normalize_language_code(language_code)
    localized_map = lookup.get(code, lookup["en"])
    return localized_map.get(key, lookup["en"].get(key, key))


def _first_letter_without_accents(text):
    normalized = unicodedata.normalize("NFKD", text or "")
    for char in normalized:
        if char.isalpha():
            return char.lower()
    return ""


def _needs_french_elision(word):
    return _first_letter_without_accents(word) in {"a", "e", "i", "o", "u", "y", "h"}


def _to_russian_genitive(name):
    word = (name or "").strip()
    if not word:
        return word

    if word in RUSSIAN_GENITIVE_EXCEPTIONS:
        return RUSSIAN_GENITIVE_EXCEPTIONS[word]

    if word.endswith("ий"):
        return f"{word[:-2]}ия"
    if word.endswith("й"):
        return f"{word[:-1]}я"
    if word.endswith("ь"):
        return f"{word[:-1]}и"
    if word.endswith("я"):
        return f"{word[:-1]}и"
    if word.endswith("а"):
        return (
            f"{word[:-1]}и"
            if word[-2:-1] in {"г", "к", "х", "ж", "ч", "ш", "щ", "ц"}
            else f"{word[:-1]}ы"
        )
    if word.endswith("о"):
        return f"{word[:-1]}а"
    return f"{word}а"


def tr(language_code, key, **kwargs):
    code = language_code or "en"
    lang = UI_TEXTS.get(code, UI_TEXTS["en"])
    fallback = UI_TEXTS["en"]
    text = lang.get(key, fallback.get(key, key))
    return text.format(**kwargs) if kwargs else text


def get_all_language_codes():
    return tuple(code for code, _ in ALL_LANGUAGE_OPTIONS)


def get_visible_language_codes():
    return tuple(code for code, _ in LANGUAGE_OPTIONS)


def audit_language_readiness(nomenclature_data, language_code):
    code = language_code or "en"
    ui_texts = UI_TEXTS.get(code, {})
    meta = nomenclature_data.get("meta", {})
    elements = nomenclature_data.get("elements", {})
    common_compounds = nomenclature_data.get("common_compounds", {})
    supported_languages = set(meta.get("supported_languages", []))

    missing_ui_text_keys = sorted(
        key for key in LANGUAGE_READINESS_REQUIRED_TEXT_KEYS if key not in ui_texts
    )
    unverified_name_symbols = sorted(
        symbol
        for symbol, entry in elements.items()
        if code not in entry.get("verified_name_languages", [])
    )
    unverified_anion_symbols = sorted(
        symbol
        for symbol, entry in elements.items()
        if "anion_en" in entry and code not in entry.get("verified_anion_languages", [])
    )
    missing_common_compound_localizations = sorted(
        f"{pair_key}:{compound_entry.get('formula', '?')}"
        for pair_key, entries in common_compounds.items()
        for compound_entry in entries
        if not compound_entry.get(f"name_{code}")
    )

    ready_for_ui = (
        code in supported_languages
        and not missing_ui_text_keys
        and not unverified_name_symbols
        and not unverified_anion_symbols
        and not missing_common_compound_localizations
    )

    return {
        "language_code": code,
        "dataset_supported": code in supported_languages,
        "missing_ui_text_keys": missing_ui_text_keys,
        "unverified_name_symbols": unverified_name_symbols,
        "unverified_anion_symbols": unverified_anion_symbols,
        "missing_common_compound_localizations": missing_common_compound_localizations,
        "ready_for_ui": ready_for_ui,
    }


def get_support_entry(nomenclature_data, symbol):
    return nomenclature_data.get("elements", {}).get(symbol, {})


def get_language_naming_rules(nomenclature_data, language_code=None):
    meta = nomenclature_data.get("meta", {})
    patterns = meta.get("naming_patterns", {})
    fallback_code = meta.get("fallback_language", "en")
    code = language_code or fallback_code
    return patterns.get(code, patterns.get(fallback_code, {}))


def get_localized_support_text(entry, field_prefix, language_code):
    code = language_code or "en"
    localized_field = f"{field_prefix}_{code}"
    fallback_field = f"{field_prefix}_en"
    localized_value = entry.get(localized_field)
    if localized_value:
        return localized_value

    if field_prefix.startswith("traditional_") and code not in {"en", "it"}:
        return None

    return entry.get(fallback_field)


def get_localized_element_name(element, nomenclature_data, language_code):
    entry = get_support_entry(nomenclature_data, element.get("symbol"))
    code = language_code or "en"
    field = f"name_{code}"
    if field in entry:
        return entry[field]
    if "name_en" in entry:
        return entry["name_en"]
    return str(element.get("name", "element"))


def get_localized_anion_name(element, nomenclature_data, language_code):
    entry = get_support_entry(nomenclature_data, element.get("symbol"))
    code = language_code or "en"
    field = f"anion_{code}"
    if field in entry:
        return entry[field]
    return entry.get("anion_en")


def get_localized_category_text(category, language_code, traditional_na="n/a"):
    return _get_localized_lookup_text(
        LOCALIZED_CATEGORY_TEXTS,
        category,
        language_code,
        traditional_na=traditional_na,
    )


def get_localized_standard_state_text(standard_state, language_code, traditional_na="n/a"):
    return _get_localized_lookup_text(
        LOCALIZED_STANDARD_STATE_TEXTS,
        standard_state,
        language_code,
        traditional_na=traditional_na,
    )


def get_localized_macro_class_text(macro_class, language_code, traditional_na="n/a"):
    return _get_localized_lookup_text(
        LOCALIZED_MACRO_CLASS_TEXTS,
        macro_class,
        language_code,
        traditional_na=traditional_na,
    )


def format_stock_compound_name(nomenclature_data, language_code, anion_name, cation_name, roman=None):
    code = _normalize_language_code(language_code)
    if code == "fr":
        connector = "d'" if _needs_french_elision(cation_name) else "de "
        suffix = f" ({roman})" if roman else ""
        return f"{anion_name} {connector}{cation_name}{suffix}"

    if code == "ru":
        cation_name = _to_russian_genitive(cation_name)

    rules = get_language_naming_rules(nomenclature_data, language_code)
    key = "stock_roman" if roman else "stock_simple"
    template = rules.get(key, "{anion} of {cation}" if not roman else "{anion} of {cation} ({roman})")
    return template.format(anion=anion_name, cation=cation_name, roman=roman or "")


def format_traditional_compound_name(nomenclature_data, language_code, anion_name, epithet):
    rules = get_language_naming_rules(nomenclature_data, language_code)
    template = rules.get("traditional", "{anion} {epithet}")
    return template.format(anion=anion_name, epithet=epithet)
