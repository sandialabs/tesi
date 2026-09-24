import { ColumnSelector } from "./ColumnSelector.js";
import { AddTableSorting } from "./TableSorting.js";

$(document).ready(function () {

  var $rows = $('#customers-table tbody tr');
  var filters = [];
  var $inputs = $("#customers-table .columnFilter input");
  let addressEditStatus, bankEditStatus = false;

  $inputs.each(function () {
    filters.push([]);
  });

  // Code for column filters on the Customers table.
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
  });


  $("#AddCustomer").click(function () {
    // var elementID = "customer_address_1";
    // var textarea = document.createElement("textarea");
    // textarea.name = elementID;
    // textarea.type = "text";
    // textarea.classList = "form-control customerAddress";
    // textarea.setAttribute("aria-label", "Address");
    // $(textarea).prop('required',true);
    // textarea.id = elementID;
    // $("#customer_addresses_block").append(textarea);

    $("#customerForm").attr("method", "post");
    $("#customerForm").trigger("reset");
    $('#customer_id, label[for=customer_id]').hide();

    editMode();
  });


  $(".editIcon").click(function () {
    var intID = $(this).data("item_id");

    $('#customer_id, label[for=customer_id]').show();

    $.ajax({
      url: "/customers/customer_details/" + intID,
      type: "GET",
      dataType: "json",
      success: function (data) {
        if (typeof (data) != 'undefined' && data != null && typeof (data.customer_id) != 'undefined') {
          $('#customer_id').val(data.customer_id ?? '');
          $('#facility_customer_id').val(data.facility_customer_id ?? '');
          $('#customer_name').val(data.customer_name);
          $('#phone_number').val(data.phone_number);
          $('#poc_name').val(data.poc_name);
          $('#poc_email').val(data.poc_email);
          $('#hq_country').val(data.hq_country);
          $('#address_proof_accept').val(data.address_proof_accept);
          $('#poc_dob').val(data.poc_dob);
          $('#poc_nationality').val(data.poc_nationality);
          $('#poc_parent_name').val(data.poc_parent_name);
          $('#business_num').val(data.business_num);
          $('#business_type').val(data.business_type);
          // $('#trusted_customer').val(data.trusted_customer);
          $('#trusted_customer').attr("checked", data.trusted_customer ? true : false);
          $('#verification_date').val(data.verification_date);
          $('#address_proof_type_id').val(data.address_proof_type_id);
          $('#third_party_ref_name').val(data.third_party_ref_name);
          $('#third_party_contact_info').val(data.third_party_contact_info);
          $('#payment_method_id').val(data.payment_method_id);
          $('#order_frequency').val(data.order_frequency);
          $('#sanctioned').val(data.sanctioned);
          $("#btnAddAddress, #btnAddBank").toggle();
        }
      }
    });

    $.ajax({
      url: "/customer/addresses/" + intID,
      type: "GET",
      dataType: "json",
      success: function (data) {
        if (typeof (data) != 'undefined' && data != null && typeof (data[0].customer_address_id) != 'undefined') {
          $('#customer_address_1').remove(); // Remove original field used for new entries but which is left empty.
          $.each(data, function (index, object) {
            createdAddressField(index, object);
          });
        }
      }
    });


    $.ajax({
      url: "/customer/banks/" + intID,
      type: "GET",
      dataType: "json",
      success: function (data) {
        if (typeof (data) != 'undefined' && data != null && typeof (data[0].customer_bank_id) != 'undefined') {

          $.each(data, function (index, object) {
            var $newBlock = $('#bank_row').clone(); // Copy template row containing fields
            $newBlock.attr("id", "bank_row_" + index);

            var $bank_name = $newBlock.find('input');
            $bank_name.val(object.bank_name);
            $bank_name.attr("aria-label", "Bank Name " + (index + 1));
            $bank_name.attr("name", "bank_name_" + index);
            $bank_name.data("customer_bank_id", object.customer_bank_id);
            $bank_name.addClass("bankAddress");

            var $bank_address = $newBlock.find('textarea');
            $bank_address.val(object.bank_address);
            $bank_address.attr("aria-label", "Bank Address " + index);
            $bank_address.attr("name", "bank_address_" + index);
            $bank_address.data("customer_bank_id", object.customer_bank_id);
            $bank_address.addClass("bankAddress");

            $('#banks_block').append($newBlock);

            var id_field = document.createElement("input");
            id_field.value = object.customer_bank_id;
            id_field.type = "hidden";
            id_field.name = "customer_bank_id";
            id_field.id = "address_id_" + index;

            $("#banks_block").append(id_field);

            // Append customer_bank_id as hidden field

            if (typeof (object.sanctioned) != "undefined" && object.sanctioned == true) {
              $bank_name.toggleClass("sanctioned");
              $bank_address.toggleClass("sanctioned");
              $bank_address.after("<p class='sanctioned_warning'>Sanctioned Entity</p>");
            }
          });

          $('#bank_row').remove(); // Remove original fields used as a template but which are left empty.

        }
      }
    });


    editMode(intID);
  });

  $(".cancel").click(function () {
    $("#table-section").show();
    $("#form-section").hide();
    $("#AddCustomer").show();
    $("#selector").show();
  });

  $(".deleteIcon").click(function () {
    var intID = $(this).data("item_id") ?? null;

    var confirmation = confirm("Are you sure you want to delete this item? (ID: " + intID + ")");
    let id_package = {};
    id_package['customer_id'] = intID;

    if (confirmation) {
      $.ajax({
        url: "/customers/customer_database",
        type: "DELETE",
        dataType: "json",
        data: id_package,
        success: function (data) {
          window.location.reload();
        }
      });
    }
  });


  $("#btnAddAddress").click(function () {
    $("#addressFormDiv, #cancelAddress, #submitAddress").show();
    $("#btnAddAddress").hide();
    addressEditStatus = false;
  });

  $("#cancelAddress").click(function () {
    $("#addressFormDiv, #cancelAddress, #submitAddress").hide();
    $("#btnAddAddress").show();
    addressEditStatus = false;
  });

  $('#customer_addresses_block').delegate(".customerAddress", "change", function () {
    $("#btnAddAddress").hide();
    addressEditStatus = true;

    if ($('#customer_id').val() == '' || $('#customer_id').val() == null) {
      // check sanction only
      search_sanctions(false, $('#customer_name').val(), $('#address_0').val());
    }
    else {
      $("#cancelAddress, #submitAddress").show();
      if (confirm("Save change to address?") == true) {
        let address_id = $(this).data("customer_address_id");
        let form_data = "new_address=" + encodeURI($(this).val());

        submitCustomerAddress(form_data, address_id);
      }
    }
  });


  $("#btnAddBank").click(function () {
    $("#bankFormDiv, #cancelBankAddress, #submitBankAddress").show();
    $("#btnAddBank").hide();
    bankEditStatus = false;
  });

  $("#cancelBankAddress").click(function () {
    $("#bankFormDiv, #cancelBankAddress, #submitBankAddress").hide();
    $("#btnAddBank").show();
    bankEditStatus = false;
  });

  $('#banks_block').delegate(".bankAddress", "change", function () {
    $("#cancelBankAddress, #submitBankAddress").show();
    $("#btnAddBank").hide();
    bankEditStatus = true;

    let bankName = $(this).parent().parent().children('.col').children('input').val();
    let bankAddress = $(this).parent().parent().children('.col').children('textarea').val();

    if ($('#customer_id').val() == '' || $('#customer_id').val() == null) {
      // check sanction only
      search_sanctions(true, bankName, bankAddress);
    }
    else {
      if (confirm("Save change to bank?") == true) {
        let address_id = $(this).data("customer_bank_id");
        let form_data = "bank_name=" + encodeURI(bankName);
        form_data += "&bank_address=" + encodeURI(bankAddress);
        submitBankAddress(form_data, address_id);
      }
    }

  });


  $("#customerForm").on("submit", function (event) {
    event.preventDefault();

    // const formObject = new FormData($(this)[0]);
    // const form = document.getElementById("form");
    // var formObject = new FormData("#customerForm");
    // $('.form-switch').each(function (index) {
    //   let switchInput = $(this).children('input')[0];
    //   if ($(switchInput).is(':checked'))
    //     formObject.set($(switchInput).attr('name'), 1);
    //   else
    //     formObject.set($(switchInput).attr('name'), 0);
    // });

    var form_data = $('#customerForm').serialize();
    $('.form-switch').each(function (index) {
      let switchInput = $(this).children('input')[0];
      if ($(switchInput).is(':checked'))
        form_data += '&' + $(switchInput).attr('name') + '=True';
      else
      form_data += '&' + $(switchInput).attr('name') + '=False';
    });
    
    $.ajax({
      url: "/customers/customer_database",
      type: "post",
      dataType: "json",
      data: form_data,
      // data: formObject,
      success: function (data) {
        if (typeof (data) != 'undefined' && data != null) {
          if (typeof (data.customer_address_id) != 'undefined') {
            displaySanctions(data.customer_address_id, data, "customer");
          }

          if (typeof (data.customer_bank_id) != 'undefined') {
            displaySanctions(data.customer_bank_id, data, "bank")
          }

          window.location.reload();
        }
      },
      error: function (request, status, error) {
        alert("Save failed, ensure customer name is unique.");
      }
    });

    //window.location.reload();
  });


  $('#submitAddress').click(function () {
    var form_data;

    if (!addressEditStatus) {
      form_data = $('#newAddressForm').serialize();
    }

    let result = submitCustomerAddress(form_data, null);
    addressEditStatus = !result;
  });

  $('#submitBankAddress').click(function () {
    var form_data = $('#newBankForm').serialize();
    submitBankAddress(form_data, null);
  });


  $('#confirmSanctioned').on("click", function () {
    var endpointURL = "/customer/flag_addresses/" + $(this).data("entityID");

    if ($(this).data("entityType") == "bank") {
      endpointURL = "/customer/flag_bank/" + $(this).data("entityID");
    }

    $.ajax({
      url: endpointURL, // Need to create a new Banks POST endpoint for this on the backend because FLASK can't handle PATCH or PUT, and the POST is already being used for updates.
      type: "post",
      dataType: "json",
      success: function (data) {
        if (typeof (data) != 'undefined' && data != null && data != "") {
          if (typeof (data.customer_bank_id) != 'undefined') {
            $('#new_bank_address, #new_bank_name').addClass('sanctioned');
          }
          else if (typeof (data.customer_address_id) != 'undefined') {
            $('.customerAddress').last().addClass('sanctioned');
          }
        }
      }
    });
  });

  ColumnSelector("customers-table", "selector");
  AddTableSorting($('.database-table'));

}); // End Document.ready()



function editMode(intID = null) {
  $("#AddCustomer").hide();
  $("#selector").hide();
  $("#table-section").hide();
  $("#form-section").show();
}

function createdAddressField(index, object, sanctioned = false) {
  var elementID = "address_" + index;
  var textarea = document.createElement("textarea");
  textarea.value = object.customer_address;
  textarea.classList = "form-control customerAddress";
  textarea.setAttribute("aria-label", "Address " + (index + 1));
  textarea.id = elementID;
  textarea.dataset.customer_address_id = object.customer_address_id

  $("#customer_addresses_block").append(textarea);

  var id_field = document.createElement("input");
  id_field.value = object.customer_address_id;
  id_field.type = "hidden";
  id_field.name = "customer_address_id";
  id_field.id = "address_id_" + index;

  $("#customer_addresses_block").append(id_field);

  if (sanctioned || (typeof (object.sanctioned) != "undefined" && object.sanctioned == true)) {
    $(textarea).toggleClass("sanctioned");
    $(textarea).after("<p class='sanctioned_warning'>Sanctioned Entity</p>");
  }
}

function displaySanctions(entityID, data, entityType) {
  if (data.length != 0) {
    $("#sanctionResults > tbody > tr").remove();
    var html = '';
    for (var i = 0; i < data.length; i++) {
      html += '<tr data-id="' + data[i].id + '">' +
        //  '<td>' + data[i].caption + '</td>' +
        '<td>' + data[i].name + '</td>' +
        '<td>' + data[i].alias + '</td>' +
        '<td>' + data[i].full + '</td>' +
        '<td>' + data[i].country + '</td>' +
        '<td>' + data[i].authority + '</td>' +
        '</tr>';
    }

    $('#sanctionResults tbody').html(html);
    $('#confirmSanctioned').data("entityID", entityID);
    $('#confirmSanctioned').data("entityType", entityType);

    $('#sanctionedEntity').modal('show');
  }

}

function submitCustomerAddress(form_data, id) {
  let customer_name = $('#customer_name').val();
  let result = false;
  form_data += '&search_name=' + encodeURI(customer_name);

  if (id != null && typeof (id) != "undefined") {
    form_data += "&customer_address_id=" + id;
  }

  $.ajax({
    url: "/customer/addresses/" + $('#customer_id').val(),
    type: "post",
    dataType: "json",
    data: form_data,
    statusCode: {
      201: function(response) {
      const data = response; // $.parseJSON(response);
      
      if (typeof (response) != 'undefined' && response != null && typeof (data.customer_address_id) != 'undefined') {
        let index = $('.customerAddress').length;

        // Create new field in the list of addresses and clear out the input field for new entries.
        createdAddressField(index, data);
        $('#new_address').empty();
        $("#addressFormDiv, #cancelAddress, #submitAddress").hide();
        $("#btnAddAddress").show();
        result = true;

        if (data.sanction_results != null && data.sanction_results.length != 0) {          
          displaySanctions(data.customer_address_id, data.sanction_results, "customer");
        }

      }
    }
  }
  });

  return result;
}


function submitBankAddress(form_data, id) {
  if (id != null && typeof (id) != "undefined") {
    form_data += "&customer_bank_id=" + id;
  }

  $.ajax({
    url: "/customer/banks/" + $('#customer_id').val(),
    type: "post",
    dataType: "json",
    data: form_data,
    success: function (data) {
      if (typeof (data) != 'undefined' && data != null && typeof (data.customer_bank_id) != 'undefined') {
        if (data.sanction_results.length != 0) {
          displaySanctions(data.customer_bank_id, data.sanction_results, "bank")
        }
      }
    }
  });
}


function search_sanctions(banksearch = false, search_name = "", search_address = "") {
  const formData = new FormData();
  formData.append("search_name", search_name);
  formData.append("search_address", search_address);

  $.ajax({
    type: "POST",
    url: "/sanctions_query",
    data: formData, // serializes the form's elements.
    processData: false,
    contentType: false,
    //dataType: "application/json",
    async: false,
    success: function (data) {
      if (typeof (data) != 'undefined' && data != null) {
        if (banksearch) {
          displaySanctions(data.customer_bank_id, data, "bank")
        }
        else {
          displaySanctions(data.customer_address_id, data, "customer");
        }

      }
    }
  });
}