from ui.prompts import BEGINNER_PROMPT
from clioraOps_cli.utils.logger import log_learning_session


def handle_beginner(topic, user_input, ai_client):
    """
    Handles a beginner learning session using the AI client and returns the response.
    """
    prompt = BEGINNER_PROMPT.format(
        topic=topic,
        input=user_input
    )

    response = ai_client.chat(prompt)

    # Log the beginner session
    log_learning_session(
        topic=topic,
        mode="beginner",
        user_input=user_input,
        ai_output=response.content
    )

    return response.content


def handle_learn(topic, mode, user_input, ai_response, visual_output="", review_output=""):
    """
    Handles a learning session for any mode (beginner/architect) and logs it.
    """
    # Log everything
    log_learning_session(
        topic=topic,
        mode=mode,
        user_input=user_input,
        ai_output=ai_response,
        visual_output=visual_output,
        review_output=review_output
    )

    # Return combined output to CLI
    combined_output = f"{ai_response}\n\n{visual_output}\n\n{review_output}"
    return combined_output
