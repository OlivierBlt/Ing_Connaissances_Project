# Movie recommendation base on video games

We want to explore 2 data sources, one for video games, https://api-docs.igdb.com/?kotlin#release-date-status (json format) . The other one for movies is https://www.themoviedb.org/?language=fr-FR with a json format. 

As IGDB is an english database we will call TMDB in english to have the same language.

---

## 1. TMDB 
 
 We have 3 different call depending on the data, movies, tv show and the genre 

### Labels

There is a list of labels for the TMDB dataset, we keep everything for the moment then we will filter and keep just what we need.


**Movies** :
 
- `id`, `title`, `original_title`, `original_language`
- `release_date`, `runtime`, `status`
- `overview`, `tagline`
- `genres` (id, name)
- `belongs_to_collection` (id, name)
- `credits.cast` (name, character, order)
- `credits.crew` (name, job)
- `keywords.keywords` (id, name)
- `production_companies`, `production_countries`
- `vote_average`, `vote_count`, `popularity`
- `budget`, `revenue`
- `external_ids` (imdb_id, wikidata_id)

**Genre** :
 
- Movies : Action, Adventure, Animation, Comedy, Crime, Documentary, Drama, Family, Fantasy, History, Horror, Music, Mystery, Romance, Science Fiction, TV Movie, Thriller, War, Western

- Tv Show : Action & Adventure, Animation, Comedy, Crime, Documentary, Drama, Family, Kids, Mystery, News, Reality, Sci-Fi & Fantasy, Soap, Talk, War & Politics, Western

**Tv Show** :
 
- `id`, `name`, `original_name`, `original_language`, `origin_country`
- `first_air_date`, `last_air_date`, `status`
- `number_of_seasons`, `number_of_episodes`
- `overview`
- `genres` (id, name)
- `created_by`, `networks`
- `aggregate_credits.cast` (name, roles.character, order)
- `keywords.results` (id, name)
- `vote_average`, `vote_count`, `popularity`
- `external_ids` (imdb_id, wikidata_id)


## 2. IGDB 

### Labels 


## 3. Thesaurus

