import { ColumnSelector } from "./ColumnSelector.js";
import { AddTableSorting } from "./TableSorting.js";

$(document).ready(function () {

  var $rows = $('#products-table tbody tr');
  var filters = [];
  var $inputs = $("#products-table .columnFilter input");
  $inputs.each(function () {
    filters.push([]);
  });

  $inputs.keyup(function () {
    var col = $(this).parent().index()
    filters[col] = $(this).val().trim().replace(/ +/g, ' ').toLowerCase().split(",").filter(l => l.length);
    $rows.show();
    if (filters.some(f => f.length)) {
      $rows.filter(function () {
        var texts = $(this).children().map((i, td) => $(td).text().replace(/\s+/g, ' ').toLowerCase()).get();
        return !texts.every((t, col) => {
          return filters[col].length == 0 || filters[col].some((f, i) => t.indexOf(f) >= 0);
        })
      }).hide();
    }
    //if($rows.filter(":visible").length===0) alert("no")
  });

  $("#AddProduct").click(function () {
    $("#productForm").attr("method", "post");
    $("#productForm").trigger("reset");
    $('#productID, label[for=productID]').hide();

    editMode();
  });


  $(".editIcon").click(function () {
    var intID = $(this).data("item_id");

    $('#productID, label[for=productID]').show();

    $.ajax({
      url: "/products/product_details/" + intID,
      type: "GET",
      dataType: "json",
      success: function (data) {
        if (typeof (data) != 'undefined' && data != null && typeof (data.product_id) != 'undefined') {
          $('#productID').val(data.product_id ?? '');
          $('#facility_product_id').val(data.facility_product_id ?? '');
          $('#productName').val(data.name);
          $('#cas_numbers').val(data.cas_numbers);
          $('#physical_state_id').val(data.physical_state_id);
          $('#concerns').attr('checked', data.concerns ? true : false);
          $('#hazard_code').val(data.hazard_codes);
          $('#other_issues').val(data.other_issues);
          $('#packaging').val(data.packaging);
          $('#size').val(data.size);
        }
      }
    });

    editMode(intID);
  });

  $(".cancel").click(function () {
    $("#table-section").show();
    $("#form-section").hide();
    $("#AddProduct").show();
    $('.dropdown').show();
  });


  $(".deleteIcon").click(function () {
    var intID = $(this).data("item_id") ?? null;

    var confirmation = confirm("Are you sure you want to delete this item? (ID: " + intID + ")");

    if (confirmation) {
      let id_package = {};
      id_package['productID'] = intID;
      console.table(id_package);

      $.ajax({
        url: "/products/product_database",
        type: "DELETE",
        dataType: "json",
        encode: true,
        data: id_package,
        success: function (data) {
          console.log(data);
          window.location.reload(true);
        }
      });
    }
  });


  $("#cas_numbers").change(function () {
    if ($(this).val() == "" || $(this).val() == null) return null;

    $.ajax({
      url: "/products/cas_hazards/" + $(this).val(),
      type: "GET",
      dataType: "json",
      success: function (data) {
        if (typeof (data) != 'undefined' && data != null && typeof (data.cas_number) != 'undefined') {
          $('#concerns').attr('checked', true);
          $('#hazard_code').val(data.hazard_code);
        }
        else $('#concerns').attr('checked', false);
      }
    });
  });


  $("#hazard_code").change(function () {
    $.ajax({
      url: "/products/ghs_hazards/" + $(this).val(),
      type: "GET",
      dataType: "json",
      success: function (data) {
        console.table(data);
        if (typeof (data) != 'undefined' && data != null && typeof (data.hazard_code) != 'undefined') {
          $('#concerns').attr('checked', true);
        }
        else $('#concerns').attr('checked', false);
      }
    });
  });

  ColumnSelector("products-table", "selector");
  AddTableSorting($('.database-table'));

}); // End document.ready



function editMode(intID = null) {
  $('#concerns').attr('checked', false);
  $("#AddProduct").hide();
  $("#table-section").hide();
  $("#form-section").show();
  $('.dropdown').hide();
}