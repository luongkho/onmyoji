from django.db import models
from .neo4j.db import Db

import pdb


class Wanted(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=30)
    rarity = models.CharField(max_length=3)
    vi_name = models.CharField(max_length=50)

    @staticmethod
    def get_all():
        sql = "MATCH (w:WANTED)-[r:APPEARS]->() WITH w, COUNT(r) AS found WHERE found > 0 RETURN w"
        result = Db.run(sql)
        if result is not False:
            records = result.records()
            wanted = [record['w'].properties for record in records]
            return wanted
        else:
            return False

    # Return json like this
    # {"1407":
    #   {"name": "Hotarugusa",
    #    "id": "5a697e690a975a0108275c29",
    #    "code_name": "Huynh_Thao",
    #    "vi_name": "Hu\u1ef3nh Th\u1ea3o",
    #    "rarity": "R",
    #    "appears": {
    #       "hunt": {"14": ["17"]},
    #       "normal": {"2": ["21"], "3": ["23"]},
    #       "orochi": {"1": ["2", "9", "10"]},
    #       "secret": {
    #           "5a68bf200a975a00f0f25de9": {
    #               "name": "Kappa",
    #               "id": "5a68bf200a975a00f0f25de9",
    #               "code_name": "Ha_Dong",
    #               "vi_name": "H\u00e0 \u0110\u1ed3ng",
    #               "rarity": "R",
    #               "found": {"1": ["4", "9"], "2": ["10"]}
    #           },
    #           "5a64bc570a975a0106700a6e": {
    #               "name": "Ootengu",
    #               "id": "5a64bc570a975a0106700a6e",
    #               "code_name": "Dai_Thien_Cau",
    #               "vi_name": "\u0110\u1ea1i Thi\u00ean C\u1ea9u",
    #               "rarity": "SSR",
    #               "found": {"4": ["7"]}}}}}
    # }
    @staticmethod
    def get_appearance_by_ids(ids):
        ids = [str(id).strip() for id in ids]
        result = Db.run("MATCH (w:WANTED)-[r:APPEARS]->(map) WHERE w.id IN $ids "
                        "OPTIONAL MATCH (map)-[:SUB_MAP_OF]->(master:MAP)"
                        "OPTIONAL MATCH (map)-[:SUB_MAP_OF]->(:SECRET)-[:OF]->(shi:HAS_SECRET) "
                        "RETURN w,r,map,master,shi "
                        "ORDER BY w.name, r.type, r.total, map.level, master.level", ids=ids)

        if result is not False:
            records = result.records()

            # Parse result
            parse_result = {}
            for record in records:
                id = record['w'].id
                wanted_properties = record['w'].properties
                if id not in parse_result:
                    parse_result[id] = wanted_properties

                location = record['r'].properties.copy()
                location.update(record['map'].properties)
                if record['master'] is not None:
                    location.update(record['master'].properties)
                if record['shi'] is not None:
                    location.update(record['shi'].properties)

                if 'appears' in parse_result[id]:
                    parse_result[id]['appears'].append(location)
                else:
                    parse_result[id]['appears'] = [location]
            # return parse_result

            # Merge similar result
            final = {}
            for id in parse_result.copy():
                wanted = parse_result[id]
                appears = wanted.pop('appears')
                wanted['appears'] = {}
                final[id] = wanted
                for appear in appears:
                    map_type = appear['type']
                    total = appear['total']
                    level = appear['level']
                    if map_type not in final[id]['appears']:
                        final[id]['appears'][map_type] = {}
                    if map_type == 'secret':
                        secret_id = appear['id']
                        if secret_id not in final[id]['appears'][map_type]:
                            has_secret = appear.copy()
                            has_secret.pop('type')
                            has_secret.pop('level')
                            has_secret.pop('total')
                            has_secret['found'] = {}
                            final[id]['appears'][map_type][secret_id] = has_secret
                        if total not in final[id]['appears'][map_type][secret_id]['found']:
                            final[id]['appears'][map_type][secret_id]['found'][total] = []
                        final[id]['appears'][map_type][secret_id]['found'][total].append(str(level))
                    else:
                        if total not in final[id]['appears'][map_type]:
                            final[id]['appears'][map_type][total] = []
                        final[id]['appears'][map_type][total].append(str(level))
            return final
        else:
            return False

    @staticmethod
    def get_all_appearance():
        result = Db.run(
            "MATCH (w:WANTED) "
            "OPTIONAL MATCH (w)-[ro:APPEARS]->(o:OROCHI) "
            "OPTIONAL MATCH (w)-[rm:APPEARS]->(:SUB_MAP)-[:SUB_MAP_OF]->(master:MAP) "
            "OPTIONAL MATCH (w)-[rs:APPEARS]->(secret:SUB_MAP)-[:SUB_MAP_OF]->(:SECRET)-[:OF]->(shi:HAS_SECRET) "
            "OPTIONAL MATCH (h:HINT)-[:HINT]->(w) "
            "WITH w, ro, o, rm, master, rs, secret, shi, h, (COUNT(ro) + COUNT(rm) + COUNT(rs)) AS found "
            "ORDER BY ro.total DESC, o.level, rm.total DESC, master.level, shi.name, rs.total DESC, secret.level "
            "WHERE found > 0 "
            "WITH w, COLLECT( DISTINCT(h.desc) ) AS hint, "
            "   CASE "
            "       WHEN ro IS NULL OR o IS NULL THEN NULL "
            "       ELSE COLLECT( DISTINCT({type:ro.type, level:o.level, total:ro.total}) ) "
            "   END AS orochi, "
            "   CASE "
            "       WHEN rm IS NULL OR master IS NULL THEN NULL "
            "       ELSE COLLECT( DISTINCT({type:rm.type, level:master.level, total:rm.total}) ) "
            "   END AS map, "
            "   CASE "
            "       WHEN rs IS NULL OR secret IS NULL OR shi IS NULL THEN NULL "
            "       ELSE {secret:shi, data:COLLECT( DISTINCT({level:secret.level, total:rs.total}) )} "
            "   END AS secret "
            "RETURN w, hint, orochi, map, COLLECT(secret) AS secret"
        )

        if result is not False:
            records = result.records()

            # Parse result
            parse_result = {}
            for record in records:
                # Define
                wanted_id = record['w'].id
                wanted = record['w'].properties
                hint = record['hint']
                orochi = record['orochi']
                maps = record['map']
                secret = record['secret']

                # Parse location
                orochi_parsed = {}
                if orochi is not None and len(orochi) > 0:
                    for orochi_map in orochi:
                        orochi_total = orochi_map['total']
                        orochi_level = orochi_map['level']
                        if orochi_total not in orochi_parsed:
                            orochi_parsed[orochi_total] = []
                        orochi_parsed[orochi_total].append(str(orochi_level))

                map_parsed = {'normal': {}, 'hard': {}, 'hunt': {}}
                if maps is not None and len(maps) > 0:
                    for map in maps:
                        map_type = map['type']
                        map_total = map['total']
                        map_level = map['level']
                        if map_total not in map_parsed[map_type]:
                            map_parsed[map_type][map_total] = []
                        map_parsed[map_type][map_total].append(str(map_level))

                secret_parsed = []
                if secret is not None and len(secret) > 0:
                    for secret_map in secret:
                        secret_merged = {}
                        secret_data = secret_map['data']
                        for map_data in secret_data:
                            secret_total = map_data['total']
                            secret_level = map_data['level']
                            if secret_total not in secret_merged:
                                secret_merged[secret_total] = []
                            secret_merged[secret_total].append(str(secret_level))
                        secret_parsed.append({'secret': secret_map['secret'].properties, 'data': secret_merged})

                # pdb.set_trace()
                # Merge final result
                found = {'orochi': orochi_parsed,
                         'normal': map_parsed['normal'], 'hard': map_parsed['hard'], 'hunt': map_parsed['hunt'],
                         'secret': secret_parsed}
                parsed = wanted.copy()
                parsed['hint'] = hint
                parsed['found'] = found
                parse_result[wanted_id] = parsed

            return parse_result
        else:
            return False


class Hint(models.Model):
    desc = models.CharField(max_length=50)

    @staticmethod
    def get_all_with_wanted():
        hint = []
        result = Db.run("MATCH (h:HINT)-[r:HINT]->(w:WANTED) RETURN h,w ORDER BY h.desc")

        if result is not False:
            records = result.records()
            for record in records:
                merge = record['h'].properties.copy()
                merge.update(record['w'].properties)
                merge['ID'] = record['h'].id
                hint.append(merge)
            return hint
        else:
            return False


class Map(models.Model):
    level = models.IntegerField()

    @staticmethod
    def get_most_appearance_by_wanted_ids(ids):
        ids = [str(id).strip() for id in ids]
        result = Db.run("MATCH (w:WANTED)-[r:APPEARS]->(map) WHERE w.id IN $ids "
                        "WITH map, count(r) as found, sum(r.total) as total WHERE found > 1 "
                        "WITH map, found, total "
                        "OPTIONAL MATCH (map)-[:SUB_MAP_OF]->(master:MAP) "
                        "OPTIONAL MATCH (map)-[:SUB_MAP_OF]->(:SECRET)-[:OF]->(shi:HAS_SECRET) "
                        "RETURN map, found, total, master, shi "
                        "ORDER BY found DESC, total DESC LIMIT 4", ids=ids)

        if result is not False:
            records = result.records()
            places = []

            for record in records:
                place = record['map'].properties.copy()
                place['found'] = record['found']
                place['total'] = record['total']
                if record['master'] is not None:
                    place.update(record['master'].properties)
                if record['shi'] is not None:
                    place.update(record['shi'].properties)
                if 'type' not in place:
                    labels = record['map'].labels
                    for label in ['NORMAL', 'HARD', 'HUNT', 'OROCHI', 'SECRET']:
                        if label in labels:
                            place['type'] = label.lower()
                            break
                places.append(place)
            return places
        else:
            return False


class Orochi(models.Model):
    level = models.IntegerField()
