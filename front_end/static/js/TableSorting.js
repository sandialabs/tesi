// Adds column sorting capability to an HTML table.

export function AddTableSorting(tables) {
    const sortCaretUp = ' <i class="bi bi-caret-up-fill"></i>';
    const sortCaretDown = ' <i class="bi bi-caret-down-fill"></i>';

    tables.each(function( index ) {
        const headings = $( this ).find('th.sortable');

        headings.each(function( index ) {
            $( this ).append(' <span class="sort-caret" data-order="0">' + sortCaretDown + '</span>');
        });
      });

      $('th.sortable').on( "click", function() {
        let caretContainer = $(this).children('.sort-caret').eq(0);
        let caret = caretContainer.data('order') ? sortCaretUp : sortCaretDown;
        caretContainer.html(caret);
        caretContainer.data('order', ! caretContainer.data('order'));

        $('.sort-caret').html();

        var table = $(this).parents('table').eq(0)
        var rows = table.find('tr:not(thead tr)').toArray().sort(comparer($(this).index()))
        this.asc = !this.asc
        if (!this.asc){rows = rows.reverse()}
        for (var i = 0; i < rows.length; i++){table.append(rows[i])}
      });
} // End function AddTableSorting()

function comparer(index) {
    return function(a, b) {
        var valA = getCellValue(a, index), valB = getCellValue(b, index)
        return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB)
    }
}
function getCellValue(row, index){ return $(row).children('td').eq(index).text() }