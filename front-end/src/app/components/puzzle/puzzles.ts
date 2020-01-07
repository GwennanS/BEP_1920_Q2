import { Puzzle } from "./puzzle";

export class Puzzles {
  all: Map<string, Puzzle>;

  constructor() {
    this.all = new Map<string, Puzzle>();
  }

  /**
   * Receives list of json objects (keys id and status)
   */
  updatePuzzles(jsonData) {
    for (const object of jsonData) {
      if (!this.all.has(object.id)) {
        this.all.set(object.id, new Puzzle(object.id, object.description));
      }
      this.all.get(object.id).updateStatus(object.status);
    }
  }

  /**
   * Set the puzzles in the list with their id and description
   * @param id of new puzzle
   * @param description of new puzzle
   */
  addPuzzle(id: string, description: string) {
    this.all.set(id, new Puzzle(id, description));
  }
}
