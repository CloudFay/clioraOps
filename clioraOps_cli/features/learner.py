from ui.prompts import BEGINNER_PROMPT
from clioraops_cli.utils.logger import log_learning_session


def handle_beginner(topic, user_input, copilot_client):
    """
    Handles a beginner learning session using Copilot and returns the response.
    """
    prompt = BEGINNER_PROMPT.format(
        topic=topic,
        input=user_input
    )

    response = copilot_client.run(prompt)

    # Log the beginner session
    log_learning_session(
        topic=topic,
        mode="beginner",
        user_input=user_input,
        copilot_output=response
    )

    return response


def handle_learn(topic, mode, user_input, copilot_response, visual_output="", review_output=""):
    """
    Handles a learning session for any mode (beginner/architect) and logs it.
    """
    # Log everything
    log_learning_session(
        topic=topic,
        mode=mode,
        user_input=user_input,
        copilot_output=copilot_response,
        visual_output=visual_output,
        review_output=review_output
    )

    # Return combined output to CLI
    combined_output = f"{copilot_response}\n\n{visual_output}\n\n{review_output}"
    return combined_output
