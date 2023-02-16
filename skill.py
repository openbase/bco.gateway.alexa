import requests
import gettext
from gettext import gettext as _
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractResponseInterceptor, AbstractExceptionHandler
from ask_sdk_core.utils import is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from typing import Dict, Any
from more_itertools import first

# Define constants
BCO_GRAPHQL_ENDPOINT = 'http://ha:13781/graphql'

# Define the skill builder
sb = SkillBuilder()

# Initialize gettext
gettext.install('messages', localedir='locales', names=['ngettext'])

def get_slot_value(handler_input: HandlerInput, slot_name: str) -> str:
    """
    Helper function to get the value of a slot.

    :param handler_input: Handler input object.
    :param slot_name: Name of the slot.
    :return: Value of the slot.
    """
    return handler_input.request_envelope.request.intent.slots[slot_name].value

def get_language(handler_input: HandlerInput) -> str:
    """
    Helper function to get the current language of the user.

    :param handler_input: Handler input object.
    :return: Language code, e.g. 'en_US'.
    """
    return handler_input.request_envelope.request.locale

def get_device_by_label(label: str) -> Dict[str, Any]:
    """
    Helper function to get a device by its label.

    :param label: Label of the device.
    :return: Device object, or None if not found.
    """
    query = '''
        query {{
            devices {{
                id
                label {{
                    value
                    language
                }}
            }}
        }}
    '''
    response = requests.post(BCO_GRAPHQL_ENDPOINT, json={'query': query})
    devices = response.json()['data']['devices']
    for device in devices:
        if first(device['label'])['value'] == label:
            return device
    return None

def get_scene_by_label(label: str) -> Dict[str, Any]:
    """
    Helper function to get a scene by its label.

    :param label: Label of the scene.
    :return: Scene object, or None if not found.
    """
    query = '''
        query {{
            scenes {{
                id
                label {{
                    value
                    language
                }}
            }}
        }}
    '''
    response = requests.post(BCO_GRAPHQL_ENDPOINT, json={'query': query})
    scenes = response.json()['data']['scenes']
    for scene in scenes:
        if first(scene['label'])['value'] == label:
            return scene
    return None

def get_room_by_label(label: str) -> Dict[str, Any]:
    """
    Helper function to get a room by its label.

    :param label: Label of the room.
    :return: Room object, or None if not found.
    """
    query = '''
        query {{
            rooms {{
                id
                label {{
                    value
                    language
                }}
            }}
        }}
    '''
    response = requests.post(BCO_GRAPHQL_ENDPOINT, json={'query': query})
    rooms = response.json()['data']['rooms']
    for room in rooms:
        if first(room['label'])['value'] == label:
            return room
    return None

# Define request handler for activating a scene
class TurnDeviceOffHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("TurnDeviceOffIntent")(handler_input)

    def handle(self, handler_input):
        device_name = get_slot_value(handler_input, 'Device')
        device = get_device_by_label(device_name)
        if device:
            query = '''
                mutation {{
                    turnDeviceOff(deviceId: "{}") {{
                        success
                    }}
                }}
            '''.format(device['id'])
            response = requests.post(BCO_GRAPHQL_ENDPOINT, json={'query': query})
            success = response.json()['data']['turnDeviceOff']['success']
            if success:
                speech_text = _("The {device_name} is now off.").format(device_name=device_name)
            else:
                speech_text = _("I am sorry, but I was unable to turn the {device_name} off. Please try again later.").format(device_name=device_name)
        else:
            speech_text = _("I am sorry, but I do not recognize that device name. Please try again with a different device name.")
        return handler_input.response_builder.speak(speech_text).response

# Define request handler for activating scenes
class ActivateSceneHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ActivateSceneIntent")(handler_input)

    def handle(self, handler_input):
        scene_name = get_slot_value(handler_input, 'Scene')
        scene = get_scene_by_label(scene_name)
        if scene:
            query = '''
                mutation {{
                    activateScene(sceneId: "{}") {{
                        success
                    }}
                }}
            '''.format(scene['id'])
            response = requests.post(BCO_GRAPHQL_ENDPOINT, json={'query': query})
            success = response.json()['data']['activateScene']['success']
            if success:
                speech_text = _("The {scene_name} scene has been activated.").format(scene_name=scene_name)
            else:
                speech_text = _(
                    "I am sorry, but I was unable to activate the {scene_name} scene. Please try again later.").format(scene_name=scene_name)
        else:
            speech_text = _(
                "I am sorry, but I do not recognize that scene name. Please try again with a different scene name.")
        return handler_input.response_builder.speak(speech_text).response

# Define request handler for setting the room
class SetRoomHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SetRoomIntent")(handler_input)

    def handle(self, handler_input):
        room_name = get_slot_value(handler_input, 'Room')
        room = get_room_by_label(room_name)
        if room:
            query = '''
                mutation {{
                    setRoom(roomId: "{}") {{
                        success
                    }}
                }}
            '''.format(room['id'])
            response = requests.post(BCO_GRAPHQL_ENDPOINT, json={'query': query})
            success = response.json()['data']['setRoom']['success']
            if success:
                speech_text = _("The {room_name} room has been set.").format(room_name=room_name)
            else:
                speech_text = _("I am sorry, but I was unable to set the {room_name} room. Please try again later.")\
                    .format(room_name=room_name)
        else:
            speech_text = _(
                "I am sorry, but I do not recognize that room name. Please try again with a different room name.")
        return handler_input.response_builder.speak(speech_text).response

# Define response interceptor for setting language
class SetLanguageResponseInterceptor(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        locale = get_locale(handler_input)
        lang, encoding = locale.split('.')
        try:
            translation = gettext.translation('messages', localedir='locales', languages=[lang])
        except FileNotFoundError:
            translation = gettext.translation('messages', localedir='locales', languages=['en'])
            translation.install()
        return response

# Define function to get devices by label
def get_device_by_label(label):
    query = '''
        query {{
            devices {{
                id
                label {{
                    text
                    lang
                }}
            }}
        }}
    '''
    response = requests.post(BCO_GRAPHQL_ENDPOINT, json={'query': query})
    devices = response.json()['data']['devices']
    for device in devices:
        if device['label']['text'] == label and (not device['label']['lang'] or device['label']['lang'] == get_locale()):
            return device
    return None

# Define function to get scenes by label
def get_scene_by_label(label):
    query = '''
        query {{
            scenes {{
                id
                label {{
                    text
                    lang
                }}
            }}
        }}
    '''
    response = requests.post(BCO_GRAPHQL_ENDPOINT, json={'query': query})
    scenes = response.json()['data']['scenes']
    for scene in scenes:
        if scene['label']['text'] == label and (not scene['label']['lang'] or scene['label']['lang'] == get_locale()):
            return scene
    return None

# Define function to get rooms by label
def get_room_by_label(label):
    query = '''
        query {{
            rooms {{
                id
                label {{
                    text
                    lang
                }}
            }}
        }}
    '''
    response = requests.post(BCO_GRAPHQL_ENDPOINT, json={'query': query})
    rooms = response.json()['data']['rooms']
    for room in rooms:
        if room['label']['text'] == label and (not room['label']['lang'] or room['label']['lang'] == get_locale()):
            return room
    return None

# Define function to get the current locale of the user
def get_locale(handler_input):
    locale = handler_input.request_envelope.request.locale
    if not locale:
        locale = 'en-US'
    return locale
