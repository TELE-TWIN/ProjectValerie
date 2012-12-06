# -*- coding: utf-8 -*-

def isGenre(name):
	for genre_key in genres:
		if genre_key.lower() == name.lower():
			return True
		
	return False

def getGenre(name):
	for genre_key in genres:
		for provider_key in genres[genre_key]:
			for langugage_key in genres[genre_key][provider_key]:
				if len(genres[genre_key][provider_key][langugage_key]) > 0 and genres[genre_key][provider_key][langugage_key].lower() == name.lower():
					if genres[genre_key].has_key("name"):
						return genres[genre_key][u"name"].capitalize()
					else:
						return genre_key.capitalize()
	return u"Unknown"

genres = {}

###

genres[u"Action"] = {}
genres[u"Action"][u"imdb"] = {}
genres[u"Action"][u"themoviedb"] = {}
genres[u"Action"][u"thetvdb"] = {}

genres[u"Action"][u"imdb"][u"de"] = u"Action"
genres[u"Action"][u"imdb"][u"en"] = u"Action"
genres[u"Action"][u"imdb"][u"es"] = u"Acción"
genres[u"Action"][u"imdb"][u"fr"] = u"Action"
genres[u"Action"][u"imdb"][u"it"] = u"Azione"
genres[u"Action"][u"imdb"][u"pt"] = u"Ação"
genres[u"Action"][u"themoviedb"][u"de"] = u"action"
genres[u"Action"][u"themoviedb"][u"en"] = u"action"
genres[u"Action"][u"themoviedb"][u"es"] = u"acci-n"
genres[u"Action"][u"themoviedb"][u"fr"] = u"action"
genres[u"Action"][u"themoviedb"][u"it"] = u"azione"
genres[u"Action"][u"themoviedb"][u"pt"] = u"a-o"
genres[u"Action"][u"thetvdb"][u"en"] = u"Action and Adventure"

###

genres[u"Adventure"] = {}
genres[u"Adventure"][u"imdb"] = {}
genres[u"Adventure"][u"themoviedb"] = {}
genres[u"Adventure"][u"thetvdb"] = {}

genres[u"Adventure"][u"imdb"][u"de"] = u"Abenteuer"
genres[u"Adventure"][u"imdb"][u"en"] = u"Adventure"
genres[u"Adventure"][u"imdb"][u"es"] = u"Aventura"
genres[u"Adventure"][u"imdb"][u"fr"] = u"Aventure"
genres[u"Adventure"][u"imdb"][u"it"] = u"Avventura"
genres[u"Adventure"][u"imdb"][u"pt"] = u"Aventura"
genres[u"Adventure"][u"themoviedb"][u"de"] = u"abenteuer"
genres[u"Adventure"][u"themoviedb"][u"en"] = u"adventure"
genres[u"Adventure"][u"themoviedb"][u"es"] = u"aventura"
genres[u"Adventure"][u"themoviedb"][u"fr"] = u"aventure"
genres[u"Adventure"][u"themoviedb"][u"it"] = u"avventura"
genres[u"Adventure"][u"themoviedb"][u"pt"] = u"aventura"
genres[u"Adventure"][u"thetvdb"][u"en"] = u"Action and Adventure"

###

genres[u"Animation"] = {}
genres[u"Animation"][u"imdb"] = {}
genres[u"Animation"][u"themoviedb"] = {}
genres[u"Animation"][u"thetvdb"] = {}

genres[u"Animation"][u"imdb"][u"de"] = u"Zeichentrick"
genres[u"Animation"][u"imdb"][u"en"] = u"Animation"
genres[u"Animation"][u"imdb"][u"es"] = u"Animación"
genres[u"Animation"][u"imdb"][u"fr"] = u"Animation"
genres[u"Animation"][u"imdb"][u"it"] = u"Animazione"
genres[u"Animation"][u"imdb"][u"pt"] = u"Animação"
genres[u"Animation"][u"themoviedb"][u"de"] = u"animation"
genres[u"Animation"][u"themoviedb"][u"en"] = u"animation"
genres[u"Animation"][u"themoviedb"][u"es"] = u"animaci-n"
genres[u"Animation"][u"themoviedb"][u"fr"] = u"animation"
genres[u"Animation"][u"themoviedb"][u"it"] = u"animazione"
genres[u"Animation"][u"themoviedb"][u"pt"] = u"anima-o"
genres[u"Animation"][u"thetvdb"][u"en"] = u"Animation"

###

genres[u"Biography"] = {}
genres[u"Biography"][u"imdb"] = {}
genres[u"Biography"][u"themoviedb"] = {}
genres[u"Biography"][u"thetvdb"] = {}

genres[u"Biography"][u"imdb"][u"de"] = u"Biographie"
genres[u"Biography"][u"imdb"][u"en"] = u"Biography"
genres[u"Biography"][u"imdb"][u"es"] = u"Biografía"
genres[u"Biography"][u"imdb"][u"fr"] = u"Biographie"
genres[u"Biography"][u"imdb"][u"it"] = u"Film Biografici"
genres[u"Biography"][u"imdb"][u"pt"] = u"Biografia"
genres[u"Biography"][u"themoviedb"][u"de"] = u""
genres[u"Biography"][u"themoviedb"][u"en"] = u""
genres[u"Biography"][u"themoviedb"][u"es"] = u""
genres[u"Biography"][u"themoviedb"][u"fr"] = u""
genres[u"Biography"][u"themoviedb"][u"it"] = u""
genres[u"Biography"][u"themoviedb"][u"pt"] = u""
genres[u"Biography"][u"thetvdb"][u"en"] = u""

###

genres[u"Comedy"] = {}
genres[u"Comedy"][u"imdb"] = {}
genres[u"Comedy"][u"themoviedb"] = {}
genres[u"Comedy"][u"thetvdb"] = {}

genres[u"Comedy"][u"imdb"][u"de"] = u"Komödie"
genres[u"Comedy"][u"imdb"][u"en"] = u"Comedy"
genres[u"Comedy"][u"imdb"][u"es"] = u"Comedia"
genres[u"Comedy"][u"imdb"][u"fr"] = u"Comédie"
genres[u"Comedy"][u"imdb"][u"it"] = u"Commedie"
genres[u"Comedy"][u"imdb"][u"pt"] = u"Comédia"
genres[u"Comedy"][u"themoviedb"][u"de"] = u"comedy"
genres[u"Comedy"][u"themoviedb"][u"en"] = u"comedy"
genres[u"Comedy"][u"themoviedb"][u"es"] = u"comedia"
genres[u"Comedy"][u"themoviedb"][u"fr"] = u"com-die"
genres[u"Comedy"][u"themoviedb"][u"it"] = u"commedia"
genres[u"Comedy"][u"themoviedb"][u"pt"] = u"com-dia"
genres[u"Comedy"][u"thetvdb"][u"en"] = u"Comedy"

###

genres[u"Crime"] = {}
genres[u"Crime"][u"imdb"] = {}
genres[u"Crime"][u"themoviedb"] = {}
genres[u"Crime"][u"thetvdb"] = {}

genres[u"Crime"][u"imdb"][u"de"] = u"Krimi"
genres[u"Crime"][u"imdb"][u"en"] = u"Crime"
genres[u"Crime"][u"imdb"][u"es"] = u"Crimen"
genres[u"Crime"][u"imdb"][u"fr"] = u"Crime"
genres[u"Crime"][u"imdb"][u"it"] = u"Crimine"
genres[u"Crime"][u"imdb"][u"pt"] = u"Crime"
genres[u"Crime"][u"themoviedb"][u"de"] = u"crime"
genres[u"Crime"][u"themoviedb"][u"en"] = u"crime"
genres[u"Crime"][u"themoviedb"][u"es"] = u"crimen"
genres[u"Crime"][u"themoviedb"][u"fr"] = u"crime"
genres[u"Crime"][u"themoviedb"][u"it"] = u"crime"
genres[u"Crime"][u"themoviedb"][u"pt"] = u"crime"
genres[u"Crime"][u"thetvdb"][u"en"] = u""

###

genres[u"Documentary"] = {}
genres[u"Documentary"][u"imdb"] = {}
genres[u"Documentary"][u"themoviedb"] = {}
genres[u"Documentary"][u"thetvdb"] = {}

genres[u"Documentary"][u"imdb"][u"de"] = u"Dokumentation"
genres[u"Documentary"][u"imdb"][u"en"] = u"Documentary"
genres[u"Documentary"][u"imdb"][u"es"] = u"Documentales"
genres[u"Documentary"][u"imdb"][u"fr"] = u"Documentaire"
genres[u"Documentary"][u"imdb"][u"it"] = u"Documentari"
genres[u"Documentary"][u"imdb"][u"pt"] = u"Documentário"
genres[u"Documentary"][u"themoviedb"][u"de"] = u"dokumentarfilm"
genres[u"Documentary"][u"themoviedb"][u"en"] = u"documentary"
genres[u"Documentary"][u"themoviedb"][u"es"] = u"documental"
genres[u"Documentary"][u"themoviedb"][u"fr"] = u"documentaire"
genres[u"Documentary"][u"themoviedb"][u"it"] = u"documentario"
genres[u"Documentary"][u"themoviedb"][u"pt"] = u"document-rio"
genres[u"Documentary"][u"thetvdb"][u"en"] = u"Documentary"

###

genres[u"Drama"] = {}
genres[u"Drama"][u"imdb"] = {}
genres[u"Drama"][u"themoviedb"] = {}
genres[u"Drama"][u"thetvdb"] = {}

genres[u"Drama"][u"imdb"][u"de"] = u"Drama"
genres[u"Drama"][u"imdb"][u"en"] = u"Drama"
genres[u"Drama"][u"imdb"][u"es"] = u"Drama"
genres[u"Drama"][u"imdb"][u"fr"] = u"Drame"
genres[u"Drama"][u"imdb"][u"it"] = u"Drammatici"
genres[u"Drama"][u"imdb"][u"pt"] = u"Drama"
genres[u"Drama"][u"themoviedb"][u"de"] = u"drama"
genres[u"Drama"][u"themoviedb"][u"en"] = u"drama"
genres[u"Drama"][u"themoviedb"][u"es"] = u"drama"
genres[u"Drama"][u"themoviedb"][u"fr"] = u"drame"
genres[u"Drama"][u"themoviedb"][u"it"] = u"drama"
genres[u"Drama"][u"themoviedb"][u"pt"] = u"drama"
genres[u"Drama"][u"thetvdb"][u"en"] = u"Drama"

###

genres[u"Family"] = {}
genres[u"Family"][u"imdb"] = {}
genres[u"Family"][u"themoviedb"] = {}
genres[u"Family"][u"thetvdb"] = {}

genres[u"Family"][u"imdb"][u"de"] = u"Familie"
genres[u"Family"][u"imdb"][u"en"] = u"Family"
genres[u"Family"][u"imdb"][u"es"] = u"Familia"
genres[u"Family"][u"imdb"][u"fr"] = u"Famille"
genres[u"Family"][u"imdb"][u"it"] = u"Famiglia"
genres[u"Family"][u"imdb"][u"pt"] = u"Familia"
genres[u"Family"][u"themoviedb"][u"de"] = u"familie"
genres[u"Family"][u"themoviedb"][u"en"] = u"family"
genres[u"Family"][u"themoviedb"][u"es"] = u"familia"
genres[u"Family"][u"themoviedb"][u"fr"] = u"la-famille"
genres[u"Family"][u"themoviedb"][u"it"] = u"famiglia"
genres[u"Family"][u"themoviedb"][u"pt"] = u"fam-lia"
genres[u"Family"][u"thetvdb"][u"en"] = u"Children"

###

genres[u"Fantasy"] = {}
genres[u"Fantasy"][u"imdb"] = {}
genres[u"Fantasy"][u"themoviedb"] = {}
genres[u"Fantasy"][u"thetvdb"] = {}

genres[u"Fantasy"][u"imdb"][u"de"] = u"Fantasy"
genres[u"Fantasy"][u"imdb"][u"en"] = u"Fantasy"
genres[u"Fantasy"][u"imdb"][u"es"] = u"Fantasía"
genres[u"Fantasy"][u"imdb"][u"fr"] = u"Fantaisie"
genres[u"Fantasy"][u"imdb"][u"it"] = u"Fantasy"
genres[u"Fantasy"][u"imdb"][u"pt"] = u"Fantasia"
genres[u"Fantasy"][u"themoviedb"][u"de"] = u"fantasy"
genres[u"Fantasy"][u"themoviedb"][u"en"] = u"fantasy"
genres[u"Fantasy"][u"themoviedb"][u"es"] = u"fantas-a"
genres[u"Fantasy"][u"themoviedb"][u"fr"] = u"fantasy"
genres[u"Fantasy"][u"themoviedb"][u"it"] = u"fantasy"
genres[u"Fantasy"][u"themoviedb"][u"pt"] = u"fantasia"
genres[u"Fantasy"][u"thetvdb"][u"en"] = u"Fantasy"

###

genres[u"Film-Noir"] = {}
genres[u"Film-Noir"][u"imdb"] = {}
genres[u"Film-Noir"][u"themoviedb"] = {}
genres[u"Film-Noir"][u"thetvdb"] = {}

genres[u"Film-Noir"][u"imdb"][u"de"] = u"Film-Noir"
genres[u"Film-Noir"][u"imdb"][u"en"] = u"Film-Noir"
genres[u"Film-Noir"][u"imdb"][u"es"] = u"Film-Noir"
genres[u"Film-Noir"][u"imdb"][u"fr"] = u"Film Noir"
genres[u"Film-Noir"][u"imdb"][u"it"] = u"Film Noir"
genres[u"Film-Noir"][u"imdb"][u"pt"] = u"Film-Noir"
genres[u"Film-Noir"][u"themoviedb"][u"de"] = u"film-noir"
genres[u"Film-Noir"][u"themoviedb"][u"en"] = u"film-noir"
genres[u"Film-Noir"][u"themoviedb"][u"es"] = u"film-noir"
genres[u"Film-Noir"][u"themoviedb"][u"fr"] = u"film-noir"
genres[u"Film-Noir"][u"themoviedb"][u"it"] = u"film-noir"
genres[u"Film-Noir"][u"themoviedb"][u"pt"] = u"film-noir"
genres[u"Film-Noir"][u"thetvdb"][u"en"] = u""

###

genres[u"History"] = {}
genres[u"History"][u"imdb"] = {}
genres[u"History"][u"themoviedb"] = {}
genres[u"History"][u"thetvdb"] = {}

genres[u"History"][u"imdb"][u"de"] = u"Geschichte"
genres[u"History"][u"imdb"][u"en"] = u"History"
genres[u"History"][u"imdb"][u"es"] = u"Historia"
genres[u"History"][u"imdb"][u"fr"] = u"Histoire"
genres[u"History"][u"imdb"][u"it"] = u"Storici"
genres[u"History"][u"imdb"][u"pt"] = u"História"
genres[u"History"][u"themoviedb"][u"de"] = u"geschichte"
genres[u"History"][u"themoviedb"][u"en"] = u"history"
genres[u"History"][u"themoviedb"][u"es"] = u"historia"
genres[u"History"][u"themoviedb"][u"fr"] = u"histoire"
genres[u"History"][u"themoviedb"][u"it"] = u"storia"
genres[u"History"][u"themoviedb"][u"pt"] = u"hist-ria"
genres[u"History"][u"thetvdb"][u"en"] = u""

###

genres[u"Horror"] = {}
genres[u"Horror"][u"imdb"] = {}
genres[u"Horror"][u"themoviedb"] = {}
genres[u"Horror"][u"thetvdb"] = {}

genres[u"Horror"][u"imdb"][u"de"] = u"Horror"
genres[u"Horror"][u"imdb"][u"en"] = u"Horror"
genres[u"Horror"][u"imdb"][u"es"] = u"Horror"
genres[u"Horror"][u"imdb"][u"fr"] = u"Horreur"
genres[u"Horror"][u"imdb"][u"it"] = u"Horror"
genres[u"Horror"][u"imdb"][u"pt"] = u"Terror"
genres[u"Horror"][u"themoviedb"][u"de"] = u"horror"
genres[u"Horror"][u"themoviedb"][u"en"] = u"horror"
genres[u"Horror"][u"themoviedb"][u"es"] = u"horror"
genres[u"Horror"][u"themoviedb"][u"fr"] = u"horreur"
genres[u"Horror"][u"themoviedb"][u"it"] = u"horror"
genres[u"Horror"][u"themoviedb"][u"pt"] = u"terror"
genres[u"Horror"][u"thetvdb"][u"en"] = u""

###

genres[u"Independent"] = {}
genres[u"Independent"][u"imdb"] = {}
genres[u"Independent"][u"themoviedb"] = {}
genres[u"Independent"][u"thetvdb"] = {}

genres[u"Independent"][u"imdb"][u"de"] = u"Independent"
genres[u"Independent"][u"imdb"][u"en"] = u"Independent"
genres[u"Independent"][u"imdb"][u"es"] = u"Independiente"
genres[u"Independent"][u"imdb"][u"fr"] = u"Indépendant"
genres[u"Independent"][u"imdb"][u"it"] = u"Indipendenti"
genres[u"Independent"][u"imdb"][u"pt"] = u"Independente"
genres[u"Independent"][u"themoviedb"][u"de"] = u"indie"
genres[u"Independent"][u"themoviedb"][u"en"] = u"indie"
genres[u"Independent"][u"themoviedb"][u"es"] = u"indie"
genres[u"Independent"][u"themoviedb"][u"fr"] = u"indie"
genres[u"Independent"][u"themoviedb"][u"it"] = u"indie"
genres[u"Independent"][u"themoviedb"][u"pt"] = u"indie"
genres[u"Independent"][u"thetvdb"][u"en"] = u""

###

genres[u"Music"] = {}
genres[u"Music"][u"imdb"] = {}
genres[u"Music"][u"themoviedb"] = {}
genres[u"Music"][u"thetvdb"] = {}

genres[u"Music"][u"imdb"][u"de"] = u"Musik"
genres[u"Music"][u"imdb"][u"en"] = u"Music"
genres[u"Music"][u"imdb"][u"es"] = u"Música"
genres[u"Music"][u"imdb"][u"fr"] = u"Musique"
genres[u"Music"][u"imdb"][u"it"] = u"Musica"
genres[u"Music"][u"imdb"][u"pt"] = u"Música"
genres[u"Music"][u"themoviedb"][u"de"] = u"musik"
genres[u"Music"][u"themoviedb"][u"en"] = u"music"
genres[u"Music"][u"themoviedb"][u"es"] = u"m-sica"
genres[u"Music"][u"themoviedb"][u"fr"] = u"musique"
genres[u"Music"][u"themoviedb"][u"it"] = u"musica"
genres[u"Music"][u"themoviedb"][u"pt"] = u"m-sica"
genres[u"Music"][u"thetvdb"][u"en"] = u""

###

genres[u"Musical"] = {}
genres[u"Musical"][u"imdb"] = {}
genres[u"Musical"][u"themoviedb"] = {}
genres[u"Musical"][u"thetvdb"] = {}

genres[u"Musical"][u"imdb"][u"de"] = u"Musical"
genres[u"Musical"][u"imdb"][u"en"] = u"Musical"
genres[u"Musical"][u"imdb"][u"es"] = u"Musical"
genres[u"Musical"][u"imdb"][u"fr"] = u"Musical"
genres[u"Musical"][u"imdb"][u"it"] = u"Musicali"
genres[u"Musical"][u"imdb"][u"pt"] = u"Musical"
genres[u"Musical"][u"themoviedb"][u"de"] = u"musical"
genres[u"Musical"][u"themoviedb"][u"en"] = u"musical"
genres[u"Musical"][u"themoviedb"][u"es"] = u"musical"
genres[u"Musical"][u"themoviedb"][u"fr"] = u"musical"
genres[u"Musical"][u"themoviedb"][u"it"] = u"musical"
genres[u"Musical"][u"themoviedb"][u"pt"] = u"musical"
genres[u"Musical"][u"thetvdb"][u"en"] = u""

###

genres[u"Mystery"] = {}
genres[u"Mystery"][u"imdb"] = {}
genres[u"Mystery"][u"themoviedb"] = {}
genres[u"Mystery"][u"thetvdb"] = {}

genres[u"Mystery"][u"imdb"][u"de"] = u"Mystery"
genres[u"Mystery"][u"imdb"][u"en"] = u"Mystery"
genres[u"Mystery"][u"imdb"][u"es"] = u"Misterio"
genres[u"Mystery"][u"imdb"][u"fr"] = u"Mystère"
genres[u"Mystery"][u"imdb"][u"it"] = u"Mystery"
genres[u"Mystery"][u"imdb"][u"pt"] = u"Mistério"
genres[u"Mystery"][u"themoviedb"][u"de"] = u"mystery"
genres[u"Mystery"][u"themoviedb"][u"en"] = u"mystery"
genres[u"Mystery"][u"themoviedb"][u"es"] = u"misterio"
genres[u"Mystery"][u"themoviedb"][u"fr"] = u"myst-re"
genres[u"Mystery"][u"themoviedb"][u"it"] = u"mistero"
genres[u"Mystery"][u"themoviedb"][u"pt"] = u"mist-rio"
genres[u"Mystery"][u"thetvdb"][u"en"] = u""

###

genres[u"Romance"] = {}
genres[u"Romance"][u"imdb"] = {}
genres[u"Romance"][u"themoviedb"] = {}
genres[u"Romance"][u"thetvdb"] = {}

genres[u"Romance"][u"imdb"][u"de"] = u"Romanze"
genres[u"Romance"][u"imdb"][u"en"] = u"Romance"
genres[u"Romance"][u"imdb"][u"es"] = u"Romance"
genres[u"Romance"][u"imdb"][u"fr"] = u"Romance"
genres[u"Romance"][u"imdb"][u"it"] = u"Romantici"
genres[u"Romance"][u"imdb"][u"pt"] = u"Romance"
genres[u"Romance"][u"themoviedb"][u"de"] = u"romanze"
genres[u"Romance"][u"themoviedb"][u"en"] = u"romance"
genres[u"Romance"][u"themoviedb"][u"es"] = u"romance"
genres[u"Romance"][u"themoviedb"][u"fr"] = u"romance"
genres[u"Romance"][u"themoviedb"][u"it"] = u"romance"
genres[u"Romance"][u"themoviedb"][u"pt"] = u"romance"
genres[u"Romance"][u"thetvdb"][u"en"] = u""

###

genres[u"Sci-Fi"] = {}
genres[u"Sci-Fi"][u"imdb"] = {}
genres[u"Sci-Fi"][u"themoviedb"] = {}
genres[u"Sci-Fi"][u"thetvdb"] = {}

genres[u"Sci-Fi"][u"imdb"][u"de"] = u"Sci-Fi"
genres[u"Sci-Fi"][u"imdb"][u"en"] = u"Sci-Fi"
genres[u"Sci-Fi"][u"imdb"][u"es"] = u"Ciencia ficción"
genres[u"Sci-Fi"][u"imdb"][u"fr"] = u"Science-fiction"
genres[u"Sci-Fi"][u"imdb"][u"it"] = u"Fantascienza"
genres[u"Sci-Fi"][u"imdb"][u"pt"] = u"Ficção Cientifica"
genres[u"Sci-Fi"][u"themoviedb"][u"de"] = u"science-fiction"
genres[u"Sci-Fi"][u"themoviedb"][u"en"] = u"science-fiction"
genres[u"Sci-Fi"][u"themoviedb"][u"es"] = u"ciencia-ficci-n"
genres[u"Sci-Fi"][u"themoviedb"][u"fr"] = u"science-fiction"
genres[u"Sci-Fi"][u"themoviedb"][u"it"] = u"fantascienza"
genres[u"Sci-Fi"][u"themoviedb"][u"pt"] = u"fic-o-cient-fica"
genres[u"Sci-Fi"][u"thetvdb"][u"en"] = u"Science-Fiction"

###

genres[u"Short"] = {}
genres[u"Short"][u"imdb"] = {}
genres[u"Short"][u"themoviedb"] = {}
genres[u"Short"][u"thetvdb"] = {}

genres[u"Short"][u"imdb"][u"de"] = u"Kurzfilm"
genres[u"Short"][u"imdb"][u"en"] = u"Short"
genres[u"Short"][u"imdb"][u"es"] = u"Cortos"
genres[u"Short"][u"imdb"][u"fr"] = u"Court-métrage"
genres[u"Short"][u"imdb"][u"it"] = u"Corti"
genres[u"Short"][u"imdb"][u"pt"] = u"Curtas"
genres[u"Short"][u"themoviedb"][u"de"] = u"kurzfilm"
genres[u"Short"][u"themoviedb"][u"en"] = u"short"
genres[u"Short"][u"themoviedb"][u"es"] = u"corto"
genres[u"Short"][u"themoviedb"][u"fr"] = u"short"
genres[u"Short"][u"themoviedb"][u"it"] = u"breve"
genres[u"Short"][u"themoviedb"][u"pt"] = u"curta"
genres[u"Short"][u"thetvdb"][u"en"] = u""

###

genres[u"Sport"] = {}
genres[u"Sport"][u"imdb"] = {}
genres[u"Sport"][u"themoviedb"] = {}
genres[u"Sport"][u"thetvdb"] = {}

genres[u"Sport"][u"imdb"][u"de"] = u"Sport"
genres[u"Sport"][u"imdb"][u"en"] = u"Sport"
genres[u"Sport"][u"imdb"][u"es"] = u"Deportes"
genres[u"Sport"][u"imdb"][u"fr"] = u"Sport"
genres[u"Sport"][u"imdb"][u"it"] = u"Sport"
genres[u"Sport"][u"imdb"][u"pt"] = u"Esporte"
genres[u"Sport"][u"themoviedb"][u"de"] = u"sport"
genres[u"Sport"][u"themoviedb"][u"en"] = u"sport"
genres[u"Sport"][u"themoviedb"][u"es"] = u"deporte"
genres[u"Sport"][u"themoviedb"][u"fr"] = u"sport"
genres[u"Sport"][u"themoviedb"][u"it"] = u"sport"
genres[u"Sport"][u"themoviedb"][u"pt"] = u"esporte"
genres[u"Sport"][u"themoviedb"][u"de2"] = u"sportereignis"
genres[u"Sport"][u"themoviedb"][u"en2"] = u"sporting-event"
genres[u"Sport"][u"themoviedb"][u"es2"] = u"sporting-event"
genres[u"Sport"][u"themoviedb"][u"fr2"] = u"sporting-event"
genres[u"Sport"][u"themoviedb"][u"it2"] = u"sporting-event"
genres[u"Sport"][u"themoviedb"][u"pt2"] = u"sporting-event"
genres[u"Sport"][u"themoviedb"][u"de3"] = u"sport-film"
genres[u"Sport"][u"themoviedb"][u"en3"] = u"sports-film"
genres[u"Sport"][u"themoviedb"][u"es3"] = u"sports-film"
genres[u"Sport"][u"themoviedb"][u"fr3"] = u"sports-film"
genres[u"Sport"][u"themoviedb"][u"it3"] = u"sports-film"
genres[u"Sport"][u"themoviedb"][u"pt3"] = u"sports-film"
genres[u"Sport"][u"thetvdb"][u"en"] = u"Sport"

###

genres[u"Thriller"] = {}
genres[u"Thriller"][u"imdb"] = {}
genres[u"Thriller"][u"themoviedb"] = {}
genres[u"Thriller"][u"thetvdb"] = {}

genres[u"Thriller"][u"imdb"][u"de"] = u"Thriller"
genres[u"Thriller"][u"imdb"][u"en"] = u"Thriller"
genres[u"Thriller"][u"imdb"][u"es"] = u"Thriller"
genres[u"Thriller"][u"imdb"][u"fr"] = u"Thriller"
genres[u"Thriller"][u"imdb"][u"it"] = u"Thriller"
genres[u"Thriller"][u"imdb"][u"pt"] = u"Suspense"
genres[u"Thriller"][u"themoviedb"][u"de"] = u"thriller"
genres[u"Thriller"][u"themoviedb"][u"en"] = u"thriller"
genres[u"Thriller"][u"themoviedb"][u"es"] = u"novela-de-suspense"
genres[u"Thriller"][u"themoviedb"][u"fr"] = u"thriller"
genres[u"Thriller"][u"themoviedb"][u"it"] = u"thriller"
genres[u"Thriller"][u"themoviedb"][u"pt"] = u"thriller"
genres[u"Thriller"][u"thetvdb"][u"en"] = u""

###

genres[u"TV mini-series"] = {}
genres[u"TV mini-series"][u"imdb"] = {}
genres[u"TV mini-series"][u"themoviedb"] = {}
genres[u"TV mini-series"][u"thetvdb"] = {}

genres[u"TV mini-series"][u"imdb"][u"de"] = u"TV-Miniserie"
genres[u"TV mini-series"][u"imdb"][u"en"] = u"TV mini-series"
genres[u"TV mini-series"][u"imdb"][u"es"] = u"Mini-series de TV"
genres[u"TV mini-series"][u"imdb"][u"fr"] = u"Mini séries TV"
genres[u"TV mini-series"][u"imdb"][u"it"] = u"Miniserie TV"
genres[u"TV mini-series"][u"imdb"][u"pt"] = u"TV mini-series"
genres[u"TV mini-series"][u"themoviedb"][u"de"] = u""
genres[u"TV mini-series"][u"themoviedb"][u"en"] = u""
genres[u"TV mini-series"][u"themoviedb"][u"es"] = u""
genres[u"TV mini-series"][u"themoviedb"][u"fr"] = u""
genres[u"TV mini-series"][u"themoviedb"][u"it"] = u""
genres[u"TV mini-series"][u"themoviedb"][u"pt"] = u""
genres[u"TV mini-series"][u"thetvdb"][u"en"] = u"Mini-Series"

###

genres[u"War"] = {}
genres[u"War"][u"imdb"] = {}
genres[u"War"][u"themoviedb"] = {}
genres[u"War"][u"thetvdb"] = {}

genres[u"War"][u"imdb"][u"de"] = u"Krieg"
genres[u"War"][u"imdb"][u"en"] = u"War"
genres[u"War"][u"imdb"][u"es"] = u"Guerra"
genres[u"War"][u"imdb"][u"fr"] = u"Guerre"
genres[u"War"][u"imdb"][u"it"] = u"Guerra"
genres[u"War"][u"imdb"][u"pt"] = u"Guerra"
genres[u"War"][u"themoviedb"][u"de"] = u"kriegsfilm"
genres[u"War"][u"themoviedb"][u"en"] = u"war"
genres[u"War"][u"themoviedb"][u"es"] = u"guerra"
genres[u"War"][u"themoviedb"][u"fr"] = u"guerre"
genres[u"War"][u"themoviedb"][u"it"] = u"guerra"
genres[u"War"][u"themoviedb"][u"pt"] = u"guerra"
genres[u"War"][u"thetvdb"][u"en"] = u""

###

genres[u"Western"] = {}
genres[u"Western"][u"imdb"] = {}
genres[u"Western"][u"themoviedb"] = {}
genres[u"Western"][u"thetvdb"] = {}

genres[u"Western"][u"imdb"][u"de"] = u"Western"
genres[u"Western"][u"imdb"][u"en"] = u"Western"
genres[u"Western"][u"imdb"][u"es"] = u"Western /Del Oeste"
genres[u"Western"][u"imdb"][u"fr"] = u"Western"
genres[u"Western"][u"imdb"][u"it"] = u"Western"
genres[u"Western"][u"imdb"][u"pt"] = u"Faroeste"
genres[u"Western"][u"themoviedb"][u"de"] = u"western"
genres[u"Western"][u"themoviedb"][u"en"] = u"western"
genres[u"Western"][u"themoviedb"][u"es"] = u"occidental"
genres[u"Western"][u"themoviedb"][u"fr"] = u"ouest"
genres[u"Western"][u"themoviedb"][u"it"] = u"western"
genres[u"Western"][u"themoviedb"][u"pt"] = u"faroeste"
genres[u"Western"][u"thetvdb"][u"en"] = u"Western"
