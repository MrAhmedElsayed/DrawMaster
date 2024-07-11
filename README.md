# DrawMaster

DrawMaster is a Python-based drawing application built using Tkinter. It allows users to draw, move, and copy points and lines with ease. The application also features snapping functionality to line ends or points and supports importing points from Excel files.

## Features

- **Drawing Points and Lines:** Easily draw points and lines on the canvas.
- **Snapping:** Snap to the nearest point or line end within a specified distance.
- **Move and Copy:** Select and move or copy points and lines.
- **Undo and Redo:** Undo and redo actions for improved usability.
- **Import from Excel:** Load points from an Excel file and display them on the canvas.

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/MrAhmedElsayed/DrawMaster.git
    cd DrawMaster
    ```

2. **Install Dependencies:**

    Ensure you have Python 3.x installed. Install required packages using pip:

    ```bash
    pip install pandas
    ```

## Usage

Run the application using the following command:

```bash
python drawmaster.py
```

### Drawing

- **Draw Point:** Click the "Draw Point" button and then click on the canvas to draw a point.
- **Draw Line:** Click the "Draw Line" button and then click two points on the canvas to draw a line.
- **Snap to Point/Line End:** Move the cursor near a point or line end to see the snap indicator.

### Modifying

- **Select Item:** Click the "Select" button and then click on a point or line to select it. Selected items will change color.
- **Move Item:** Click the "Move" button, select an item, and drag it to a new position.
- **Copy Item:** Select an item and click the "Copy" button to duplicate it.
- **Delete Item:** Select an item and click the "Delete" button to remove it.

### Undo/Redo

- **Undo:** Click the "Undo" button to revert the last action.
- **Redo:** Click the "Redo" button to reapply the last undone action.

### Import Points from Excel

1. Click the "Upload Excel" button.
2. Select an Excel file (.xlsx) containing points with columns named `x` and `y`.
3. The points will be loaded and displayed on the canvas.

## Example Excel File Format

| x   | y   |
| --- | --- |
| 100 | 150 |
| 200 | 250 |
| 300 | 350 |

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.


## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
