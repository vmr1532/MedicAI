from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import sys
import requests
import json
import logging
import os
import requests
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

WIT_API_HOST = os.getenv('WIT_URL', 'https://api.wit.ai')
WIT_API_VERSION = os.getenv('WIT_API_VERSION', '20200513')
INTERACTIVE_PROMPT = '> '
LEARN_MORE = 'Learn more at https://wit.ai/docs/quickstart'


class WitError(Exception):
    pass


def req(logger, access_token, meth, path, params, **kwargs):
    full_url = WIT_API_HOST + path
    logger.debug('%s %s %s', meth, full_url, params)
    headers = {
        'authorization': 'Bearer ' + access_token,
        'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json'
    }
    headers.update(kwargs.pop('headers', {}))
    rsp = requests.request(
        meth,
        full_url,
        headers=headers,
        params=params,
        **kwargs
    )
    if rsp.status_code > 200:
        raise WitError('Wit responded with status: ' + str(rsp.status_code) +
                       ' (' + rsp.reason + ')')
    json = rsp.json()
    if 'error' in json:
        raise WitError('Wit responded with an error: ' + json['error'])

    logger.debug('%s %s %s', meth, full_url, json)
    return json


class Wit(object):
    access_token = None
    _sessions = {}

    def __init__(self, access_token, logger=None):
        self.access_token = access_token
        self.logger = logger or logging.getLogger(__name__)

    def message(self, msg, context=None, n=None, verbose=None):
        params = {}
        if n is not None:
            params['n'] = n
        if msg:
            params['q'] = msg
        if context:
            params['context'] = json.dumps(context)
        if verbose:
            params['verbose'] = verbose
        resp = req(self.logger, self.access_token, 'GET', '/message', params)
        return resp

    def speech(self, audio_file, headers=None, verbose=None):
        """ Sends an audio file to the /speech API.
        Uses the streaming feature of requests (see `req`), so opening the file
        in binary mode is strongly reccomended (see
        http://docs.python-requests.org/en/master/user/advanced/#streaming-uploads).
        Add Content-Type header as specified here: https://wit.ai/docs/http/20200513#post--speech-link
        :param audio_file: an open handler to an audio file
        :param headers: an optional dictionary with request headers
        :param verbose: for legacy versions, get extra information
        :return:
        """
        params = {}
        headers = headers or {}
        if verbose:
            params['verbose'] = True
        resp = req(self.logger, self.access_token, 'POST', '/speech', params,
                   data=audio_file, headers=headers)
        return resp

    def interactive(self, handle_message=None, context=None):
        """Runs interactive command line chat between user and bot. Runs
        indefinitely until EOF is entered to the prompt.
         handle_message -- optional function to customize your response.
        context -- optional initial context. Set to {} if omitted
        """
        if context is None:
            context = {}

        history = InMemoryHistory()
        while True:
            try:
                message = prompt(INTERACTIVE_PROMPT, history=history, mouse_support=True).rstrip()
            except (KeyboardInterrupt, EOFError):
                return
            if handle_message is None:
                print(self.message(message, context))
            else:
                print(handle_message(self.message(message, context)))



API_ENDPOINT =  "https://api.wit.ai/entities/intent"
WIT_ACCESS_TOKEN = 'XMRYLMHN2EDYADESNE2FYRAOHAIF6BYQ'


def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0] # to get the second entity
    if not val:
        return None
    return val



def first_trait_value(traits, trait):
    if trait not in traits:
        return None
    val = traits[trait][0]['value']
    if not val:
        return None
    return val
def handle_message(response):
    traits = response['traits']
    greetings = first_trait_value(traits, 'wit$greetings')
    medic_purchase = first_entity_value(response['entities'], 'medic_purchase:medic_purchase')
    stores_list = first_entity_value(response['entities'],'stores_list:stores_list')
    address_list = first_entity_value(response['entities'], 'address_list:address_list')
    medical_products = first_entity_value(response['entities'], 'Medical_products:Medical_products')
    mode_pay = first_entity_value(response['entities'], 'mode_pay:mode_pay')
    medic_condition = first_entity_value(response['entities'],'medical-condition:medical-condition')
    COVID19 = first_entity_value(response['entities'], 'COVID19:COVID19')
    chickenpox = first_entity_value(response['entities'], 'chicken_pox:chickenpox')
    symptoms = first_entity_value(response['entities'], 'symotoms_list:symotoms_list')

    if medic_purchase:
        return 'Enter the name of the store Where would you prefer to order from \n Enter \n \t 1) store A \n \t 2) store b \n \t 3) store c '
    elif greetings:
        return ' Hey ! How do you like to have MedicAI support ? \n 1) Enter purchase to purchase medical items \n 2) Enter check health condition to know your health condition'
    elif stores_list:
        return 'Where do you want your kit to be delivered ? \n Enter \n \t 1) Address1 to deliver to address1 \n \t 2) address2 to deliver it to address2'
    elif medical_products:
        return 'please enter the payment method \n Enter \n \t 1) wallet \n \t 2) Credit card \n \t 3) Debit card'    
    elif address_list:
        return 'enter the items you want to buy and also select the no of items you want to purchase \n Enter the option like this \n \t Eg:- band aid - 1'
    elif mode_pay:
        return 'Thanks for making the payment'

    elif medic_condition:
        return 'Please start typing the medical symptom which you are currently experiencingt to know whether you have \n 1) COVID19 \n 2) Chickenpox'
    elif COVID19:
        return 'You are having COVID19 symptoms'    
    elif chickenpox:
        return "You have chickenpox symptoms"  
    elif symptoms:
        return "Please consult nearby doctor near you"                          
    else:
        return "sorry. i did'nt understant what you have said"

client = Wit(WIT_ACCESS_TOKEN)
client.interactive(handle_message=handle_message)