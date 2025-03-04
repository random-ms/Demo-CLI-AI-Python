import os
import subprocess
import openai

def get_git_diff():
    """Gets the staged changes from git."""
    try:
        diff_output = subprocess.check_output(["git", "diff", "--staged"], text=True)
        return diff_output
    except subprocess.CalledProcessError:
        return None  # No staged changes

def generate_commit_message(diff, api_key):
    """Generates a commit message using OpenAI."""
    openai.api_key = api_key

    promptMessage = f"""Generate a concise and informative commit message based on the following git diff:\n\n{diff}\n\nCommit message: """

    try:
        response = openai.Completion.create(
            engine="gpt-4o-mini",
            prompt=promptMessage,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5, # Adjust for creativity. 0 is more deterministic
        )
        message = response.choices[0].text.strip()
        return message
    except openai.error.OpenAIError as e:
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
    api_key = os.environ.get("OPENAI_API_KEY") # Get API key from environment variable
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

if __name__ == "__main__":
    main()