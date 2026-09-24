// Adds  Column Chooser capability to an HTML table.

export function ColumnSelector(tableID, selectorID) {
    loadColumnNames(tableID, selectorID);
    const $selectorButton = $('#' + selectorID);
    const tableUID = window.location.href + tableID + '_columnPreferences';
  
    //const $columnSelector = $('.columnSelector');
    const $columnSelector = $selectorButton.children('.columnSelector');
    const $checkboxes = $columnSelector.find('input[type="checkbox"]');
    const numColumns = $columnSelector.children().length;
    const columnsShown = Array(numColumns).fill(true);
    console.log("Columns Shown", columnsShown);
    
    
    // Load saved column preferences from local storage
    const savedPreferences = JSON.parse(localStorage.getItem(tableUID)) || columnsShown;
    console.log("Stored", JSON.parse(localStorage.getItem(tableUID)));
    
    $checkboxes.each(function (index) {
      $(this).prop('checked', savedPreferences[index]);
      toggleColumnVisibility(tableID, index, savedPreferences[index], numColumns);
    });
  
    // Add event listener to checkboxes
    $columnSelector.on('change', 'input[type="checkbox"]', function () {
      const $checkbox = $(this);
      const columnIndex = parseInt($checkbox.val());
      const isChecked = $checkbox.is(':checked');
      toggleColumnVisibility(tableID, columnIndex, isChecked, numColumns);
  
      // Save preferences to local storage
      const preferences = $checkboxes.map(function () {
        return $(this).is(':checked');
      }).get();
      localStorage.setItem(tableUID, JSON.stringify(preferences));
    });
  
    // Dropdown functionality
    $selectorButton.on('click', function () {
      $columnSelector.toggleClass('show');
    });
  
    // Close the dropdown if the user clicks outside of it
    $(window).on('click', function (event) {
      if (!$(event.target).closest('.dropdown').length) {
        $columnSelector.removeClass('show');
      }
    });
} // End Function ColumnSelector()

function loadColumnNames(tableID, selectorID) {
    const $table = $('#' + tableID);
    const $selectorButton = $('#' + selectorID);
    const $columnSelector = $selectorButton.children('.columnSelector');
  
    const headerRow = $table.children('thead').children('tr')[0];
    
    $.each($(headerRow).children(), function (i, item) {
      // <label><input type="checkbox" value="0" checked> Column 1</label>
      const label = document.createElement("label");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.id = i;
      checkbox.value = i;
      checkbox.name = "columnSelection";
      checkbox.checked = true;
      const textContent = document.createTextNode($(item).text());
  
      label.appendChild(checkbox);
      label.appendChild(textContent);
  
      $columnSelector.append(
        label
      );
    });
  
  } // End Function loadColumnNames()
  
  function toggleColumnVisibility(tableID, index, isVisible, numColumns) {
    // console.log("number of columns", numColumns);
    // console.log(index, isVisible);
    const $table = $('#' + tableID);
    const $columns = $table.find('th, td');
    $columns.each(function (cellIndex) {
      if (cellIndex % numColumns === index) {
        $(this).toggleClass('hidden', !isVisible);
      }
    });
  } // End Function toggleColumnVisibility()