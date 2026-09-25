import argparse
from app.services.collection_service import collect_all


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect MOLIT apartment sale transactions")
    parser.add_argument("--months", type=int, default=24)
    args = parser.parse_args()
    for _progress, message in collect_all(args.months):
        print(message)


if __name__ == "__main__":
    main()
