(() => {
  'use strict';

  const DATA_FILES = ['opportunities.json', 'crypto_opportunities.json', 'cyber_opportunities.json', 'catalogue_events.json', 'publication_recommender_events.json'];
  const PAGE_SIZE_EVENTS = 60;
  const PAGE_SIZE_JOURNALS = 36;
  const LOCALES = { fr: 'fr-FR', en: 'en-GB', kab: 'fr-DZ' };
  const CONTINENTS = ['Africa', 'Asia', 'Europe', 'North America', 'South America', 'Oceania', 'Global'];

  const EN = {
    metaTitle: 'CyberResearch Radar — Cyber events worldwide',
    metaDescription: 'Worldwide map of cybersecurity and cryptography conferences, workshops and calls for papers.',
    skip: 'Skip to content', brandSubtitle: 'Global cyber event intelligence', navAria: 'Primary navigation',
    navEvents: 'Events', navJournals: 'Journals', navMethod: 'Method', navScope: 'Scope', navContribute: 'Contribute ↗',
    weeklyRefresh: 'Updated every Monday', languageAria: 'Language',
    heroEyebrow: 'Evidence-led · worldwide · open to the community',
    heroTitle: 'The global map of <em>cybersecurity and cryptography events.</em>',
    heroLead: 'Track conferences, workshops, hands-on events and CFP deadlines across every continent, with separate ranking signals and official-source links.',
    exploreRadar: 'Explore the radar', chooseJournal: 'Choose a journal', readMethod: 'Read the method',
    coreScopeAria: 'Core research topics', expertScope: 'Topics:', nextDeadlinesAria: 'Next verified deadlines',
    deadlineSignal: 'Deadline signal', officialEvidence: 'official evidence', closestFirst: 'closest deadlines',
    coverageAria: 'Portal coverage', statEvents: 'cyber and crypto events', statCountries: 'countries represented',
    statJournals: 'journal records', statRanks: 'traceable ICORE signals', hubAria: 'Research intelligence directory',
    tabEvents: 'Events', tabJournals: 'Journals', eventsTabCount: '{n} conferences & workshops', journalsTabCount: '{n} cyber & crypto titles',
    eventsEyebrow: 'Global event intelligence', eventsTitle: 'Find the right event before its CFP closes.',
    eventsLead: 'Filter worldwide conferences and workshops. Ranking signals remain separate and linked to their original framework.',
    searchLabel: 'Keywords, city or country', searchPlaceholder: 'e.g. post-quantum, PPML, Paris',
    typeLabel: 'Call type', modeLabel: 'Attendance format', rankLabel: 'Venue rank', continentLabel: 'Continent',
    countryLabel: 'Country', deadlineLabel: 'Deadline', sortLabel: 'Sort', verifiedOnly: 'Verified only', resetFilters: 'Reset filters',
    showMore: 'Show more', mapColumnAria: 'Map and selected event', globalMap: 'Global map',
    mapHint: 'Drag, zoom and select a marker.', mapAria: 'Interactive map of research events',
    journalsEyebrow: 'Traceable journal targeting', journalsTitle: 'Compare journals without mixing scope, fees and metrics.',
    journalsLead: 'Records are dated and linked to publisher or bibliometric-index sources.',
    journalSearchLabel: 'Title, publisher or topic', journalSearchPlaceholder: 'e.g. privacy, cryptography, IEEE',
    accessLabel: 'Access model', journalRankLabel: 'Ranking signal', activeOnly: 'Active journals only',
    methodEyebrow: 'No black-box prestige score', methodTitle: 'Academic signals, kept honest.',
    methodLead: 'Conference ranks, journal indexing and bibliometric metrics answer different questions. The radar keeps them separate, dated and sourced.',
    openPolicy: 'Open the editorial policy ↗',
    coreText: 'Primary A*, A, B and C evidence for matching conference series.', conferenceRank: 'Conference ranking ↗',
    ccfText: 'A separate A, B and C perspective, especially useful for international and Asian venues.', ccfSignal: 'Conferences & journals ↗',
    scopusText: 'Source-level indexing and metrics, never converted artificially into CORE ranks.', indexSignal: 'Indexing signal ↗',
    doraText: 'Journal metrics do not replace assessment of an article, researcher or programme.', responsibleUse: 'Responsible use ↗',
    scopeEyebrow: 'Senior-researcher context', scopeTitle: 'Wide enough for discovery. Precise enough for a submission plan.',
    scopeLead: 'The scope covers applied cryptography, cybersecurity, privacy, secure systems, trustworthy AI and digital investigation.',
    scopeCryptoTitle: 'Cryptography & privacy', scopeCryptoText: 'Homomorphic encryption, PQC, secure computation, blockchain and privacy-preserving learning.',
    scopeSystemsTitle: 'Systems & networks', scopeSystemsText: 'IoT/cloud, encrypted traffic, SIEM, Windows/AD, network resilience and critical infrastructure.',
    scopeAiTitle: 'AI & digital investigation', scopeAiText: 'Trustworthy AI, adversarial ML, forensics, incident response and cybercrime.',
    scopeResearchTitle: 'Research & education', scopeResearchText: 'Research schools, grants, doctoral positions, cyber ranges, curricula and security education.',
    communityEyebrow: 'A shared point of entry', communityTitle: 'Help researchers find the call they would otherwise miss.',
    communityText: 'Suggest an event, correct a deadline or add a source. Every change remains visible and reviewable.',
    contributeGithub: 'Contribute on GitHub ↗', footerTagline: 'Worldwide map of cybersecurity and cryptography events.',
    curatedBy: 'Curated by Yulliwas Ameur', loading: 'Loading…', officialFirst: 'official sources first',
    sourceLanguageNote: 'The interface is trilingual; official titles and summaries stay in their source language to preserve accuracy.',
    allTypes: 'All event types', conference: 'Conference', workshop: 'Workshop',
    allModes: 'All formats', onsite: 'In person', online: 'Remote', hybrid: 'Hybrid', multiple: 'Multiple locations', unspecified: 'Not specified',
    allRanks: 'All ranks', unranked: 'Unranked', allContinents: 'All continents', allCountries: 'All countries',
    anyDeadline: 'Any deadline', openDeadlines: 'Open or to be announced', next14: 'Next 14 days', next30: 'Next 30 days', next90: 'Next 90 days', tba: 'To be announced',
    sortClosest: 'Closest deadline', sortEventDate: 'Event date', sortCountry: 'Country', sortTitle: 'Title',
    allAccess: 'All access models', diamond: 'Diamond open access', gold: 'Gold open access', subscription: 'Subscription', other: 'Other / not stated',
    allJournalRanks: 'All ranking signals',
    eventResults: '<strong>{n}</strong> events · <span>{mapped} mapped</span> · <span>{listOnly} list only</span>',
    journalResults: '<strong>{n}</strong> journals', mappedLocations: '{events} events · {locations} locations',
    verified: 'Verified', watchlist: 'Watchlist', needsReview: 'Needs review', closed: 'Closed',
    officialSourceReviewed: 'Official source reviewed', venueUnranked: 'unranked',
    submissionDeadline: 'Submission deadline', deadlineTba: 'Deadline to be announced', closesToday: 'Closes today',
    daysLeft: '{n} days left', oneDayLeft: '1 day left', closedText: 'Closed',
    viewDetails: 'View details', officialCall: 'Official call ↗', officialWebsite: 'Event website ↗', evidence: 'Evidence ↗',
    addCalendar: 'Add deadline to calendar ↓', eventPeriod: 'Event', deadlineWord: 'Deadline', noExactMatch: 'No exact match yet.',
    broadenFilters: 'Broaden a filter or include records awaiting verification.', resetAndShow: 'Reset and show all events',
    noUpcoming: 'No verified future deadline is currently available.', mapUnavailable: 'The map library could not load. The event list remains fully available.',
    noCoordinates: 'No verified coordinates for this selection.', dataErrorTitle: 'The radar data could not be loaded.',
    dataErrorText: 'The automated refresh will retry on the next run. Official source links remain available in the source repository.',
    accessModel: 'Access', apc: 'APC', firstDecision: 'First decision', peerReview: 'Peer review',
    noPublishedFee: 'Not published', noPublishedTimeline: 'Not published', days: '{n} days', active: 'Active', caution: 'Caution',
    authorGuidelines: 'Author guidelines ↗', submit: 'Submission portal ↗', journalWebsite: 'Journal website ↗',
    noJournalMatch: 'No journal matches these filters.', weeklyUpdated: 'Updated {date}', neverUpdated: 'Awaiting first automated refresh',
    countryAfrica: 'Africa', countryAsia: 'Asia', countryEurope: 'Europe', countryNorthAmerica: 'North America',
    countrySouthAmerica: 'South America', countryOceania: 'Oceania', countryGlobal: 'Global',
    navAiSecurity: 'AI security', navShort: 'Short contribution',
    aiEyebrow: 'Matched to your AI-security work', aiTitle: 'Where to publish on AI, LLM & agentic security.',
    aiLead: 'Open special issues and on-theme venues for LLM security, agentic AI, prompt injection and zero-trust for agents. Deadlines checked Aug 2026 — confirm on the official page before submitting.',
    aiAllCfp: 'All IEEE-CS calls for papers ↗', aiWatch: 'On-theme workshops & conferences (short-paper tracks):',
    shortEyebrow: 'Letters & rapid short-paper venues', shortTitle: 'Place a short contribution, fast.',
    shortLead: 'Journals that accept letters and short papers — the quickest route to a citable result, in the same short format as your IEEE Networking Letters paper. Rolling submission.',
    shortRolling: 'Rolling'
  };

  const FR = {
    ...EN,
    metaTitle: 'CyberResearch Radar — Événements cyber dans le monde',
    metaDescription: 'Carte mondiale des conférences, workshops et appels à communications en cybersécurité et cryptographie.',
    skip: 'Aller au contenu', brandSubtitle: 'Veille mondiale des événements cyber', navAria: 'Navigation principale',
    navEvents: 'Événements', navJournals: 'Revues', navMethod: 'Méthode', navScope: 'Périmètre', navContribute: 'Contribuer ↗',
    weeklyRefresh: 'Actualisation chaque lundi', languageAria: 'Langue',
    heroEyebrow: 'Fondé sur les preuves · mondial · ouvert à la communauté',
    heroTitle: 'La carte mondiale des événements de <em>cybersécurité et cryptographie.</em>',
    heroLead: 'Suivez conférences, workshops, ateliers et échéances de CFP sur tous les continents, avec des classements distincts et des liens vers les sources officielles.',
    exploreRadar: 'Explorer le radar', chooseJournal: 'Choisir une revue', readMethod: 'Lire la méthode', coreScopeAria: 'Thématiques principales', expertScope: 'Domaines :',
    nextDeadlinesAria: 'Prochaines échéances vérifiées', deadlineSignal: 'Signal des échéances', officialEvidence: 'preuve officielle', closestFirst: 'échéances proches',
    coverageAria: 'Couverture du portail', statEvents: 'événements cyber et crypto', statCountries: 'pays représentés', statJournals: 'fiches de revues', statRanks: 'signaux ICORE traçables',
    hubAria: 'Répertoire de veille scientifique', tabEvents: 'Événements', tabJournals: 'Revues', eventsTabCount: '{n} conférences et workshops', journalsTabCount: '{n} revues cyber et crypto',
    eventsEyebrow: 'Veille mondiale des événements', eventsTitle: 'Trouvez le bon événement avant la clôture du CFP.',
    eventsLead: 'Filtrez les conférences et workshops mondiaux. Les rangs restent séparés et reliés à leur cadre d’origine.',
    searchLabel: 'Mots-clés, ville ou pays', searchPlaceholder: 'ex. post-quantum, PPML, Paris', typeLabel: 'Type d’appel', modeLabel: 'Format', rankLabel: 'Classement', continentLabel: 'Continent', countryLabel: 'Pays', deadlineLabel: 'Échéance', sortLabel: 'Tri', verifiedOnly: 'Vérifiés uniquement', resetFilters: 'Réinitialiser', showMore: 'Afficher davantage',
    mapColumnAria: 'Carte et détail de l’événement', globalMap: 'Carte mondiale', mapHint: 'Déplacez, zoomez et sélectionnez un marqueur.', mapAria: 'Carte interactive des événements de recherche',
    journalsEyebrow: 'Ciblage éditorial traçable', journalsTitle: 'Comparez les revues sans confondre portée, frais et métriques.',
    journalsLead: 'Les informations sont datées et reliées aux sources de l’éditeur ou des index bibliométriques.', journalSearchLabel: 'Titre, éditeur ou thématique', journalSearchPlaceholder: 'ex. privacy, cryptography, IEEE', accessLabel: 'Modèle d’accès', journalRankLabel: 'Signal de classement', activeOnly: 'Revues actives uniquement',
    methodEyebrow: 'Aucun score de prestige opaque', methodTitle: 'Des signaux académiques maintenus honnêtes.',
    methodLead: 'Classements de conférences, indexation des revues et métriques bibliométriques répondent à des questions différentes. Le radar les conserve séparés, datés et sourcés.', openPolicy: 'Ouvrir la politique éditoriale ↗',
    coreText: 'Preuve principale A*, A, B et C pour les séries de conférences correspondantes.', conferenceRank: 'Classement conférence ↗', ccfText: 'Une perspective A, B et C distincte, utile notamment pour les événements internationaux et asiatiques.', ccfSignal: 'Conférences et revues ↗', scopusText: 'Indexation et métriques au niveau de la source, jamais converties artificiellement en rang CORE.', indexSignal: 'Signal d’indexation ↗', doraText: 'Les métriques d’une revue ne remplacent pas l’évaluation d’un article, d’un chercheur ou d’un programme.', responsibleUse: 'Usage responsable ↗',
    scopeEyebrow: 'Contexte de chercheur senior', scopeTitle: 'Assez large pour découvrir. Assez précis pour préparer une soumission.', scopeLead: 'Le périmètre couvre la cryptographie appliquée, la cybersécurité, la confidentialité, les systèmes sûrs, l’IA digne de confiance et l’investigation numérique.',
    scopeCryptoTitle: 'Cryptographie et confidentialité', scopeCryptoText: 'Chiffrement homomorphe, PQC, calcul sécurisé, blockchain et apprentissage préservant la vie privée.', scopeSystemsTitle: 'Systèmes et réseaux', scopeSystemsText: 'IoT/cloud, trafic chiffré, SIEM, Windows/AD, résilience réseau et infrastructures critiques.', scopeAiTitle: 'IA et investigation numérique', scopeAiText: 'IA digne de confiance, ML adversarial, forensique, réponse à incident et cybercriminalité.', scopeResearchTitle: 'Recherche et formation', scopeResearchText: 'Écoles de recherche, financements, doctorats, cyber ranges, programmes et pédagogie de la sécurité.',
    communityEyebrow: 'Un point d’entrée partagé', communityTitle: 'Aidez les chercheurs à trouver l’appel qu’ils auraient manqué.', communityText: 'Proposez un événement, corrigez une échéance ou ajoutez une source. Chaque changement reste visible et révisable.', contributeGithub: 'Contribuer sur GitHub ↗', footerTagline: 'Carte mondiale des événements de cybersécurité et cryptographie.', curatedBy: 'Sélectionné par Yulliwas Ameur', loading: 'Chargement…', officialFirst: 'sources officielles en priorité', sourceLanguageNote: 'L’interface est trilingue ; les titres et résumés officiels restent dans leur langue source afin de préserver leur exactitude.',
    allTypes: 'Tous les types d’événements', conference: 'Conférence', workshop: 'Workshop / atelier', allModes: 'Tous les formats', onsite: 'Présentiel', online: 'À distance', hybrid: 'Hybride', multiple: 'Plusieurs lieux', unspecified: 'Non précisé', allRanks: 'Tous les rangs', unranked: 'Non classé', allContinents: 'Tous les continents', allCountries: 'Tous les pays', anyDeadline: 'Toutes les échéances', openDeadlines: 'Ouvertes ou à annoncer', next14: '14 prochains jours', next30: '30 prochains jours', next90: '90 prochains jours', tba: 'À annoncer', sortClosest: 'Échéance la plus proche', sortEventDate: 'Date de l’événement', sortCountry: 'Pays', sortTitle: 'Titre',
    allAccess: 'Tous les modèles d’accès', diamond: 'Accès ouvert diamant', gold: 'Accès ouvert gold', subscription: 'Abonnement', other: 'Autre / non précisé', allJournalRanks: 'Tous les signaux de classement',
    eventResults: '<strong>{n}</strong> événements · <span>{mapped} cartographiés</span> · <span>{listOnly} en liste uniquement</span>', journalResults: '<strong>{n}</strong> revues', mappedLocations: '{events} événements · {locations} lieux', verified: 'Vérifié', watchlist: 'Sous surveillance', needsReview: 'À vérifier', closed: 'Clos', officialSourceReviewed: 'Source officielle vérifiée', venueUnranked: 'non classé', submissionDeadline: 'Échéance de soumission', deadlineTba: 'Échéance à annoncer', closesToday: 'Clôture aujourd’hui', daysLeft: '{n} jours restants', oneDayLeft: '1 jour restant', closedText: 'Clos', viewDetails: 'Voir le détail', officialCall: 'Appel officiel ↗', officialWebsite: 'Site de l’événement ↗', evidence: 'Preuve ↗', addCalendar: 'Ajouter au calendrier ↓', eventPeriod: 'Événement', deadlineWord: 'Échéance', noExactMatch: 'Aucune correspondance exacte.', broadenFilters: 'Élargissez un filtre ou incluez les fiches en attente de vérification.', resetAndShow: 'Réinitialiser et tout afficher', noUpcoming: 'Aucune échéance future vérifiée n’est actuellement disponible.', mapUnavailable: 'La bibliothèque cartographique n’a pas pu se charger. La liste des événements reste entièrement disponible.', noCoordinates: 'Aucune coordonnée vérifiée pour cette sélection.', dataErrorTitle: 'Les données du radar n’ont pas pu être chargées.', dataErrorText: 'L’actualisation automatique réessaiera au prochain passage. Les liens officiels restent disponibles dans le dépôt source.',
    accessModel: 'Accès', apc: 'APC', firstDecision: 'Première décision', peerReview: 'Évaluation', noPublishedFee: 'Non publié', noPublishedTimeline: 'Non publié', days: '{n} jours', active: 'Active', caution: 'Prudence', authorGuidelines: 'Instructions aux auteurs ↗', submit: 'Portail de soumission ↗', journalWebsite: 'Site de la revue ↗', noJournalMatch: 'Aucune revue ne correspond à ces filtres.', weeklyUpdated: 'Actualisé le {date}', neverUpdated: 'En attente de la première actualisation automatique',
    countryAfrica: 'Afrique', countryAsia: 'Asie', countryEurope: 'Europe', countryNorthAmerica: 'Amérique du Nord', countrySouthAmerica: 'Amérique du Sud', countryOceania: 'Océanie', countryGlobal: 'Monde',
    navAiSecurity: 'Sécurité IA', navShort: 'Short contribution',
    aiEyebrow: 'Aligné sur vos travaux en sécurité des IA', aiTitle: 'Où publier sur la sécurité des IA, des LLM et des agents.',
    aiLead: 'Numéros spéciaux ouverts et lieux ciblés pour la sécurité des LLM, l’IA agentique, l’injection de prompt et le zero-trust pour agents. Échéances relevées en août 2026 — à confirmer sur la page officielle avant toute soumission.',
    aiAllCfp: 'Tous les appels IEEE-CS ↗', aiWatch: 'Ateliers et conférences dans votre axe (pistes short-paper) :',
    shortEyebrow: 'Letters et revues courtes rapides', shortTitle: 'Publier une contribution courte, vite.',
    shortLead: 'Des revues qui acceptent letters et short papers — la voie la plus rapide vers un résultat citable, dans le même format court que votre IEEE Networking Letters. Soumission au fil de l’eau.',
    shortRolling: 'Au fil de l’eau'
  };

  const KAB = {
    ...EN,
    metaTitle: 'CyberResearch Radar — Tidyanin n tɣellist tumḍint deg umaḍal',
    metaDescription: 'Takarḍa n umaḍal n timliliyin, workshops d yizmaz n usuter deg tɣellist tumḍint d takriptugrafit.',
    skip: 'Ddu ɣer ugbur', brandSubtitle: 'Asefru amaḍlan n tidyanin cyber', navAria: 'Inig agejdan',
    navEvents: 'Tidyanin', navJournals: 'Tisɣunin', navMethod: 'Tarrayt', navScope: 'Taɣult', navContribute: 'Rnu tawsa ↗',
    weeklyRefresh: 'Asnifel yal letnayen', languageAria: 'Tutlayt',
    heroEyebrow: 'S ubeggen · amaḍlan · yeldi i temɣiwent',
    heroTitle: 'Takarḍa n umaḍal n tidyanin n <em>tɣellist tumḍint d takriptugrafit.</em>',
    heroLead: 'Ḍfer timliliyin, workshops, ateliers d yizmaz n CFP deg meṛṛa timura, s yiswiren yemgaraden d yiseɣwan ɣer yiɣbula unṣiben.',
    exploreRadar: 'Wali radar', chooseJournal: 'Fren tasɣunt', readMethod: 'Ɣer tarrayt', coreScopeAria: 'Isental igejdanen', expertScope: 'Isental:',
    nextDeadlinesAria: 'Izmaz iqerben yettwasneqden', deadlineSignal: 'Anamal n yizmaz', officialEvidence: 'abeggen unṣib', closestFirst: 'izmaz iqerben',
    coverageAria: 'Tɣzi n usmel', statEvents: 'tidyanin cyber d crypto', statCountries: 'timura yettwaseknen', statJournals: 'tisɣunin', statRanks: 'inamal ICORE s uɣbalu',
    hubAria: 'Aseknan n unadi ussnan', tabEvents: 'Tidyanin', tabJournals: 'Tisɣunin', eventsTabCount: '{n} timliliyin d workshops', journalsTabCount: '{n} tisɣunin cyber d crypto',
    eventsEyebrow: 'Asefru amaḍlan n tidyanin', eventsTitle: 'Af-d tadyant iwulmen send ad yemdel CFP.', eventsLead: 'Sizdeg timliliyin d workshops n umaḍal. Iswiren qqimen mgaraden u sɛan aɣbalu-nsen.',
    searchLabel: 'Awal, tamdint neɣ tamurt', searchPlaceholder: 'amedya: post-quantum, PPML, Paris', typeLabel: 'Anaw n usuter', modeLabel: 'Askar n timlilit', rankLabel: 'Aswir', continentLabel: 'Agafa n umaḍal', countryLabel: 'Tamurt', deadlineLabel: 'Azemz n taggara', sortLabel: 'Semyiz', verifiedOnly: 'Wid yettwasneqden kan', resetFilters: 'Ales awennez', showMore: 'Sken ugar',
    mapColumnAria: 'Takarḍa d talqayt n tedyant', globalMap: 'Takarḍa n umaḍal', mapHint: 'Smutti, semɣer u fren ticreḍt.', mapAria: 'Takarḍa tamyigawt n tidyanin',
    journalsEyebrow: 'Afran n tesɣunt s uɣbalu', journalsTitle: 'Snemhel tisɣunin war ma tesxelḍeḍ taɣult, lexlaṣ d yizamulen.', journalsLead: 'Talɣut tesɛa azemz u terza ɣer yiɣbula n umeskar neɣ n yisebdaden bibliométriques.', journalSearchLabel: 'Azwel, ameskar neɣ asentel', journalSearchPlaceholder: 'amedya: privacy, cryptography, IEEE', accessLabel: 'Askar n unekcum', journalRankLabel: 'Anamal n uswir', activeOnly: 'Tisɣunin turmidin kan',
    methodEyebrow: 'Ulac asmiḍan uffir n ccan', methodTitle: 'Inamal ussnanen, s tidet.', methodLead: 'Iswiren n timliliyin, indexation n tesɣunin d yizamulen bibliométriques ur d-ttarran ara ɣef yiwen n usteqsi. Radar ibedd-iten mgaraden, s wazemz d uɣbalu.', openPolicy: 'Ldi tasertit taseddasant ↗',
    coreText: 'Abeggen agejdan A*, A, B d C i timliliyin yemṣadan.', conferenceRank: 'Aswir n temlilit ↗', ccfText: 'Tamuɣli-nniḍen A, B d C, tesɛa azal i tidyanin n umaḍal d Asia.', ccfSignal: 'Timliliyin d tesɣunin ↗', scopusText: 'Indexation d yizamulen ɣef uɣbalu, war asenfel ar uswir CORE.', indexSignal: 'Anamal n indexation ↗', doraText: 'Izamulen n tesɣunt ur ttuɣalen ara d asekyed n umagrad, amnadi neɣ ahil.', responsibleUse: 'Aseqdec s leɛqel ↗',
    scopeEyebrow: 'Amnaḍ n umnadi ameqqran', scopeTitle: 'D wessiɛ i tifin. D usdid i uheggi n usuter.', scopeLead: 'Taɣult tesɛa takriptugrafit, taɣellist tumḍint, tabaḍnit, inagrawen imɣuden, AI yettwamanen d usenqed umḍin.',
    scopeCryptoTitle: 'Takriptugrafit d tbaḍnit', scopeCryptoText: 'Homomorphic encryption, PQC, asiḍen aɣelsan, blockchain d ulmad iḥerzen tabaḍnit.', scopeSystemsTitle: 'Inagrawen d yiẓeḍwan', scopeSystemsText: 'IoT/cloud, trafic yettwawgelhen, SIEM, Windows/AD, resilience d tɣessa taxatert.', scopeAiTitle: 'AI d usenqed umḍin', scopeAiText: 'AI yettwamanen, ML adversarial, forensics, tiririt ɣef tedyant d cybercrime.', scopeResearchTitle: 'Anadi d uselmed', scopeResearchText: 'Timusniwin n unadi, tedrimt, doctorat, cyber ranges, ahilen d uselmed n tɣellist.',
    communityEyebrow: 'Anekcum i meṛṛa', communityTitle: 'Ɛiwen imnadiyen ad afen asuter i zemren ad ssutren.', communityText: 'Sumer tadyant, seɣti azemz neɣ rnu aɣbalu. Yal abeddel yeqqim d aban u yezmer ad yettwasekyed.', contributeGithub: 'Rnu tawsa deg GitHub ↗', footerTagline: 'Takarḍa n umaḍal n tidyanin n tɣellist tumḍint d takriptugrafit.', curatedBy: 'Yettwafren sɣur Yulliwas Ameur', loading: 'Asali…', officialFirst: 'iɣbula unṣiben d imezwura', sourceLanguageNote: 'Agrudem s kraḍ n tutlayin; izwal d igzul unṣiben qqimen s tutlayt n uɣbalu iwakken ad qqimen d usdid.',
    allTypes: 'Meṛṛa anawen n tidyanin', conference: 'Tamlilit', workshop: 'Workshop / atelier', allModes: 'Meṛṛa iskaren', onsite: 'Deg umkan', online: 'S internet', hybrid: 'Ameslay', multiple: 'Aṭas n yimukan', unspecified: 'Ur d-yettwasefhem ara', allRanks: 'Meṛṛa iswiren', unranked: 'War aswir', allContinents: 'Meṛṛa igafa n umaḍal', allCountries: 'Meṛṛa timura', anyDeadline: 'Meṛṛa izmaz', openDeadlines: 'Yeldin neɣ mazal', next14: '14 n wussan', next30: '30 n wussan', next90: '90 n wussan', tba: 'Mazal ad d-yili', sortClosest: 'Azemz aqreb', sortEventDate: 'Azemz n tedyant', sortCountry: 'Tamurt', sortTitle: 'Azwel',
    allAccess: 'Meṛṛa iskaren n unekcum', diamond: 'Anekcum ilelli diamond', gold: 'Anekcum ilelli gold', subscription: 'Ajerred', other: 'Wayeḍ / ur d-yettwasefhem', allJournalRanks: 'Meṛṛa inamal n uswir',
    eventResults: '<strong>{n}</strong> tidyanin · <span>{mapped} deg tkarḍa</span> · <span>{listOnly} deg tebdart kan</span>', journalResults: '<strong>{n}</strong> tisɣunin', mappedLocations: '{events} tidyanin · {locations} imukan', verified: 'Yettwasenqed', watchlist: 'Deg uḍfar', needsReview: 'Yesra asenqed', closed: 'Yemdel', officialSourceReviewed: 'Aɣbalu unṣib yettwasenqed', venueUnranked: 'war aswir', submissionDeadline: 'Azemz n taggara n usuter', deadlineTba: 'Azemz mazal', closesToday: 'Ad yemdel ass-a', daysLeft: '{n} n wussan qqimen', oneDayLeft: '1 n wass yeqqim', closedText: 'Yemdel', viewDetails: 'Wali talqayt', officialCall: 'Asuter unṣib ↗', officialWebsite: 'Asmel n tedyant ↗', evidence: 'Abeggen ↗', addCalendar: 'Rnu ɣer uwitay ↓', eventPeriod: 'Tadyant', deadlineWord: 'Azemz', noExactMatch: 'Ulac ayen yemṣadan.', broadenFilters: 'Ssiwseɛ imsizdeg neɣ sekcem wid mazal ur nettwasenqed ara.', resetAndShow: 'Ales u sken meṛṛa', noUpcoming: 'Ulac azemz iqerben yettwasenqed akka tura.', mapUnavailable: 'Takarḍa ur d-tuli ara. Tabdart n tidyanin tezga tettban.', noCoordinates: 'Ulac tisekta yettwasneqden i ufran-a.', dataErrorTitle: 'Isefka n radar ur d-ulin ara.', dataErrorText: 'Asnifel awurman ad yales tikelt-nniḍen. Iseɣwan unṣiben llan deg ukaram n uɣbalu.',
    accessModel: 'Anekcum', apc: 'APC', firstDecision: 'Tiririt tamezwarut', peerReview: 'Asenqed', noPublishedFee: 'Ur d-yettwaseknen', noPublishedTimeline: 'Ur d-yettwaseknen', days: '{n} n wussan', active: 'Turmidt', caution: 'Ɣur-k', authorGuidelines: 'Iwellihen i yimura ↗', submit: 'Anagraw n usuter ↗', journalWebsite: 'Asmel n tesɣunt ↗', noJournalMatch: 'Ulac tasɣunt yemṣadan d yimsizdeg-a.', weeklyUpdated: 'Yettusnifel {date}', neverUpdated: 'Yettṛaǧu asnifel awurman amezwaru',
    countryAfrica: 'Tafriqt', countryAsia: 'Asya', countryEurope: 'Turuft', countryNorthAmerica: 'Marikan n ugafa', countrySouthAmerica: 'Marikan n unẓul', countryOceania: 'Usyanya', countryGlobal: 'Amaḍal',
    navAiSecurity: 'Taɣellist AI', navShort: 'Short contribution',
    aiEyebrow: 'Yeddukel d umahil-ik ɣef tɣellist n AI', aiTitle: 'Anda ara tsuffɣeḍ ɣef tɣellist n AI, LLM d yimyellal.',
    aiLead: 'Iḥricen ispesyalen yeldin d yimukan i tɣellist n LLM, AI tamyellalt, prompt injection d zero-trust i yimyellal. Izmaz ttwasneqden deg ɣuct 2026 — senqed asebter unṣib send tuzzna.',
    aiAllCfp: 'Meṛṛa isutar IEEE-CS ↗', aiWatch: 'Workshops d timliliyin deg wannar-ik (iberdan short-paper) :',
    shortEyebrow: 'Letters d tesɣunin timeẓyanin tirurdanin', shortTitle: 'Suffeɣ tawsa tawezzlant, s tɣawla.',
    shortLead: 'Tisɣunin i yeqbelen letters d short papers — abrid arurad ɣer ugmuḍ yezmren ad yettwabdar, s wemasal awezzlan am IEEE Networking Letters-ik. Tuzzna s ttawil.',
    shortRolling: 'S ttawil'
  };

  const I18N = { fr: FR, en: EN, kab: KAB };
  const state = {
    lang: 'fr', view: 'events', events: [], journals: [], manifest: null,
    eventLimit: PAGE_SIZE_EVENTS, journalLimit: PAGE_SIZE_JOURNALS,
    selectedEventId: null,
    eventFilters: { q: '', type: 'all', mode: 'all', rank: 'all', continent: 'all', country: 'all', deadline: 'open', sort: 'deadline', verified: false },
    journalFilters: { q: '', access: 'all', rank: 'all', active: true },
    map: null, markerLayer: null, markerIndex: new Map()
  };

  const byId = (id) => document.getElementById(id);
  const tr = (key, vars = {}) => {
    let value = (I18N[state.lang] && I18N[state.lang][key]) || EN[key] || key;
    Object.entries(vars).forEach(([name, replacement]) => { value = value.replaceAll(`{${name}}`, String(replacement)); });
    return value;
  };
  const escapeHtml = (value) => String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
  const safeUrl = (value) => {
    try {
      const url = new URL(String(value || ''), window.location.href);
      return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
    } catch { return ''; }
  };
  const normalizeText = (value) => String(value ?? '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const todayUtc = () => {
    const now = new Date();
    return Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
  };
  const dayValue = (value) => {
    if (!value) return Number.POSITIVE_INFINITY;
    const parsed = Date.parse(`${String(value).slice(0, 10)}T00:00:00Z`);
    return Number.isFinite(parsed) ? parsed : Number.POSITIVE_INFINITY;
  };
  const daysUntil = (value) => value ? Math.round((dayValue(value) - todayUtc()) / 86400000) : null;
  const formatDate = (value, short = false) => {
    if (!value) return tr('tba');
    try {
      return new Intl.DateTimeFormat(LOCALES[state.lang], short
        ? { day: '2-digit', month: 'short', timeZone: 'UTC' }
        : { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' })
        .format(new Date(`${String(value).slice(0, 10)}T00:00:00Z`));
    } catch { return String(value).slice(0, 10); }
  };
  const formatNumber = (value) => new Intl.NumberFormat(LOCALES[state.lang]).format(Number(value || 0));
  const continentText = (value) => ({
    Africa: tr('countryAfrica'), Asia: tr('countryAsia'), Europe: tr('countryEurope'),
    'North America': tr('countryNorthAmerica'), 'South America': tr('countrySouthAmerica'),
    Oceania: tr('countryOceania'), Global: tr('countryGlobal')
  }[value] || value || tr('countryGlobal'));
  const typeText = (value) => tr(value === 'workshop' ? 'workshop' : 'conference');
  const modeText = (value) => tr(['onsite', 'online', 'hybrid', 'multiple', 'unspecified'].includes(value) ? value : 'unspecified');
  const statusText = (value) => tr(({ verified: 'verified', watchlist: 'watchlist', 'needs-review': 'needsReview', closed: 'closed' })[value] || 'needsReview');
  const locationText = (item) => [item.city, item.country].filter(Boolean).join(', ') || continentText(item.continent);
  const primaryRank = (item) => Array.isArray(item.rankings) && item.rankings.length ? item.rankings[0] : null;

  function getInitialLanguage() {
    const query = new URLSearchParams(window.location.search).get('lang');
    if (['fr', 'en', 'kab'].includes(query)) return query;
    try {
      const saved = localStorage.getItem('cyberresearchradar-language');
      if (['fr', 'en', 'kab'].includes(saved)) return saved;
    } catch { /* storage may be blocked */ }
    const browser = String(navigator.language || '').toLowerCase();
    if (browser.startsWith('kab')) return 'kab';
    if (browser.startsWith('en')) return 'en';
    return 'fr';
  }

  function setLanguage(lang, updateUrl = true) {
    state.lang = ['fr', 'en', 'kab'].includes(lang) ? lang : 'fr';
    document.documentElement.lang = state.lang;
    document.title = tr('metaTitle');
    const meta = document.querySelector('meta[name="description"]');
    if (meta) meta.setAttribute('content', tr('metaDescription'));
    document.querySelectorAll('[data-i18n]').forEach((node) => { node.textContent = tr(node.dataset.i18n); });
    document.querySelectorAll('[data-i18n-html]').forEach((node) => { node.innerHTML = tr(node.dataset.i18nHtml); });
    document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => { node.setAttribute('placeholder', tr(node.dataset.i18nPlaceholder)); });
    document.querySelectorAll('[data-i18n-aria]').forEach((node) => { node.setAttribute('aria-label', tr(node.dataset.i18nAria)); });
    document.querySelectorAll('[data-lang]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.lang === state.lang)));
    try { localStorage.setItem('cyberresearchradar-language', state.lang); } catch { /* storage may be blocked */ }
    if (updateUrl) {
      const url = new URL(window.location.href);
      url.searchParams.set('lang', state.lang);
      history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`);
    }
    populateEventSelects();
    populateJournalSelects();
    renderAll();
  }

  function option(value, label, selected) {
    return `<option value="${escapeHtml(value)}"${value === selected ? ' selected' : ''}>${escapeHtml(label)}</option>`;
  }

  function populateEventSelects() {
    if (!byId('event-type')) return;
    const f = state.eventFilters;
    byId('event-type').innerHTML = [option('all', tr('allTypes'), f.type), option('conference', tr('conference'), f.type), option('workshop', tr('workshop'), f.type)].join('');
    byId('event-mode').innerHTML = ['all', 'hybrid', 'online', 'onsite', 'multiple', 'unspecified'].map((value) => option(value, value === 'all' ? tr('allModes') : tr(value), f.mode)).join('');
    byId('event-rank').innerHTML = [option('all', tr('allRanks'), f.rank), ...['A*', 'A', 'B', 'C', 'Q1', 'Q2', 'Q3', 'Q4'].map((value) => option(value, value, f.rank)), option('unranked', tr('unranked'), f.rank)].join('');
    byId('event-continent').innerHTML = [option('all', tr('allContinents'), f.continent), ...CONTINENTS.map((value) => option(value, continentText(value), f.continent))].join('');
    const countries = [...new Set(state.events.filter((item) => f.continent === 'all' || item.continent === f.continent).map((item) => item.country).filter(Boolean))].sort((a, b) => a.localeCompare(b, LOCALES[state.lang]));
    if (f.country !== 'all' && !countries.includes(f.country)) f.country = 'all';
    byId('event-country').innerHTML = [option('all', tr('allCountries'), f.country), ...countries.map((value) => option(value, value, f.country))].join('');
    byId('event-deadline').innerHTML = [
      option('open', tr('openDeadlines'), f.deadline), option('14', tr('next14'), f.deadline), option('30', tr('next30'), f.deadline),
      option('90', tr('next90'), f.deadline), option('tba', tr('tba'), f.deadline), option('all', tr('anyDeadline'), f.deadline)
    ].join('');
    byId('event-sort').innerHTML = [option('deadline', tr('sortClosest'), f.sort), option('event', tr('sortEventDate'), f.sort), option('country', tr('sortCountry'), f.sort), option('title', tr('sortTitle'), f.sort)].join('');
    byId('event-query').value = f.q;
    byId('event-verified').checked = f.verified;
  }

  function populateJournalSelects() {
    if (!byId('journal-access')) return;
    const f = state.journalFilters;
    byId('journal-access').innerHTML = ['all', 'diamond', 'gold', 'hybrid', 'subscription', 'other'].map((value) => option(value, value === 'all' ? tr('allAccess') : tr(value), f.access)).join('');
    byId('journal-rank').innerHTML = [option('all', tr('allJournalRanks'), f.rank), ...['Q1', 'Q2', 'Q3', 'Q4', 'A', 'B', 'C', 'Indexed'].map((value) => option(value, value, f.rank))].join('');
    byId('journal-query').value = f.q;
    byId('journal-active').checked = f.active;
  }

  function eventScore(item) {
    return (item.status === 'verified' ? 5 : 0) + (item.deadline ? 3 : 0) + (item.latitude != null && item.longitude != null ? 2 : 0) + (Array.isArray(item.rankings) ? item.rankings.length : 0) + (item.summary ? 1 : 0);
  }

  function mergeEvents(left, right) {
    const primary = eventScore(right) >= eventScore(left) ? right : left;
    const secondary = primary === right ? left : right;
    const rankingKey = (entry) => `${entry.framework}|${entry.rank}|${entry.edition}|${entry.sourceUrl}`;
    const rankings = [...(secondary.rankings || []), ...(primary.rankings || [])];
    return {
      ...secondary, ...primary,
      topics: [...new Set([...(secondary.topics || []), ...(primary.topics || [])])],
      rankings: [...new Map(rankings.map((entry) => [rankingKey(entry), entry])).values()],
      indexedIn: [...new Set([...(secondary.indexedIn || []), ...(primary.indexedIn || [])])]
    };
  }

  function normalizeEvents(datasets) {
    const unique = new Map();
    datasets.flat().forEach((raw) => {
      if (!raw || typeof raw !== 'object' || !raw.id || !raw.title || !['conference', 'workshop'].includes(raw.type)) return;
      const item = {
        ...raw,
        id: String(raw.id), title: String(raw.title), acronym: raw.acronym ? String(raw.acronym) : null,
        summary: String(raw.summary || ''), topics: Array.isArray(raw.topics) ? raw.topics.map(String) : [],
        country: String(raw.country || ''), continent: CONTINENTS.includes(raw.continent) ? raw.continent : 'Global',
        mode: ['onsite', 'hybrid', 'online', 'multiple', 'unspecified'].includes(raw.mode) ? raw.mode : 'unspecified',
        rankings: Array.isArray(raw.rankings) ? raw.rankings : [], status: ['verified', 'watchlist', 'needs-review', 'closed'].includes(raw.status) ? raw.status : 'needs-review'
      };
      unique.set(item.id, unique.has(item.id) ? mergeEvents(unique.get(item.id), item) : item);
    });
    return [...unique.values()];
  }

  function normalizeJournals(dataset) {
    const unique = new Map();
    (Array.isArray(dataset) ? dataset : []).forEach((raw) => {
      if (!raw || typeof raw !== 'object' || !raw.id || !raw.title || !raw.officialUrl) return;
      const item = {
        ...raw, id: String(raw.id), title: String(raw.title), publisher: String(raw.publisher || ''), summary: String(raw.summary || ''),
        topics: Array.isArray(raw.topics) ? raw.topics.map(String) : [], rankings: Array.isArray(raw.rankings) ? raw.rankings : [],
        accessModel: ['diamond', 'gold', 'hybrid', 'subscription', 'other'].includes(raw.accessModel) ? raw.accessModel : 'other',
        status: raw.status === 'caution' ? 'caution' : 'active'
      };
      unique.set(item.id, item);
    });
    return [...unique.values()];
  }

  function eventMatches(item) {
    const f = state.eventFilters;
    const needle = normalizeText(f.q.trim());
    const haystack = normalizeText([item.title, item.acronym, item.summary, item.city, item.country, item.continent, ...(item.topics || [])].filter(Boolean).join(' '));
    if (needle && !haystack.includes(needle)) return false;
    if (f.type !== 'all' && item.type !== f.type) return false;
    if (f.mode !== 'all' && item.mode !== f.mode) return false;
    if (f.rank !== 'all') {
      if (f.rank === 'unranked' && (item.rankings || []).length) return false;
      if (f.rank !== 'unranked' && !(item.rankings || []).some((entry) => entry.rank === f.rank)) return false;
    }
    if (f.continent !== 'all' && item.continent !== f.continent) return false;
    if (f.country !== 'all' && item.country !== f.country) return false;
    if (f.verified && item.status !== 'verified') return false;
    const deadline = dayValue(item.deadline);
    if (f.deadline === 'tba' && item.deadline) return false;
    if (f.deadline === 'open' && item.deadline && deadline < todayUtc()) return false;
    if (['14', '30', '90'].includes(f.deadline)) {
      const delta = deadline - todayUtc();
      if (!item.deadline || delta < 0 || delta > Number(f.deadline) * 86400000) return false;
    }
    return true;
  }

  function filteredEvents() {
    const items = state.events.filter(eventMatches);
    return items.sort((a, b) => {
      if (state.eventFilters.sort === 'deadline') return dayValue(a.deadline) - dayValue(b.deadline) || a.title.localeCompare(b.title, LOCALES[state.lang]);
      if (state.eventFilters.sort === 'event') return dayValue(a.eventStart) - dayValue(b.eventStart) || a.title.localeCompare(b.title, LOCALES[state.lang]);
      if (state.eventFilters.sort === 'country') return String(a.country).localeCompare(String(b.country), LOCALES[state.lang]) || a.title.localeCompare(b.title, LOCALES[state.lang]);
      return a.title.localeCompare(b.title, LOCALES[state.lang]);
    });
  }

  function deadlineMarkup(item) {
    const remaining = daysUntil(item.deadline);
    const relative = remaining === null ? tr('deadlineTba') : remaining < 0 ? tr('closedText') : remaining === 0 ? tr('closesToday') : remaining === 1 ? tr('oneDayLeft') : tr('daysLeft', { n: remaining });
    return `<div class="deadline-block"><small>${escapeHtml(item.deadlineLabel || tr('submissionDeadline'))}</small><strong>${escapeHtml(item.deadline ? formatDate(item.deadline) : tr('tba'))}</strong>${item.deadlineTimezone ? `<span>${escapeHtml(item.deadlineTimezone)}</span>` : ''}<span>${escapeHtml(relative)}</span></div>`;
  }

  function eventCard(item, selected) {
    const rank = primaryRank(item);
    const rankUrl = rank ? safeUrl(rank.sourceUrl) : '';
    const rankHtml = rank
      ? `<a class="rank-badge" href="${escapeHtml(rankUrl || '#')}"${rankUrl ? ' target="_blank" rel="noreferrer"' : ''}><span>${escapeHtml(rank.rank)}</span><small>${escapeHtml(rank.framework)}</small></a>`
      : `<span class="rank-badge rank-none"><span>N/R</span><small>${escapeHtml(tr('venueUnranked'))}</small></span>`;
    const callUrl = safeUrl(item.cfpUrl || item.officialUrl);
    return `<article class="opportunity-card${selected ? ' selected' : ''}" data-event-card="${escapeHtml(item.id)}">
      <div class="card-topline"><span class="type-label type-${escapeHtml(item.type)}">${escapeHtml(typeText(item.type))}</span><span class="status-label status-${escapeHtml(item.status)}">${escapeHtml(statusText(item.status))}</span></div>
      <div class="card-title-row"><div><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml([item.acronym, locationText(item), modeText(item.mode)].filter(Boolean).join(' · '))}</p></div>${rankHtml}</div>
      <p class="card-summary">${escapeHtml(item.summary || '')}</p>
      <div class="topic-row">${(item.topics || []).slice(0, 5).map((topic) => `<span>${escapeHtml(topic)}</span>`).join('')}</div>
      <div class="card-bottom">${deadlineMarkup(item)}<div class="card-actions"><button type="button" data-action="select-event" data-id="${escapeHtml(item.id)}">${escapeHtml(tr('viewDetails'))}</button>${callUrl ? `<a href="${escapeHtml(callUrl)}" target="_blank" rel="noreferrer">${escapeHtml(tr('officialCall'))}</a>` : ''}</div></div>
    </article>`;
  }

  function calendarHref(item) {
    if (!item.deadline) return '';
    const date = String(item.deadline).slice(0, 10).replaceAll('-', '');
    const title = String(item.title).replace(/[\r\n,;]/g, ' ');
    const url = safeUrl(item.cfpUrl || item.officialUrl);
    const calendar = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//CyberResearch Radar//EN', 'BEGIN:VEVENT', `UID:${item.id}@cyberresearchradar`, `DTSTART;VALUE=DATE:${date}`, `SUMMARY:${tr('submissionDeadline')} — ${title}`, `URL:${url}`, `DESCRIPTION:${tr('deadlineWord')}: ${item.deadlineTimezone || 'UTC / not stated'}`, 'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
    return `data:text/calendar;charset=utf-8,${encodeURIComponent(calendar)}`;
  }

  function renderEventDetail(items) {
    const host = byId('event-detail');
    if (!host) return;
    const item = items.find((entry) => entry.id === state.selectedEventId) || items[0];
    if (!item) {
      state.selectedEventId = null;
      host.innerHTML = `<div class="empty-state"><strong>${escapeHtml(tr('noExactMatch'))}</strong><p>${escapeHtml(tr('broadenFilters'))}</p></div>`;
      return;
    }
    state.selectedEventId = item.id;
    const official = safeUrl(item.officialUrl);
    const evidenceUrl = safeUrl(item.evidenceUrl);
    const cal = calendarHref(item);
    host.innerHTML = `<div class="map-detail-heading"><span>${escapeHtml(typeText(item.type))}</span><strong>${escapeHtml(item.acronym || item.title)}</strong></div>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(locationText(item))} · ${escapeHtml(modeText(item.mode))}</p>
      <p>${escapeHtml(item.summary || '')}</p>
      <div class="map-detail-topics">${(item.topics || []).slice(0, 4).map((topic) => `<span>${escapeHtml(topic)}</span>`).join('')}</div>
      <p class="map-deadline"><strong>${escapeHtml(tr('deadlineWord'))}:</strong> ${escapeHtml(item.deadline ? formatDate(item.deadline) : tr('deadlineTba'))}${item.deadlineTimezone ? ` · ${escapeHtml(item.deadlineTimezone)}` : ''}</p>
      ${item.eventStart ? `<p><strong>${escapeHtml(tr('eventPeriod'))}:</strong> ${escapeHtml(formatDate(item.eventStart))}${item.eventEnd ? ` — ${escapeHtml(formatDate(item.eventEnd))}` : ''}</p>` : ''}
      <div class="detail-links">${official ? `<a href="${escapeHtml(official)}" target="_blank" rel="noreferrer">${escapeHtml(tr('officialWebsite'))}</a>` : ''}${evidenceUrl ? `<a href="${escapeHtml(evidenceUrl)}" target="_blank" rel="noreferrer">${escapeHtml(tr('evidence'))}</a>` : ''}${cal ? `<a href="${cal}" download="${escapeHtml(item.id)}-deadline.ics">${escapeHtml(tr('addCalendar'))}</a>` : ''}</div>`;
  }

  function ensureMap() {
    const host = byId('research-map');
    if (!host || state.map) return Boolean(state.map);
    if (!window.L) {
      host.innerHTML = `<div class="map-placeholder">${escapeHtml(tr('mapUnavailable'))}</div>`;
      return false;
    }
    state.map = window.L.map(host, { minZoom: 1, worldCopyJump: true, scrollWheelZoom: false }).setView([23, 8], 2);
    window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '&copy; OpenStreetMap contributors' }).addTo(state.map);
    state.markerLayer = window.L.layerGroup().addTo(state.map);
    return true;
  }

  function renderMap(items) {
    const mapped = items.filter((item) => Number.isFinite(Number(item.latitude)) && Number.isFinite(Number(item.longitude)));
    byId('map-count').textContent = tr('mappedLocations', { events: formatNumber(mapped.length), locations: formatNumber(new Set(mapped.map((item) => `${Number(item.latitude).toFixed(4)},${Number(item.longitude).toFixed(4)}`)).size) });
    if (!ensureMap()) return;
    state.markerLayer.clearLayers();
    state.markerIndex = new Map();
    const groups = new Map();
    mapped.forEach((item) => {
      const key = `${Number(item.latitude).toFixed(5)},${Number(item.longitude).toFixed(5)}`;
      groups.set(key, [...(groups.get(key) || []), item]);
    });
    const bounds = [];
    groups.forEach((group) => {
      const lead = group[0];
      const selected = group.some((item) => item.id === state.selectedEventId);
      const markerClass = `map-marker ${lead.type === 'workshop' ? 'workshop' : ''} ${group.length > 1 ? 'stack' : ''} ${selected ? 'is-selected' : ''}`;
      const label = group.length > 1 ? String(group.length) : (lead.type === 'workshop' ? 'WKSP' : 'CONF');
      const icon = window.L.divIcon({ className: '', html: `<span class="${markerClass}">${escapeHtml(label)}</span>`, iconSize: [50, 50], iconAnchor: [25, 25] });
      const marker = window.L.marker([Number(lead.latitude), Number(lead.longitude)], { icon, title: group.length > 1 ? `${group.length} · ${locationText(lead)}` : lead.title });
      const tooltip = `<strong>${escapeHtml(group.length > 1 ? `${group.length} · ${locationText(lead)}` : (lead.acronym || lead.title))}</strong><br><small>${escapeHtml(group.slice(0, 3).map((item) => `${item.acronym || item.title}: ${item.deadline ? formatDate(item.deadline, true) : tr('tba')}`).join(' · '))}</small>`;
      marker.bindTooltip(tooltip, { direction: 'top', offset: [0, -18] });
      marker.on('click', () => {
        const selectedItem = group.find((item) => item.id === state.selectedEventId) || group[0];
        state.selectedEventId = selectedItem.id;
        renderEvents(false);
        if (window.matchMedia('(max-width: 920px)').matches) byId('event-detail').scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      marker.addTo(state.markerLayer);
      group.forEach((item) => state.markerIndex.set(item.id, marker));
      bounds.push([Number(lead.latitude), Number(lead.longitude)]);
    });
    state.map.invalidateSize({ pan: false });
    if (bounds.length === 0) state.map.setView([23, 8], 2);
    else if (bounds.length === 1) state.map.setView(bounds[0], 4);
    else state.map.fitBounds(bounds, { padding: [45, 45], maxZoom: 5 });
  }

  function renderNextCalls() {
    const host = byId('next-calls');
    if (!host) return;
    const upcoming = state.events.filter((item) => item.status === 'verified' && item.deadline && dayValue(item.deadline) >= todayUtc()).sort((a, b) => dayValue(a.deadline) - dayValue(b.deadline)).slice(0, 4);
    host.innerHTML = upcoming.length ? upcoming.map((item, index) => {
      const url = safeUrl(item.cfpUrl || item.officialUrl);
      return `<a href="${escapeHtml(url || '#')}"${url ? ' target="_blank" rel="noreferrer"' : ''}><span>${String(index + 1).padStart(2, '0')}</span><div><strong>${escapeHtml(item.acronym || item.title)}</strong><small>${escapeHtml((item.topics || []).slice(0, 2).join(' · '))}</small></div><time datetime="${escapeHtml(item.deadline)}">${escapeHtml(formatDate(item.deadline, true))}</time></a>`;
    }).join('') : `<div class="empty-state"><p>${escapeHtml(tr('noUpcoming'))}</p></div>`;
  }

  function renderEvents(rebuildMap = true) {
    if (!byId('event-list')) return;
    const items = filteredEvents();
    if (state.selectedEventId && !items.some((item) => item.id === state.selectedEventId)) state.selectedEventId = items[0]?.id || null;
    if (!state.selectedEventId && items.length) state.selectedEventId = items[0].id;
    const shown = items.slice(0, state.eventLimit);
    byId('event-list').innerHTML = shown.length ? shown.map((item) => eventCard(item, item.id === state.selectedEventId)).join('') : `<div class="empty-state"><strong>${escapeHtml(tr('noExactMatch'))}</strong><p>${escapeHtml(tr('broadenFilters'))}</p><button type="button" data-action="reset-events">${escapeHtml(tr('resetAndShow'))}</button></div>`;
    const mapped = items.filter((item) => Number.isFinite(Number(item.latitude)) && Number.isFinite(Number(item.longitude))).length;
    byId('event-result-copy').innerHTML = tr('eventResults', { n: formatNumber(items.length), mapped: formatNumber(mapped), listOnly: formatNumber(items.length - mapped) });
    byId('show-more-events').hidden = shown.length >= items.length;
    renderEventDetail(items);
    if (rebuildMap) renderMap(items);
  }

  function journalMatches(item) {
    const f = state.journalFilters;
    const needle = normalizeText(f.q.trim());
    const haystack = normalizeText([item.title, item.acronym, item.publisher, item.summary, item.scope, ...(item.topics || []), ...(item.indexing || [])].filter(Boolean).join(' '));
    if (needle && !haystack.includes(needle)) return false;
    if (f.access !== 'all' && item.accessModel !== f.access) return false;
    if (f.rank !== 'all' && !(item.rankings || []).some((entry) => entry.rank === f.rank)) return false;
    if (f.active && item.status !== 'active') return false;
    return true;
  }

  function formatMoney(charge) {
    if (!charge || charge.amount == null) return charge?.label || tr('noPublishedFee');
    try { return new Intl.NumberFormat(LOCALES[state.lang], { style: 'currency', currency: charge.currency || 'EUR', maximumFractionDigits: 0 }).format(charge.amount); }
    catch { return `${formatNumber(charge.amount)} ${charge.currency || ''}`.trim(); }
  }

  function journalCard(item) {
    const official = safeUrl(item.officialUrl);
    const guidelines = safeUrl(item.authorGuidelinesUrl);
    const submit = safeUrl(item.submissionUrl);
    const rankingHtml = (item.rankings || []).slice(0, 5).map((entry) => {
      const url = safeUrl(entry.sourceUrl);
      return `<a href="${escapeHtml(url || '#')}"${url ? ' target="_blank" rel="noreferrer"' : ''}>${escapeHtml(`${entry.framework} ${entry.rank}`)}</a>`;
    }).join('');
    const firstDecision = item.timeline && item.timeline.firstDecisionDays != null ? tr('days', { n: formatNumber(item.timeline.firstDecisionDays) }) : tr('noPublishedTimeline');
    return `<article class="journal-card">
      <div class="card-topline"><span class="access-label">${escapeHtml(tr(item.accessModel || 'other'))}</span><span class="${item.status === 'caution' ? 'caution-label' : 'status-label status-verified'}">${escapeHtml(tr(item.status === 'caution' ? 'caution' : 'active'))}</span></div>
      <h3>${escapeHtml(item.title)}</h3><p class="publisher">${escapeHtml([item.acronym, item.publisher].filter(Boolean).join(' · '))}</p>
      <p class="journal-summary">${escapeHtml(item.summary || item.scope || '')}</p>
      <div class="topic-row">${(item.topics || []).slice(0, 5).map((topic) => `<span>${escapeHtml(topic)}</span>`).join('')}</div>
      <div class="journal-signals"><div><small>${escapeHtml(tr('accessModel'))}</small><strong>${escapeHtml(tr(item.accessModel || 'other'))}</strong></div><div><small>${escapeHtml(tr('apc'))}</small><strong>${escapeHtml(formatMoney(item.apc))}</strong></div><div><small>${escapeHtml(tr('firstDecision'))}</small><strong>${escapeHtml(firstDecision)}</strong></div></div>
      <div class="journal-ranks">${rankingHtml}</div>
      <div class="journal-links">${official ? `<a href="${escapeHtml(official)}" target="_blank" rel="noreferrer">${escapeHtml(tr('journalWebsite'))}</a>` : ''}${guidelines ? `<a href="${escapeHtml(guidelines)}" target="_blank" rel="noreferrer">${escapeHtml(tr('authorGuidelines'))}</a>` : ''}${submit ? `<a href="${escapeHtml(submit)}" target="_blank" rel="noreferrer">${escapeHtml(tr('submit'))}</a>` : ''}</div>
    </article>`;
  }

  function renderJournals() {
    if (!byId('journal-list')) return;
    const items = state.journals.filter(journalMatches).sort((a, b) => a.title.localeCompare(b.title, LOCALES[state.lang]));
    const shown = items.slice(0, state.journalLimit);
    byId('journal-list').innerHTML = shown.length ? shown.map(journalCard).join('') : `<div class="empty-state"><strong>${escapeHtml(tr('noJournalMatch'))}</strong></div>`;
    byId('journal-result-copy').innerHTML = tr('journalResults', { n: formatNumber(items.length) });
    byId('show-more-journals').hidden = shown.length >= items.length;
  }

  function renderStats() {
    byId('stat-events').textContent = formatNumber(state.events.length);
    byId('stat-countries').textContent = formatNumber(new Set(state.events.map((item) => item.country).filter(Boolean)).size);
    byId('stat-journals').textContent = formatNumber(state.journals.length);
    byId('events-tab-count').textContent = tr('eventsTabCount', { n: formatNumber(state.events.length) });
    byId('journals-tab-count').textContent = tr('journalsTabCount', { n: formatNumber(state.journals.length) });
    const generatedAt = state.manifest && state.manifest.generatedAt;
    byId('last-refresh').textContent = generatedAt ? tr('weeklyUpdated', { date: new Intl.DateTimeFormat(LOCALES[state.lang], { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(generatedAt)) }) : tr('neverUpdated');
  }

  function renderAll() {
    if (!byId('event-list')) return;
    renderStats(); renderNextCalls(); renderEvents(); renderJournals();
  }

  function activateView(view, updateHash = true) {
    state.view = view === 'journals' ? 'journals' : 'events';
    const eventsActive = state.view === 'events';
    byId('events-tab').setAttribute('aria-selected', String(eventsActive));
    byId('events-tab').tabIndex = eventsActive ? 0 : -1;
    byId('journals-tab').setAttribute('aria-selected', String(!eventsActive));
    byId('journals-tab').tabIndex = eventsActive ? -1 : 0;
    byId('events-panel').hidden = !eventsActive;
    byId('journals-panel').hidden = eventsActive;
    if (updateHash) history.replaceState(null, '', `${window.location.pathname}${window.location.search}${eventsActive ? '#events' : '#journals'}`);
    if (eventsActive && state.map) window.setTimeout(() => state.map.invalidateSize({ pan: false }), 0);
  }

  async function fetchJson(path) {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
    return response.json();
  }

  async function loadData() {
    byId('event-list').innerHTML = '<div class="opportunity-card loading-card"></div><div class="opportunity-card loading-card"></div>';
    byId('journal-list').innerHTML = '<div class="journal-card loading-card"></div><div class="journal-card loading-card"></div>';
    try {
      const eventResults = await Promise.allSettled(DATA_FILES.map((file) => fetchJson(`./data/${file}`)));
      const datasets = eventResults.filter((result) => result.status === 'fulfilled' && Array.isArray(result.value)).map((result) => result.value);
      if (!datasets.length) throw new Error('No event dataset loaded');
      const [journalsResult, manifestResult] = await Promise.allSettled([fetchJson('./data/journals.json'), fetchJson('./data/manifest.json')]);
      state.events = normalizeEvents(datasets);
      state.journals = journalsResult.status === 'fulfilled' ? normalizeJournals(journalsResult.value) : [];
      state.manifest = manifestResult.status === 'fulfilled' ? manifestResult.value : null;
      if (!state.events.length) throw new Error('No valid conference or workshop record');
      populateEventSelects(); populateJournalSelects(); renderAll();
    } catch (error) {
      console.error(error);
      const message = `<div class="error-state"><strong>${escapeHtml(tr('dataErrorTitle'))}</strong><p>${escapeHtml(tr('dataErrorText'))}</p></div>`;
      byId('event-list').innerHTML = message;
      byId('journal-list').innerHTML = message;
      byId('event-result-copy').textContent = '—';
      byId('journal-result-copy').textContent = '—';
    }
  }

  function bindControls() {
    document.querySelectorAll('[data-lang]').forEach((button) => button.addEventListener('click', () => setLanguage(button.dataset.lang)));
    document.querySelectorAll('[data-view]').forEach((button) => button.addEventListener('click', () => activateView(button.dataset.view)));
    byId('events-tab').addEventListener('keydown', tabKeyHandler);
    byId('journals-tab').addEventListener('keydown', tabKeyHandler);
    const eventBindings = {
      'event-query': ['q', 'input'], 'event-type': ['type', 'change'], 'event-mode': ['mode', 'change'], 'event-rank': ['rank', 'change'],
      'event-country': ['country', 'change'], 'event-deadline': ['deadline', 'change'], 'event-sort': ['sort', 'change']
    };
    Object.entries(eventBindings).forEach(([id, [key, eventName]]) => byId(id).addEventListener(eventName, (event) => {
      state.eventFilters[key] = event.target.value; state.eventLimit = PAGE_SIZE_EVENTS; renderEvents();
    }));
    byId('event-continent').addEventListener('change', (event) => {
      state.eventFilters.continent = event.target.value; state.eventFilters.country = 'all'; state.eventLimit = PAGE_SIZE_EVENTS; populateEventSelects(); renderEvents();
    });
    byId('event-verified').addEventListener('change', (event) => { state.eventFilters.verified = event.target.checked; state.eventLimit = PAGE_SIZE_EVENTS; renderEvents(); });
    byId('reset-events').addEventListener('click', resetEvents);
    byId('event-list').addEventListener('click', (event) => {
      const target = event.target.closest('[data-action]');
      if (!target) return;
      if (target.dataset.action === 'select-event') {
        state.selectedEventId = target.dataset.id; renderEvents();
        if (window.matchMedia('(max-width: 920px)').matches) byId('event-detail').scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else if (target.dataset.action === 'reset-events') resetEvents();
    });
    byId('show-more-events').addEventListener('click', () => { state.eventLimit += PAGE_SIZE_EVENTS; renderEvents(false); });

    const journalBindings = { 'journal-query': ['q', 'input'], 'journal-access': ['access', 'change'], 'journal-rank': ['rank', 'change'] };
    Object.entries(journalBindings).forEach(([id, [key, eventName]]) => byId(id).addEventListener(eventName, (event) => {
      state.journalFilters[key] = event.target.value; state.journalLimit = PAGE_SIZE_JOURNALS; renderJournals();
    }));
    byId('journal-active').addEventListener('change', (event) => { state.journalFilters.active = event.target.checked; state.journalLimit = PAGE_SIZE_JOURNALS; renderJournals(); });
    byId('reset-journals').addEventListener('click', resetJournals);
    byId('show-more-journals').addEventListener('click', () => { state.journalLimit += PAGE_SIZE_JOURNALS; renderJournals(); });
    byId('event-filters').addEventListener('submit', (event) => event.preventDefault());
    byId('journal-filters').addEventListener('submit', (event) => event.preventDefault());
    window.addEventListener('hashchange', () => {
      if (window.location.hash === '#journals') activateView('journals', false);
      else if (['#events', '#top', ''].includes(window.location.hash)) activateView('events', false);
    });
    document.querySelectorAll('a[href="#journals"]').forEach((link) => link.addEventListener('click', () => activateView('journals', false)));
    document.querySelectorAll('a[href="#events"]').forEach((link) => link.addEventListener('click', () => activateView('events', false)));
  }

  function tabKeyHandler(event) {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const next = event.key === 'Home' ? 'events' : event.key === 'End' ? 'journals' : state.view === 'events' ? 'journals' : 'events';
    activateView(next);
    byId(`${next}-tab`).focus();
  }

  function resetEvents() {
    state.eventFilters = { q: '', type: 'all', mode: 'all', rank: 'all', continent: 'all', country: 'all', deadline: 'open', sort: 'deadline', verified: false };
    state.eventLimit = PAGE_SIZE_EVENTS; state.selectedEventId = null; populateEventSelects(); renderEvents();
  }
  function resetJournals() {
    state.journalFilters = { q: '', access: 'all', rank: 'all', active: true };
    state.journalLimit = PAGE_SIZE_JOURNALS; populateJournalSelects(); renderJournals();
  }

  function init() {
    state.lang = getInitialLanguage();
    bindControls();
    activateView(window.location.hash === '#journals' ? 'journals' : 'events', false);
    setLanguage(state.lang, false);
    void loadData();
  }

  init();
})();
