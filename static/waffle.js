const waffle_url = 'http://127.0.0.1:5000/waffle';
// when button with id "reset" is clicked, reset the board
$(document).ready(function () {
    $("#reset").click(function () {
        $("#solve").prop("disabled", true);
        for (var i = 0; i < 5; i++) {
            for (var j = 0; j < 5; j++) {
                let cell = $("#puzzle #" + i + j);
                if (cell.hasClass("unselectable")) {
                    continue;
                }
                cell.removeClass("selected");
                cell.removeClass("dark");
                cell.removeClass("light");
                cell.removeClass("none");
                if (((i == 0) && (j == 0)) || ((i == 0) && (j == 4)) || ((i == 4) && (j == 0)) || ((i == 4) && (j == 4)) || ((i == 2) && (j == 2))) {
                    cell.addClass("dark");
                } else {
                    cell.addClass("none");
                }
                cell.text("");
            }
        }
    });
});
// when button with id "solve" is clicked, send a POST request to the waffle_url server with the 5x5 grid as a JSON object
$(document).ready(function () {
    $("#solve").click(function () {
        display_solution_path([]);
        var grid = [];
        for (var i = 0; i < 5; i++) {
            var row = [];
            for (var j = 0; j < 5; j++) {
                let cell = $("#puzzle #" + i + j);
                let code = '';
                // if cell has class .dark, code = 'G'
                if (cell.hasClass('dark')) {
                    code = 'G';
                } else if (cell.hasClass('light')) {
                    code = 'L';
                } else if (cell.hasClass('none')) {
                    code = 'N';
                } else {
                    code = 'U';
                }
                row.push(cell.text() + code);
            }
            grid.push(row);
        }
        $.ajax({
            type: "POST",
            url: waffle_url,
            data: JSON.stringify(grid),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                let dgrid = data.grid;
                // on success, update the grid with the solution
                for (var i = 0; i < 5; i++) {
                    for (var j = 0; j < 5; j++) {
                        let cell = $("#solution #" + i + j);
                        if (cell.hasClass('unselectable')) {
                            continue;
                        }
                        cell.text(dgrid[i][j][0]);
                        cell.addClass('dark');
                        cell.removeClass('light');
                        cell.removeClass('none');
                    }
                }
                display_solution_path(data.path);
            },
            failure: function (errMsg) {
                alert(errMsg);
            }
        });
    });
});
function display_solution_path(path) {
    const pattern = 'XXXXXX X XXXXXXX X XXXXXX';
    // get the canvas element
    var canvas = document.getElementById("solutionpath");
    // get the 2d context of the canvas
    var ctx = canvas.getContext("2d");
    // clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // set canvas scaling to 1:1
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    // divide the canvas into ten equal parts. Inside each one, draw a 5x5 grid of gray
    // squares with a 1 pixel separation between them. first third and fifth rows have five squares,
    // second and fourth rows have three squares in the pattern X X X.
    let solution_step_separation = 3;
    let solution_step_solution_size = Math.floor((canvas.width - 9 * solution_step_separation) / 10);
    let letter_separation = 1;
    let letter_grid_size = Math.floor((solution_step_solution_size - 4 * letter_separation) / 5);

    // log all these values
    console.log("solution_step_separation: " + solution_step_separation);
    console.log("solution_step_solution_size: " + solution_step_solution_size);
    console.log("letter_separation: " + letter_separation);
    console.log("letter_grid_size: " + letter_grid_size);
    // and the canvas size
    console.log("canvas.width: " + canvas.width);
    console.log("canvas.height: " + canvas.height);

    // draw as many of these squares as there are steps in the path
    for (var i = 0; i < path.length; i++) {
        let step = path[i];
        let x = i * (solution_step_solution_size + solution_step_separation);
        ctx.fillStyle = "lightgray";
        for (var pos = 0; pos < pattern.length; pos++) {
            if (pattern[pos] == 'X') {
                let lx = x + (pos % 5) * (letter_grid_size + letter_separation);
                let ly = Math.floor(pos / 5) * (letter_grid_size + letter_separation);
                ctx.fillStyle = "lightgray";
                ctx.fillRect(lx, ly, letter_grid_size, letter_grid_size);

                // Function to draw the letter in the square with green background and white text
                function drawLetter(letter, pos, stepPos) {
                    if (stepPos == pos) {
                        ctx.fillStyle = "green";
                        ctx.fillRect(lx, ly, letter_grid_size, letter_grid_size);
                        ctx.fillStyle = "white";
                        ctx.font = "6pt Arial";
                        ctx.textAlign = "center";
                        ctx.textBaseline = "middle";
                        ctx.fillText(letter, lx + letter_grid_size / 2, ly + letter_grid_size / 2);
                    }
                }

                // Draw the letter for step[0] and step[1]
                drawLetter(step[0], pos, step[1]);

                // Draw the letter for step[2] and step[3]
                drawLetter(step[2], pos, step[3]);
            }
        }
    }

}

function cycle_cell(cell) {
    // if cell has class .dark, remove .dark and add .light
    if (cell.hasClass('dark')) {
        cell.removeClass('dark');
        cell.addClass('light');
        // if cell has class .light, remove .light and add .none
    } else if (cell.hasClass('light')) {
        cell.removeClass('light');
        cell.addClass('none');
        // if cell has class .none, remove .none and add .dark
    } else if (cell.hasClass('none')) {
        cell.removeClass('none');
        cell.addClass('dark');
    }
}
// jquery cycle background color through classes .dark, .light and .none when user clicks on the cell
$(document).ready(function () {
    $("#puzzle td").click(function () {
        // if cell has class .unselectable ignore click
        if ($(this).hasClass("unselectable")) {
            return;
        }
        // select cell if it does not have selected class
        if (!$(this).hasClass("selected")) {
            // remove selected class from all cells
            $("#puzzle td").removeClass("selected");
            $(this).addClass("selected");
        } else {
            cycle_cell($(this));
        }
    });
});
// jquery when a user types a key and a cell is selected, set the contents of that cell to the upper case key
$(document).ready(function () {
    $(document).keydown(function (event) {
        // if event is tab, cycle through the cells
        if (event.which == 9) {
            event.preventDefault();
            // "puzzle td" signals the selected cell. If no cell is selected, select the first cell.
            // if the cell is the last cell on the row, select the first cell on the next row.
            // if the cell is the last cell on the last row, select the first cell on the first row.
            // otherwise select the next cell on the same row.

            let selected = $(".selected");
            if (selected.length == 0) {
                $("#puzzle td").first().addClass("selected");
            } else {
                let id = selected.attr("id");
                let row = parseInt(id[0]);
                let col = parseInt(id[1]);
                // remove selected from all cells
                $("#puzzle td").removeClass("selected");
                if (col == 4) {
                    if (row == 4) {
                        $("#puzzle td").first().addClass("selected");
                    } else {
                        $("#puzzle #" + (row + 1) + "0").addClass("selected");
                    }
                } else {
                    // if the next cell is unselectable, select the next cell after that
                    if ($("#puzzle #" + row + (col + 1)).hasClass("unselectable")) {
                        $("#puzzle #" + row + (col + 2)).addClass("selected");
                    } else {
                        $("#puzzle #" + row + (col + 1)).addClass("selected");
                    }
                }
            }
            return;
        }
        let disabled = false;
        $("#puzzle td").each(function () {
            if ($(this).hasClass("selected")) {
                console.log(event.key);
                console.log(event.which);
                // if keystroke is non-alphabetic, delete contents of cell
                if ((event.which >= 65 && event.which <= 90) || (event.which >= 97 && event.which <= 122)) {
                    let key = event.key.toUpperCase();
                    if (key == $(this).text()) {
                        cycle_cell($(this));
                    } else {
                        $(this).text(key);
                    }
                } else {
                    $(this).text("");
                }
            }
            if (!$(this).hasClass("unselectable")) {
                if ($(this).text() == "") {
                    disabled = true;
                }
            }
        });
        $("#solve").prop("disabled", disabled);
    });
});
