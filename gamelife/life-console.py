import curses
import time
import argparse


from life import GameOfLife
from ui import UI


class Console(UI):


	def __init__(self, life: GameOfLife) -> None:
		super().__init__(life)

	def draw_borders(self, screen) -> None:
		screen.border(0)
		pass


	def draw_grid(self, screen) -> None:
		for row_ind, row in enumerate(self.life.curr_generation):
			for col_ind, cell in enumerate(row):
				if cell != 0:
					try:
						screen.addstr(row_ind + 1, col_ind + 1, '*')
					except Exception as e:
						print(row_ind, col_ind)


	def run(self) -> None:
		screen = curses.initscr()
		curses.curs_set(0)

		running = True
		while running:
			screen.clear()
			self.draw_borders(screen)
			self.draw_grid(screen)
			self.life.step()
			if self.life.is_max_generations_exceed:
				running = False
			screen.refresh()
			time.sleep(2/60)

		screen.getch()
		curses.endwin()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Console Game of life')
	parser.add_argument('--rows', type=int, default=80, help='Number of rows')
	parser.add_argument('--cols', type=int, default=30, help='Number of columns')
	parser.add_argument('--max-generations', default=100, type=int, help='Maximum generation count')
	args = parser.parse_args()
	game = GameOfLife((args.cols, args.rows), max_generations=args.max_generations)
	console = Console(game)
	console.run()	