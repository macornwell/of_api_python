import requests

class FruitReference:
    fruit_reference_id = None
    title = None
    reference = None
    url = None
    type = None
    author = None
    publish_date = None

    def __str__(self):
        return '{0} - {1}'.format(self.title, self.author)

class StateRegion:
    state_region_id = None
    state = None
    name = None
    counties = []
    url = None

    def __str__(self):
        return '{0}: {1}'.format(self.state, self.name)

class Location:
    country = None
    county = None
    region = None
    state = None
    city = None
    geocoordinate = None
    map_file_url = None

    def __str__(self):
        result = ''
        if self.city:
            result = self.city
        elif self.county:
            result = self.county
        elif self.state:
            result = self.state
        elif self.country:
            result = self.country
        if self.geocoordinate:
            if result:
                return '{0} - {1}'.format(result, self.geocoordinate)
            else:
                return self.geocoordinate
        else:
            return result


class Genus:
    genus_id = None
    kingdom_id = None
    latin_name = None
    name = None

    def __str__(self):
        return '{0}'.format(self.latin_name)


class Species:
    species_id = None
    genus_id = None
    latin_name = None
    name = None

    def __str__(self):
        return '{0}'.format(self.latin_name)


class Cultivar:
    cultivar_id = None
    name = None
    species = None
    species_id = None
    species_latin = None
    location = None
    origin_year = None
    uses = []
    chromosome_count = None
    ripens_early = None
    ripens_late = None
    resistances = []
    reviews = []
    brief_description = None

    def __str__(self):
        return '{0} ({1})'.format(self.name, self.species)


class ResultsList:
    count = None
    next_url = None
    previous_url = None
    results = []
    _api = None
    _create_obj_method = None

    def __str__(self):
        return 'ResultsList: Count {0}'.format(self.count)

    def get_next(self):
        if not self.next_url:
            return None
        return self._api.get_from_url(self.next_url, self._create_obj_method)

    def get_previous(self):
        if not self.previous_url:
            return None
        return self._api.get_from_url(self.previous_url, self._create_obj_method)

    def get_all_results(self):
        all_results = []
        for r in self.results:
            all_results.append(r)
        next_url = self.next_url
        while next_url:
            next_results = self._api.get_from_url(next_url, self._create_obj_method)
            next_url = next_results.next_url
            for r in next_results.results:
                all_results.append(r)
        return all_results


class FruitSearchQuery:
    species = None
    states = []
    uses = []
    year_low = None
    year_high = None
    ripening_low = None
    ripening_high = None
    references = []
    chromosomes = None
    resistances = []


class OpenFruitAPI:
    url_prefix = 'http://www.openfruit.io/api/v1'
    token_url = 'http://www.openfruit.io/api/v1/auth/token/'
    limit = None
    debug = False

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __get_token(self):
        data = {
            'username': self.username,
            'password': self.password
        }
        response = requests.post(self.token_url, data=data)
        data = response.json()
        return 'JWT ' + data['token']

    def __build_query_string(self, key_value_dict, split_value='&'):
        query = ''
        for key in key_value_dict:
            value = key_value_dict[key]
            if not value:
                continue
            if isinstance(value, list):
                value_string = ''
                for v in value:
                    value_string += '{0},'.format(v)
                value = value_string
            if value is not None:
                query += '{0}={1}{2}'.format(key, str(value), str(split_value))
        return query

    def __query(self, url, data=None):
        token = self.__get_token()
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': token,
        }
        if self.limit:
            url += '&limit=' + str(self.limit)
        if self.debug:
            print('Querying: {0}'.format(url))
        result = requests.get(url, data=data or {}, headers=headers)
        result = result.json()
        return result

    def __create_results_list(self, response_dict, obj_transform_method):
        count = response_dict['count']
        next_url = response_dict['next']
        previous_url = response_dict['previous']
        obj_list = []
        for response_dict in response_dict['results']:
            obj = obj_transform_method(response_dict)
            obj_list.append(obj)
        results_list = ResultsList()
        results_list._api = self
        results_list._create_obj_method = obj_transform_method
        results_list.count = count
        results_list.next_url = next_url
        results_list.previous_url = previous_url
        results_list.results = obj_list
        return results_list

    def __create_species(self, species_dict):
        species = Species()
        species.species_id = species_dict['species_id']
        species.latin_name = species_dict['latin_name']
        species.name = species_dict['name']
        species.genus_id = species_dict['genus_id']
        return species

    def __create_genus(self, genus_dict):
        genus = Genus()
        genus.genus_id = genus_dict['genus_id']
        genus.latin_name = genus_dict['latin_name']
        genus.name = genus_dict['name']
        genus.kingdom_id = genus_dict['kingdom_id']
        return genus

    def __create_cultivar(self, cultivar_dict):
        cultivar = Cultivar()
        cultivar.cultivar_id = cultivar_dict['cultivar_id']
        cultivar.name = cultivar_dict['name']
        cultivar.species = cultivar_dict['species']
        cultivar.species_id = cultivar_dict['species_id']
        cultivar.species_latin = cultivar_dict['species_latin']
        cultivar.origin_year = cultivar_dict['origin_year']
        if cultivar.origin_year:
            cultivar.origin_year = int(cultivar.origin_year)
        cultivar.uses = cultivar_dict['uses']
        cultivar.chromosome_count = cultivar_dict['chromosome_count']
        if cultivar.chromosome_count:
            cultivar.chromosome_count = int(cultivar.chromosome_count)
        cultivar.ripens_early = cultivar_dict['ripens_early']
        cultivar.ripens_late = cultivar_dict['ripens_late']
        cultivar.location = self.__create_location(cultivar_dict['origin_location'])
        return cultivar

    def __create_location(self, location_dict):
        location = Location()
        location.country = location_dict['country']
        location.county = location_dict['county']
        location.region = location_dict['region']
        location.state = location_dict['state']
        location.city = location_dict['city']
        location.geocoordinate = location_dict['geocoordinate']
        if 'map_file_url' in location_dict:
            location.map_file_url = location_dict['map_file_url']
        return location


    def __create_fruit_reference(self, reference_dict):
        reference = FruitReference()
        reference.fruit_reference_id = reference_dict['fruit_reference_id']
        if reference.fruit_reference_id:
            reference.fruit_reference_id = int(reference.fruit_reference_id)
        reference.title = reference_dict['title']
        reference.url = reference_dict['url']
        reference.type = reference_dict['type']
        reference.author = reference_dict['author']
        reference.publish_date = reference_dict['publish_date']
        return reference

    def __create_state_region(self, dict_obj):
        region = StateRegion()
        region.name = dict_obj['name']
        region.state_region_id = dict_obj['state_region_id']
        region.state = dict_obj['state']
        region.name = dict_obj['name']
        region.counties = dict_obj['counties']
        region.url = dict_obj['url']
        return region

    def get_from_url(self, url, transform_method):
        result = self.__query(url)
        return self.__create_results_list(result, transform_method)

    def get_cultivars_from_url(self, url):
        result = self.__query(url)
        return self.__create_results_list(result, self.__create_cultivar)

    def get_genus_from_url(self, url):
        result = self.__query(url)
        return self.__create_results_list(result, self.__create_genus)

    def get_species_from_url(self, url):
        result = self.__query(url)
        return self.__create_results_list(result, self.__create_species)

    def get_cultivars(self, species=None, name=None, name_contains=None,
                      country=None, state=None, county=None, city=None,
                      year_low=None, year_high=None, uses=[], chromosomes=None):
        data = {
            'species': species,
            'name': name,
            'name_contains': name_contains,
            'country': country,
            'state': state,
            'county': county,
            'city': city,
            'year_low': year_low,
            'year_high': year_high,
            'chromosomes': chromosomes,
        }
        use_line = ''
        for use in uses:
            use_line += '{0},'.format(use)
        if len(use_line) > 0:
            use_line = use_line[0:-1]
        data['uses'] = use_line
        url = self.url_prefix + '/cultivar_list/?'
        url += self.__build_query_string(data)
        result = self.__query(url)
        return self.__create_results_list(result, self.__create_cultivar)

    def get_species(self, species_id=None, name=None, latin_name=None, genus_latin_name=None):
        data = {}
        if species_id:
            data['species_id'] = species_id
        if name:
            data['name'] = name
        if latin_name:
            data['latin_name'] = latin_name
        if genus_latin_name:
            data['genus'] = genus_latin_name
        url = self.url_prefix + '/species_list/?'
        url += self.__build_query_string(data)
        result = self.__query(url)
        return self.__create_results_list(result, self.__create_species)

    def get_genus(self):
        data = {}
        url = self.url_prefix + '/genus_list/?'
        url += self.__build_query_string(data)
        result = self.__query(url)
        return self.__create_results_list(result, self.__create_genus)

    def fruit_search(self, *query):
        url = self.url_prefix + '/fruit-search/?'
        for q in query:
            url += 'query='
            data = {
                'species': q.species,
                'states': q.states,
                'uses': q.uses,
                'year_low': q.year_low,
                'year_high': q.year_high,
                'ripening_low': q.ripening_low,
                'ripening_high': q.ripening_high,
                'references': q.references,
                'chromosomes': q.chromosomes,
                'resistances': q.resistances,
            }
            url += self.__build_query_string(data, split_value='$')
        result = self.__query(url)
        return self.__create_results_list(result, self.__create_cultivar)

    def get_fruit_references(self, type=None, authors_name=None, title=None):
        url = self.url_prefix + '/fruit-references/?'
        data = {
            'author': authors_name,
            'title': title,
            'type': type
        }
        url += self.__build_query_string(data)
        result = self.__query(url)
        results = self.__create_results_list(result, self.__create_fruit_reference)
        return results

    def get_regions(self, name=None, state_name=None):
        url = self.url_prefix + '/state-region/?'
        data = {
            'state__name': state_name,
            'name': name,
        }
        url += self.__build_query_string(data)
        result = self.__query(url)
        results = self.__create_results_list(result, self.__create_state_region)
        return results

    """
    Multi-Geo:
    /api/v1/fruits/cultivars/?species=Malus domestica&country=United States of America&state=Georgia

    &addons=[location,review,resistances]
    &review_types=[sweet,sour,firm,bitter,juicy,rating]
    &review_metrics=[avg,max,min]
    """

    def cultivar_query(self, species_to_cultivar=None, country=None, region=None, state=None, county=None,
                       city=None, species=None, addons=None, review_types=None, review_metrics=None):
        url = self.url_prefix + '/fruits/cultivars/?'
        data = {
            'country': country,
            'region': region,
            'city': city,
            'species': species,
            'state': state,
            'county': county,
            'addons': addons,
            'review_types': review_types,
            'review_metrics': review_metrics,
        }
        species_to_cultivar = species_to_cultivar or []
        length = len(species_to_cultivar)
        for idx in range(length):
            s, c = species_to_cultivar[idx]
            data['sc_{0}'.format(idx)] = [s, c]
        url += self.__build_query_string(data)

        results = self.__query(url)

        def get_ripens(statement, mod):
            if mod == 'Late':
                return 'Late-' + statement
            if mod == 'Early':
                return 'Early-' + statement
            return statement
        cultivars = []
        for result in results:
            cultivar = Cultivar()
            cultivar.name = result['name']
            cultivar.species_latin = result['latin_name']
            cultivar.cultivar_id = result['cultivar_id']
            cultivar.origin_year = result['origin_year']
            cultivar.chromosome_count = result['chromosome_count']
            cultivar.ripens_early = get_ripens(result['ripens_early'], result['ripens_early_mod'])
            cultivar.ripens_late = get_ripens(result['ripens_late'], result['ripens_late_mod'])
            cultivar.location = self.__create_location(result['location'])
            cultivar.uses = result['uses']
            if 'review' in result:
                cultivar.reviews = result['review']
            if 'resistances' in result:
                cultivar.resistances = result['resistances']
            cultivar.brief_description = result['brief_description']
            cultivars.append(cultivar)
        return cultivars


