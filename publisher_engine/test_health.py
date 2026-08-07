from moodle_client import MoodleClient

# ==========================================================
# Test Moodle Health
# ==========================================================

def main():

    print("=" * 60)
    print("RONO CURRICULUM BUILDER")
    print("MOODLE HEALTH TEST")
    print("=" * 60)

    try:

        client = MoodleClient()

        result = client.health()

        print("\nSUCCESS\n")

        print(result)

    except Exception as e:

        print("\nFAILED\n")

        print(str(e))


if __name__ == "__main__":

    main()