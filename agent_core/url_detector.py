import re

def detect_urls(text: str) -> list[str]:
    """
    Detects and returns all URLs present in the input text.

    Args:
        text: The input string to search for URLs.

    Returns:
        A list of URLs found in the text.
    """
    # Regex to find URLs:
    # http[s]?://             - matches http:// or https://
    # (?:[a-zA-Z]|[0-9]|      - matches letters, numbers, or
    #  [$-_@.&+]|[!*\\(\\),]|   - special characters $-_@.&+ or !*(),
    #  (?:%[0-9a-fA-F][0-9a-fA-F]))+ - or percent-encoded characters
    # This regex is a common pattern for matching URLs.
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls

def confirm_urls(urls: list[str]) -> bool:
    """
    Prints the detected URLs and prompts the user for confirmation.

    Args:
        urls: A list of URLs to be confirmed.

    Returns:
        True if the user confirms, False otherwise.
    """
    if not urls:
        return False # No URLs to confirm

    print("Detected URLs:")
    for i, url in enumerate(urls):
        print(f"{i + 1}. {url}")

    # Prompt user for confirmation.
    while True:
        user_input = input("Do you want to proceed with these URLs? (yes/no): ").strip().lower()
        if user_input == "yes":
            return True
        elif user_input == "no":
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
