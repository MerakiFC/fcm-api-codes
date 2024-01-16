
def main() -> None:
    print(f'This is the motionAlert.py main definition')

def test_printer(payload: dict):
    print(f'This is the motionAlert.py test_printer function')
    print(payload['deviceModel'])
    return


if __name__ == "__main__":
    main()