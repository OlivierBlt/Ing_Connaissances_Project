# Movie recommendation based on video games

We want to explore 2 data sources, one for video games, https://api-docs.igdb.com/?kotlin#release-date-status (json format -> transformed: XML format) . The other one for movies is https://www.themoviedb.org with a json format.

As IGDB is an english database we will call TMDB in english to have the same language.

---

## 1. TMDB

We have 3 different calls depending on the data: movies, tv shows and genres. For movies and tv shows, we keep the 1000 most popular (at least 200 votes) plus the ones tagged `based on video game`. ~2800 works in total.

### Movie fields

The `movie.json` export contains the fields below, filtered in `fetch_tmdb.py`.

| Category | Fields |
| --- | --- |
| Identification | `id`, `title`, `original_title`, `original_language` |
| Description | `overview`, `tagline` |
| Release dates and status | `release_date`, `runtime`, `status` |
| Classification | `genres` (id, name), `keywords.keywords` (id, name) |
| Series | `belongs_to_collection` (id, name) |
| Cast and crew | `credits.cast` (name, character, order), `credits.crew` (name, job) |
| Companies | `production_companies`, `production_countries` |
| Ratings and popularity | `vote_average`, `vote_count`, `popularity` |
| Box office | `budget`, `revenue` |
| External references | `external_ids` (imdb_id, wikidata_id) |

### Tv show fields

The `tv.json` export contains the fields below, filtered in `fetch_tmdb.py`.

| Category | Fields |
| --- | --- |
| Identification | `id`, `name`, `original_name`, `original_language`, `origin_country` |
| Description | `overview` |
| Release dates and status | `first_air_date`, `last_air_date`, `status` |
| Seasons | `number_of_seasons`, `number_of_episodes` |
| Classification | `genres` (id, name), `keywords.results` (id, name) |
| Cast and creators | `aggregate_credits.cast` (name, roles.character, order), `created_by` |
| Companies | `networks` |
| Ratings and popularity | `vote_average`, `vote_count`, `popularity` |
| External references | `external_ids` (imdb_id, wikidata_id) |

### Genres

The `genres_movie.json` and `genres_tv.json` exports contain the genre lists (id, name).

| Type | Genres |
| --- | --- |
| Movies | Action, Adventure, Animation, Comedy, Crime, Documentary, Drama, Family, Fantasy, History, Horror, Music, Mystery, Romance, Science Fiction, TV Movie, Thriller, War, Western |
| Tv shows | Action & Adventure, Animation, Comedy, Crime, Documentary, Drama, Family, Kids, Mystery, News, Reality, Sci-Fi & Fantasy, Soap, Talk, War & Politics, Western |


## 2. IGDB

### Game fields

The current `games.xml` export contains 3,000 games from `/games`. Each of the 58 fields below appears in at least one game.

| Category | Fields |
| --- | --- |
| Identification | `id`, `name`, `alternative_names`, `slug`, `url` |
| Description | `summary`, `storyline` |
| Release dates and status | `first_release_date`, `release_dates`, `game_status`, `status` |
| Classification | `game_type`, `genres` (id, name), `themes`, `keywords`, `tags` |
| Platforms and technology | `platforms` (id, name), `game_engines`, `executables` |
| Gameplay | `game_modes`, `multiplayer_modes`, `player_perspectives` |
| Age ratings and localization | `age_ratings`, `language_supports`, `game_localizations` |
| Companies and series | `involved_companies`, `collections`, `franchise`, `franchises` |
| Bundles and expansions | `bundles`, `dlcs`, `expansions`, `standalone_expansions`, `expanded_games` |
| Versions and ports | `parent_game`, `version_parent`, `version_title`, `remakes`, `remasters`, `ports` |
| Other related games | `forks`, `similar_games` |
| Media | `cover`, `artworks`, `screenshots`, `videos` |
| External references | `websites`, `external_games` |
| User ratings and interest | `rating`, `rating_count`, `hypes` |
| Critic and combined ratings | `aggregated_rating`, `aggregated_rating_count`, `total_rating`, `total_rating_count` |
| Record metadata | `created_at`, `updated_at`, `checksum` |

## 3. Thesaurus

### Field mapping

| TMDB movies | TMDB tv shows | IGDB games | Link |
| --- | --- | --- | --- |
| `title`, `original_title` | `name`, `original_name` | `name`, `alternative_names` | Same work or franchise |
| `belongs_to_collection.name` | - | `franchise`, `franchises`, `collections` | Franchise |
| `credits.cast.character` | `aggregate_credits.cast.roles.character` | `/characters` (separate endpoint) | Character |
| `genres` | `genres` | `themes` | Genre / theme |
| `genres` (Adventure, Music) | `genres` (Action & Adventure) | `genres` (Adventure, Music) | Genre |
| `keywords.keywords` | `keywords.results` | `keywords` | Motif (zombies, magic...) |
| `production_companies` | `networks` | `involved_companies` | Company (Nintendo...) |
| `vote_average`, `vote_count` | `vote_average`, `vote_count` | `total_rating`, `total_rating_count` | Rating comparison |
| `overview` | `overview` | `summary`, `storyline` | Text similarity |

### Genre mapping

| TMDB genre | IGDB |
| --- | --- |
| Horror | theme Horror |
| Science Fiction, Sci-Fi & Fantasy | theme Science fiction |
| Fantasy, Sci-Fi & Fantasy | theme Fantasy |
| Action, Action & Adventure | theme Action |
| Adventure, Action & Adventure | genre Adventure |
| Comedy | theme Comedy |
| Drama | theme Drama |
| Mystery | theme Mystery |
| Romance | theme Romance |
| Thriller | theme Thriller |
| War, War & Politics | theme Warfare |
| History | theme Historical |
| Kids, Family | theme Kids |
| Documentary | theme Non-fiction |
| Music | genre Music |
| Animation, Crime, Western, TV Movie, News, Reality, Soap, Talk | - |
| - | themes Survival, Stealth, Sandbox, Open world, 4X, Party, Business, Educational |

### Schema 

The schema was created with Canva and you can access by this link : https://canva.link/u2lwrfb3x28ui00