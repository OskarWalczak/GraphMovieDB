# GraphMovieDB - backend

Backend do aplikacji na zaliczenie PPP, PAI, OIRPOS

Autorzy: Oskar Walczak, Marcin Sitarz

Backend aplikacji przechowującej i wyświetlającej informacjie o filmach w formie grafu.

Wykorzystuje bazę danych Neo4j i API The Movie Database https://www.themoviedb.org/

Po otrzymaniu zapytania aplikacja sprawdza, czy przechowuje informacje o danym filmie lub osobie. Jeśli nie, pobiera te informacje, oraz powiązane informacje, z TMDB i przechowuje w formie grafu.