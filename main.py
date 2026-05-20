from core.main_controller import MainController
from utils.single_instance import SingleInstance


def main():
    with SingleInstance() as instance:
        if not instance.acquired:
            return

        controller = MainController("config/config.yaml")
        controller.run()


if __name__ == "__main__":
    main()