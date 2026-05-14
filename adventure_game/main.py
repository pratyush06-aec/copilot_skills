from colorama import init as colorama_init

from game.engine import GameEngine
from ui.display import UIRenderer
from story.nodes import STORY_NODES


def main() -> None:
    colorama_init(autoreset=True)
    renderer = UIRenderer()
    engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
    engine.run()


if __name__ == "__main__":
    main()
