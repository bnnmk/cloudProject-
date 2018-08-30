import json
import os
from shapely import geometry

ABS_PATH = os.path.dirname(os.path.realpath(__file__))


def load_postcodes():
    with open(ABS_PATH + '/melb_nrai_2017.geo.json') as f:
        geo = json.load(f)

        areas = []
        min_longitude = 180
        max_longitude = -180
        min_latitude = 90
        max_latitude = -90

        for area in geo['features']:
            postcode = area['properties']['geography_name']
            apex_list = area['geometry']['coordinates'][0][0]

            polygon = geometry.Polygon([(apex[0], apex[1]) for apex in apex_list])

            areas.append((postcode, polygon))

            for apex in apex_list:
                min_longitude = min(min_longitude, apex[0])
                max_longitude = max(max_longitude, apex[0])
                min_latitude = min(min_latitude, apex[1])
                max_latitude = max(max_latitude, apex[1])

        bounds = (min_longitude, max_longitude, min_latitude, max_latitude)

        return areas, bounds


def load_lgas():
    with open(ABS_PATH + '/melb_population_lga.geo.json') as f:
        geo = json.load(f)

        areas = []
        min_longitude = 180
        max_longitude = -180
        min_latitude = 90
        max_latitude = -90

        for area in geo['features']:
            lga = area['properties']['lga_code']
            apex_list = area['geometry']['coordinates'][0][0]

            polygon = geometry.Polygon([(apex[0], apex[1]) for apex in apex_list])

            areas.append((lga, polygon))

            for apex in apex_list:
                min_longitude = min(min_longitude, apex[0])
                max_longitude = max(max_longitude, apex[0])
                min_latitude = min(min_latitude, apex[1])
                max_latitude = max(max_latitude, apex[1])

        bounds = (min_longitude, max_longitude, min_latitude, max_latitude)

        return areas, bounds


AREAS_POSTCODE, BOUNDS1 = load_postcodes()
AREAS_LGA, BOUNDS2 = load_lgas()


def get_postcode(longitude, latitude):
    # BOUNDS is a rectangle that incorporates all the areas of interest
    if longitude < BOUNDS1[0] or longitude > BOUNDS1[1] or latitude < BOUNDS1[2] or latitude > BOUNDS1[3]:
        return -1

    point = geometry.Point(longitude, latitude)

    for postcode, polygon in AREAS_POSTCODE:
        if polygon.contains(point):
            return postcode

    return -1


def get_lga(longitude, latitude):
    # BOUNDS is a rectangle that incorporates all the areas of interest
    if longitude < BOUNDS2[0] or longitude > BOUNDS2[1] or latitude < BOUNDS2[2] or latitude > BOUNDS2[3]:
        return -1

    point = geometry.Point(longitude, latitude)

    for lga, polygon in AREAS_LGA:
        if polygon.contains(point):
            return lga

    return -1


if __name__ == '__main__':
    print(BOUNDS1)
    print(BOUNDS2)

    longitude = 144.957093
    latitude = -37.809666

    print(get_postcode(longitude, latitude))
    print(get_lga(longitude, latitude))
