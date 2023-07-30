import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

import requests
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "What's up? Ask me when's the next f1 race and I'll tell you how much time until the next Formula 1 Grand Prix"
      
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class NextRaceIntentHandler(AbstractRequestHandler):
    """Handler for Next Race Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("NextRaceIntent")(handler_input)

    def handle(self, handler_input):
        url = 'http://ergast.com/api/f1/current.json'
        response = requests.get(url)
        data = response.json()

        races = data['MRData']['RaceTable']['Races']

        current_datetime = datetime.now()

        next_race_info = {}

        for race in races:
            race_date_str = race['date']
            race_time_str = race['time']
            race_datetime_str = race_date_str + ' ' + race_time_str[:-1]
            race_datetime = datetime.strptime(race_datetime_str, '%Y-%m-%d %H:%M:%S')

            if race_datetime > current_datetime:
                difference = race_datetime - current_datetime
                days = difference.days
                hours, remainder = divmod(difference.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                next_race_info = {
                    'name': race['raceName'],
                    'datetime': race_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'location': race['Circuit']['Location']['locality'] + ', ' + race['Circuit']['Location']['country'],
                    'days': str(days) + ' days',
                    'hours': str(hours) + ' hours',
                    'minutes': str(minutes) + ' minutes',
                    'seconds': str(seconds) + ' seconds'
                }
                
                break
            
        speak_output = "The next race is  the " + next_race_info['name'] + " in " + next_race_info['location'] + ". It takes place in " + next_race_info['days'] + ", " + next_race_info['hours'] + ", " + next_race_info['minutes'] + ", and " + next_race_info['seconds'] + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )



sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(NextRaceIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
