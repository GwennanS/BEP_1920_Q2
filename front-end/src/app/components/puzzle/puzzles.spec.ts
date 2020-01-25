import { Puzzles } from "./puzzles";

describe("Puzzles", () => {
  let puzzles: Puzzles;
  let jsonData: JSON;

  beforeEach(() => {
    jsonData = JSON.parse(`[{
          "id": "Door open",
          "status": true,
           "description": "The door opens"
        }]
    `);
    puzzles = new Puzzles();
  });

  it("should create", () => {
    expect(puzzles).toBeTruthy();
  });

  it("should set status", () => {
    expect(puzzles.all.size).toBe(0);
    puzzles.updatePuzzles(jsonData);
    expect(puzzles.all.size).toBe(1);
    puzzles.updatePuzzles(jsonData);
    expect(puzzles.all.get("Door open").status).toBe(true);
  });

  it("should add puzzle", () => {
    const newMap = new Map<string, string>();
    expect(puzzles.all.size).toBe(0);
    puzzles.addPuzzle("my rule", "this my rule");
    expect(puzzles.all.size).toBe(1);
    expect(puzzles.all.get("my rule").status).toBe(false);
  });
});
