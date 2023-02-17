from neomodel import db
from neo4j.graph import Node


def movieQuery(movie_id):
    query_response = db.cypher_query(
        'MATCH (m:Movie {movie_id: "' + movie_id + '"})<-[d1:DIRECTED]-(d:Person) '
        'OPTIONAL MATCH (d)-[d2:DIRECTED]->(m2:Movie) '
        'OPTIONAL MATCH (m)-[g1:BELONGS_TO_GENRE]->(g:Genre) '
        'OPTIONAL MATCH (m)-[g2:BELONGS_TO_GENRE]->(g)<-[g3:BELONGS_TO_GENRE]-(m3:Movie) '
        'OPTIONAL MATCH (m)<-[a1:ACTED_IN]-(a:Person)-[a2:ACTED_IN]->(m4:Movie) '
        'WHERE m4.movie_id <> "' + movie_id + '" '
        'WITH collect(distinct m) + collect(distinct d) + collect(distinct m2) + collect(distinct g) + '
        'collect(distinct m3) + collect(distinct m4) + collect(distinct a) + collect( d1) +  collect( d2) +  '
        'collect( g1) +  collect( g2) +  collect( g3) +  collect( a1) +  '
        'collect( a2) as nodes '
        'WITH REDUCE(output = [], i IN nodes| output + i) AS flat '
        'UNWIND flat AS all '
        'RETURN DISTINCT all '
    )[0]

    links = []
    nodes = []

    movie_set = frozenset(['Movie'])
    person_set = frozenset(['Person'])
    genre_set = frozenset(['Genre'])

    print(query_response)
    print(len(query_response))

    for ln in query_response:
        for sth in ln:
            if len(sth._properties) == 0:
                source_id = ""
                target_id = ""
                for n in sth.nodes:
                    if movie_set.issubset(n.labels):
                        source_id = n['movie_id']
                    if genre_set.issubset(n.labels):
                        target_id = n['genre_id']
                    if person_set.issubset(n.labels):
                        target_id = n['person_id']
                links.append({
                    "source": source_id,
                    "target": target_id,
                    "value": 5 * (5 if sth.type == 'DIRECTED' else 1)
                })
            elif movie_set.issubset(sth.labels):
                nodes.append({
                    "id": sth['movie_id'],
                    "text": sth['title'],
                    "group": 1 + (3 if sth['movie_id'] == movie_id else 0)
                })
            elif genre_set.issubset(sth.labels):
                nodes.append({
                    "id": sth['genre_id'],
                    "text": sth['name'],
                    "group": 2
                })
            elif person_set.issubset(sth.labels):
                nodes.append({
                    "id": sth['person_id'],
                    "text": sth['name'],
                    "group": 3
                })

    for link in links:
        found_source = False
        found_target = False
        for node in nodes:
            if node['id'] == link['source']:
                found_source = True
            if node['id'] == link['target']:
                found_target = True
        if link['source'] == "" or link['target'] == "" or not found_source or not found_target or link['source'] == \
                link['target']:
            links.remove(link)

    print(len(nodes), len(links))
    return nodes, links


def personQuery(person_id):
    query_response = db.cypher_query(
        'MATCH (p:Person {person_id: "' + person_id + '"}) '
        'OPTIONAL MATCH (p)-[a1:ACTED_IN]->(m:Movie) '
        'OPTIONAL MATCH (p)-[d1:DIRECTED]->(m2:Movie) '
        'WITH collect(distinct p) + collect(distinct a1) + collect(distinct m) + '
        'collect(distinct d1) + collect(distinct m2) as nodes '
        'WITH REDUCE (output = [], i IN nodes| output + i) AS flat '
        'UNWIND flat as all '
        'RETURN DISTINCT all '
    )[0]

    links = []
    nodes = []

    movie_set = frozenset(['Movie'])
    person_set = frozenset(['Person'])
    genre_set = frozenset(['Genre'])

    print(query_response)
    print(len(query_response))

    for ln in query_response:
        for sth in ln:
            if len(sth._properties) == 0:
                source_id = ""
                target_id = ""
                for n in sth.nodes:
                    if movie_set.issubset(n.labels):
                        source_id = n['movie_id']
                    if genre_set.issubset(n.labels):
                        target_id = n['genre_id']
                    if person_set.issubset(n.labels):
                        target_id = n['person_id']
                links.append({
                    "source": source_id,
                    "target": target_id,
                    "value": 5 * (5 if sth.type == 'DIRECTED' else 1)
                })
            elif movie_set.issubset(sth.labels):
                nodes.append({
                    "id": sth['movie_id'],
                    "text": sth['title'],
                    "group": 1
                })
            elif genre_set.issubset(sth.labels):
                nodes.append({
                    "id": sth['genre_id'],
                    "text": sth['name'],
                    "group": 2
                })
            elif person_set.issubset(sth.labels):
                nodes.append({
                    "id": sth['person_id'],
                    "text": sth['name'],
                    "group": 3
                })

    for link in links:
        found_source = False
        found_target = False
        for node in nodes:
            if node['id'] == link['source']:
                found_source = True
            if node['id'] == link['target']:
                found_target = True
        if link['source'] == "" or link['target'] == "" or not found_source or not found_target or link['source'] == link['target']:
            links.remove(link)

    print(len(nodes), len(links))
    return nodes, links

