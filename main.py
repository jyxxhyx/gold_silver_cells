from model.gold_silver_cells import GoldSilverCells
from output_handler.drawer import draw_solution


def main():
    grid = (9, 9)
    k = 3
    model = GoldSilverCells(grid, k)
    silver_cells, gold_cells = model.solve()
    draw_solution(grid, silver_cells, gold_cells,
                  f'data/output/{grid[0]}_{grid[1]}_{k}')
    return


if __name__ == '__main__':
    main()
