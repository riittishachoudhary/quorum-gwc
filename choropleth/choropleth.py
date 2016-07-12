# this sets your path correctly so the imports work
import sys
import os
sys.path.insert(1, os.path.dirname(os.getcwd()))

from api import QuorumAPI
import json
# this library will let us turn dictionaries into csv files
import csv


class ChoroplethVisualizer(object):

    def save_members_by_state_json(self):
        """
        Creates a json file (serialized file) of the dictionary
        generated by above function so that it can be easily reaccessed
        without having to repeatedly call the above function.
        """
        members_by_state = self.get_members_by_state()
        with open('member_by_state.json', 'wb') as f:
            json.dump(members_by_state, f)

    def parse_members_by_state_json(self):
        """
        Parses and returns the dictionary contained in the file containing
        the members by state dictionary.
        """
        path_name = 'member_by_state.json'
        if not os.path.isfile(path_name):
             self.save_members_by_state_json()

        with open(path_name, 'rb') as f:
            data = json.load(f)
        return data

    def save_state_csv(self, item_dict, file_name):
        """
        Takes in a dictionary (item_dict) and produces a two-column
        CSV (named file_name) of the format:
        state,num
        Alabama,9
        Montana,4
        ...etc
        """
        with open(file_name, 'wb') as f:
            print "GOT HERE DOE"
            w = csv.writer(f, delimiter=',')
            w.writerow(('state', 'num'))
            w.writerows(item_dict.items())

    def get_members_by_state(self):
        """
        Creates a dictionary with state names as keys
        and representatives/senators from those states as values.
        """
        members_by_state = {}

        quorum_api = self.quorum_api.set_endpoint("state") \
                        .count(True) \
                        .limit(100) \
                        .filter()
        states = quorum_api.GET()

        for state in states["objects"]:
            state_id = state["id"]
            state_name = state["name"]
            
            quorum_api = self.quorum_api.set_endpoint("person") \
                            .count(True) \
                            .limit(100) \
                            .filter(most_recent_state = state_id, current=True)
            members = quorum_api.GET()

            member_ids = [member["id"] for member in members["objects"]]
            members_by_state[state_name] = member_ids
            print members_by_state
        return members_by_state

    def get_word_mentions_per_state(self, word):
        """
        For the given word, get the number of documents per state that it is mentioned in.
        Write this to the data.csv file.
        """
        members_by_state = self.parse_members_by_state_json()

        mentions_per_state = {}
        quorum_api = self.quorum_api.set_endpoint("document") \
                            .count(True) \
                            .limit(100) \

        for state, member_lst in members_by_state.iteritems():
            quorum_api = quorum_api.filter(count_only = True, advanced_search = word, source_person__in = member_lst)
            results = quorum_api.GET()
            # store the number of documents for this state
            mentions_per_state[state] = results
        self.save_state_csv(mentions_per_state, 'data.csv')

cv = ChoroplethVisualizer()

# the word that we are building the choropleth about!
word = "representation"

cv.get_word_mentions_per_state(word)
