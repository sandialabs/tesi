$(document).ready(function () {
    keepAlive();
    setInterval(keepAlive, 240000);
});

// For each for field marked as required, add a red asterisk to its label (if it has an assigned label).
document.addEventListener("DOMContentLoaded", function() {
    const requiredInputs = document.querySelectorAll('input[required], textarea[required], select[required]');
    requiredInputs.forEach(input => {
        const label = document.querySelector(`label[for="${input.id}"]`);
        if (label) {
            label.innerHTML += ' <span style="color: red;">*</span>';
        }
    });
});

function keepAlive() {
    let package = {};
    package["is-window-open"] = "Window Open";

    $.ajax({
        url: "/is_open",
        type: "POST",
        //dataType: "json",
        encode: true,
        data: package,
        success: function(data){
          //console.log(data);
          return null;
        }
    });
  }

// Function for filtering rows out of a table based on a filter input
function filterRows($rows, filters, $input) {
    console.log("Input: " + $input.val());
    var col = $input.parent().index()
    filters[col] = $input.val().trim().replace(/ +/g, ' ').toLowerCase().split(",").filter(l => l.length);
    $rows.show();
    if(filters.some(f => f.length)) {
        $rows.filter(function() {
            var texts = $input.children().map((i, td) => $(td).text().replace(/\s+/g, ' ').toLowerCase()).get();
            return !texts.every((t, col) => {
                return filters[col].length == 0 || filters[col].some((f, i) => t.indexOf(f) >= 0);
            })
        }).hide();
    }
}