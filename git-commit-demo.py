import os
import subprocess
from openai import OpenAI

def get_git_diff():
    """Gets the staged changes from git."""
    try:
        diff_output = subprocess.check_output(["git", "diff", "--staged"], text=True)
        return diff_output
    except subprocess.CalledProcessError:
        return None  # No staged changes

def generate_commit_message(diff, api_key):
    client = OpenAI(api_key=api_key)

    promptMessage = f"""Generate a concise and informative commit message based on the following git diff:\n\n{diff}\n\nCommit message:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user", 
                    "content": promptMessage
                }
            ],
            stream=True,
        )

        for message in response:
            if message.choices[0].delta.content is not None:
                print(message.choices[0], end="")

            return message

    except ValueError as e:
        print(f"Error communicating with OpenAI: {e}")
        return None

def commit_changes(message):
    """Commits the staged changes with the generated message."""
    try:
        subprocess.run(["git", "commit", "-m", message], check=True)
        print("Commit successful!")
    except subprocess.CalledProcessError as e:
        print(f"Error committing: {e}")

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return

    diff = get_git_diff()
    if not diff:
        print("No staged changes to commit.")
        return

    message = generate_commit_message(diff, api_key)
    if message:
        print(f"Generated commit message:\n{message}")
        user_input = input("Use this message? (y/n): ").lower()
        if user_input == 'y':
            commit_changes(message)
        else:
            custom_message = input("Enter a custom commit message: ")
            if custom_message:
                commit_changes(custom_message)
            else:
                print("Commit aborted.")
    else:
        print("Failed to generate commit message.")

main()