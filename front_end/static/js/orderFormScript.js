import { ColumnSelector } from "./ColumnSelector.js";
import { AddTableSorting } from "./TableSorting.js";

var $productRowTemplate = $('#product1').clone();

$(document).ready(function () {
  var $rows = $('.database-table tbody tr');
  var filters = [];
  var $inputs = $(".database-table .columnFilter input");
  $productRowTemplate = $('#product1').clone();
  $inputs.each(function () {
    filters.push([]);
  });

  // Code for column filters on Orders tables.
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



  setClickEvents();

  ///   Repeating Product Form Rows    ////

  $("#addProduct").click(function () {

    // get the last DIV which ID starts with ^= "another-participant"
    var $div = $('div[id^="product"]:last');

    // Read the Number from that DIV's ID (i.e: 1 from "another-participant1")
    // And increment that number by 1
    var num = parseInt($div.prop("id").match(/\d+/g), 10) + 1;

    // Clone it and assign the new ID (i.e: from num 4 to ID "another-participant4")
    var $newRow = $div.clone().prop('id', 'product' + num);

    // for each of the inputs inside the div, clear it's value and 
    // increment the number in the 'name' attribute by 1
    $newRow.find('input, select').each(function () {
      this.value = "";
      let name_number = this.name.match(/\d+/);
      name_number++;
      let new_name = this.name.replace(/\[[0-9]\]+/, '[' + name_number + ']');
      if (this.type == 'button') {
        this.value = "Product Name";
      }
      else {
        this.name = new_name
      }
    });
    // Finally insert $newRow after the last div
    $div.after($newRow);

    var $newDiv = $('div[id^="product"]:last');
    $newDiv.children("select").each(function () {
      resetSelect(this);
    });

    $(".productSelection").off("click");
    setFilterButtons();
    updateRemoveLinks();

    $(".removeProductIcon").click(function () {
      let $parentTag = $(this).parent().get(0);
      $parentTag.remove();
      updateRemoveLinks();
    });

  }); // End addProduct.click()

  setFilterButtons();
  updateRemoveLinks();


  $(".concernSwitch").change(function () {
    updateConcernSummary();
  });


  $(".customerSelection").click(function () {
    let customer_id = $(this).data("customer_id");
    let customer_name = $(this).data("customer_name");

    $("#customer_id").val(customer_id);
    $("#customer_heading").html(customer_name);

    //filterButton($(this).parent());
    selectCustomer($(this).parent());

    getCustomerData(customer_id);
    insertAddrBankData(customer_id);
    displayOrderHistory(customer_id);

    $('#orderForm').removeClass("orderFormDisplay");
  });


  $("#orderForm").submit(function (e) {
    e.preventDefault();

    // const form = document.getElementById('orderForm');
    const formData = new FormData($(this)[0]);

    var arrProducts = [];
    $('.repeatable').each(function () {
      var product = {};
      var product_id =  $(this).children(".unitSize").val();
      if(product_id > 0) {        
        product["product_id"] = product_id;
        product["quantity"] = $(this).children(".number_units").val();
        product["order_item_id"] = $(this).children(".order_item_id").val();
        arrProducts.push(product);
      }
    });


    formData.append("products", JSON.stringify(arrProducts));


    $('.form-switch').each(function (index) {
      let switchInput = $(this).children('input')[0];
      if ($(switchInput).is(':checked'))
        formData.set($(switchInput).attr('name'), 1);
      else
        formData.set($(switchInput).attr('name'), 0);
    });

    var actionUrl = "#";
    $.ajax({
      type: "POST",
      url: actionUrl,
      data: formData, // serializes the form's elements.
      processData: false,
      contentType: false,
      dataType: "application/json",
      statusCode: {
        201: function(response) {
      //success: function (data) {
        // window.location.reload();
        return true;
      }
    },
      fail: function( jqXHR, textStatus ) {
        alert( "Save failed: " + textStatus );
      },
      done: function( msg ) {
        console.log(msg);
      }
    });

    // window.location.reload();


    return true;
  }); // End Function submit.click()


  $("#address_different").change(function () {
    $("#newAddressBlock").toggle();
    if (this.checked) {
      //Do stuff
    }
  });

  $("#bank_name_different, #bank_address_different").change(function () {
    if ($("#bank_name_different").is(":checked") || $("#bank_address_different").is(":checked")) {
      $(".newBankBlock").show();
    }
    else {
      $(".newBankBlock").hide();
    }
  });



  $('#submitAddress').click(function () {
    var form_data = $('#newAddressForm').serialize();

    $.ajax({
      url: "/customer/addresses/" + $('#customer_id').val(),
      type: "post",
      dataType: "json",
      data: form_data,
      success: function (data) {
        if (typeof (data) != 'undefined' && data != null && typeof (data.customer_address_id) != 'undefined') {

        }
      }
    });
  });


  $('#submitBankAddress').click(function () {
    var form_data = $('#newBankForm').serialize();

    $.ajax({
      url: "/customer/banks/" + $('#customer_id').val(),
      type: "post",
      dataType: "json",
      data: form_data,
      success: function (data) {
        if (typeof (data) != 'undefined' && data != null && typeof (data.customer_bank_id) != 'undefined') {
        }
      }
    });
  });

  ColumnSelector("orders-table-active", "active-table-selector");
  ColumnSelector("orders-table-all", "all-table-selector");
  AddTableSorting($('.database-table, #orders-table-all'));

  // $('#productRows .filterButton')
  $("#productRows").delegate(".filterButton", "click", function() {
    filterButton(this);
});

}); // End Document Ready


function updateRemoveLinks() {
  // if "repeatable" element count is greater than 1...
  if ($('.repeatable').length > 1) {
    // ...show the "remove" link
    $('.repeatable').children('.removeProductIcon').css({ 'display': 'inline-block' });
    // otherwise...
  } else {
    // don't display the "remove" link
    $('.repeatable').children('.removeProductIcon').css({ 'display': 'none' });
  }

}


function setFilterButtons() {

  $(".productSelection").on("click", function () {
    let product_name = $(this).data("product_name");
    var $row = $(this).parent().parent().parent();
    var dropdown = $row.children(".unitSize")[0];

    console.log("Flag Value", $row.find(".hazardousFlag")[0].value);
    
    $row.children(".unitSize")[0].value = "";
    $row.find(".hazardousFlag")[0].value = "";


    resetSelect(dropdown);

    $(this).parent().siblings(".filterButton").prop('value', product_name);

    filterButton($(this).parent());

    $.ajax({
      url: "/products/products_by_name/" + product_name,
      type: "GET",
      dataType: "json",
      success: function (data) {
        if (typeof (data) != 'undefined' && data != null && typeof (data[0].name) != 'undefined') {
          console.log("This: ", this);
          
          dropdown.onchange = function () { checkConcerns(this) };


          $.each(data, function (i, item) {
            let option = document.createElement("option");
            option.value = data[i]["product_id"];
            option.text = data[i]["size"];

            $row.children(".unitSize")[0].append(
              option
            );
          });

        }
      }
    });
  });

  $(".filterInput").on("keyup", function () {

    var filter, ul, li, a, i;
    filter = $(this).val().toUpperCase();
    a = $(this).parent().children("a");
    for (i = 0; i < a.length; i++) {
      let txtValue = a[i].textContent || a[i].innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        a[i].style.display = "";
      } else {
        a[i].style.display = "none";
      }
    }
  });
}


/* When the user clicks on the Company button,
toggle between hiding and showing the dropdown content */
export function filterButton(filterButton) {
  var $button = $(filterButton).parent();
  $button.children(".dropdown-content").toggle();
}

function filterFunction() {
  var input, filter, ul, li, a, i;
  input = document.getElementById("companyInput");
  filter = input.value.toUpperCase();
  div = document.getElementById("myDropdown");
  a = div.getElementsByTagName("a");
  for (i = 0; i < a.length; i++) {
    txtValue = a[i].textContent || a[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      a[i].style.display = "";
    } else {
      a[i].style.display = "none";
    }
  }
}


function checkConcerns(item, value) {
  //var $selectedItem = $(item).find(':selected');

  // Reset any existing flags
  var $txtConcerns = $(item).siblings(".hazards");
  var $hazardFlag = $(item).siblings(".hazardousFlag");
  var $securityFlag = $(item).siblings(".securityFlag");
  var hazardIcon = `<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' fill='currentColor' class='bi bi-exclamation-octagon-fill hazardous-icon' viewBox='0 0 16 16'>
  <path d='M11.46.146A.5.5 0 0 0 11.107 0H4.893a.5.5 0 0 0-.353.146L.146 4.54A.5.5 0 0 0 0 4.893v6.214a.5.5 0 0 0 .146.353l4.394 4.394a.5.5 0 0 0 .353.146h6.214a.5.5 0 0 0 .353-.146l4.394-4.394a.5.5 0 0 0 .146-.353V4.893a.5.5 0 0 0-.146-.353L11.46.146zM8 4c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995A.905.905 0 0 1 8 4zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z'></path>
</svg>`;

  $hazardFlag.html("");
  $txtConcerns.val("");
  $securityFlag.html("");

  $.ajax({
    url: "/products/product_details/" + value,
    type: "GET",
    dataType: "json",
    success: function (product_data) {
      if (typeof (product_data) != 'undefined' && product_data != null && typeof (product_data.product_id) != 'undefined') {
        product_data.concerns == 1 ? $securityFlag.html(hazardIcon) : $securityFlag.html("");

        // $(item).siblings(".other_issues").val(product_data.other_issues);

        // $.ajax({
        //   url: "/products/cas_hazards/" + product_data.cas,
        //   type: "GET",
        //   dataType: "json",
        //   success: function (data) {
        //     if (typeof (data) != 'undefined' && data != null && typeof (data.cas_hazard_code) != 'undefined') {
        //       $txtConcerns.val(data.cas_hazard_code);
        //       $securityFlag.html(hazardIcon);
        //     }
        //     else {
        //       $txtConcerns.val("");
        //       $securityFlag.html("");
        //     }
        //   }
        // });

        if(product_data.hazard_codes) {
          console.log("Test");
          
          $hazardFlag.html(hazardIcon);
          $.ajax({
            url: "/products/ghs_hazards/" + product_data.hazard_codes,
            type: "GET",
            dataType: "json",
            success: function (data) {
              if (typeof (data) != 'undefined' && data != null) {
              if (typeof (data.hazard_code) != 'undefined') {
                $hazardFlag.html(hazardIcon);
              }
              else $hazardFlag.html("");
              
            }
          }
          });
        }

      }
    }
  });

}


function resetSelect(dropdown) {
  $(dropdown).empty();
  var option = document.createElement("option");
  option.value = null;
  option.text = " -- Select Size -- ";
  option.disabled = true;
  option.selected = true;
  $(dropdown).append(
    option
  );

}


function insertAddrBankData(intID, selectedAddress = 0, selectedBank = 0) {
  resetAddressHistory();
  resetBankHistory();

  $.ajax({
    url: "/orders/customer_order/shipping_history/" + intID,
    type: "GET",
    dataType: "json",
    success: function (data) {
      fillAddressHistory(data, selectedAddress);
    }
  });


  $.ajax({
    url: "/orders/customer_order/bank_history/" + intID,
    type: "GET",
    dataType: "json",
    success: function (data) {
      fillBankHistory(data, selectedBank);
    }
  });
}

function fillAddressHistory(addresses, selectedAddress = 0) {
  if (typeof (addresses) != 'undefined' && addresses != null && typeof (addresses[0]) != 'undefined') {
    $.each(addresses, function (index, object) {
console.log("History Object:", object);

      var option = document.createElement("option");
      // option.value = object.customer_address_id;
      option.value = object.shipping_address;
      option.innerHTML = object.shipping_address;

      $("#customer_address_id").append(option);
      if(selectedAddress > 0) $("#customer_address_id").val(selectedAddress);

      if (typeof (object.sanctioned) != "undefined" && object.sanctioned == true) {
        $('#customer_address_id').toggleClass("sanctioned");
        $('#customer_address_id').after("<p class='sanctioned_warning'>Sanctioned Entity</p>");
      }
    });
  }
} // End Function fillAddressHistory()

function fillBankHistory(banks, selectedBank = 0) {
  if (typeof (banks) != 'undefined' && banks != null && typeof (banks[0]) != 'undefined' && typeof (banks[0].order_bank) != 'undefined') {
    $.each(banks, function (index, object) {
      var option = document.createElement("option");
      option.value = object.order_bank;
      //option.title = object.bank_name + "\n" + object.bank_address;
      option.innerHTML = object.order_bank;

      $("#bank_history").append(option);
      if(selectedBank > 0) $("#bank_history").val(selectedBank);

      if (typeof (object.sanctioned) != "undefined" && object.sanctioned == true) {
        $('#bank_history').toggleClass("sanctioned");
        $('#bank_history').after("<p class='sanctioned_warning'>Sanctioned Entity</p>");
      }
    });

  }
} // End Function fillBankHistory()

function resetAddressHistory() {
  $('#customer_address_id').empty();
  var titleOption = document.createElement("option");
  titleOption.value = 0;
  titleOption.innerHTML = "-- Previous Addresses --";
  $("#customer_address_id").append(titleOption);
  titleOption.disabled = true;
} // End Function resetAddressHistory()

function resetBankHistory() {
  $('#bank_history').empty();
  var titleOption = document.createElement("option");
  titleOption.value = 0;
  titleOption.innerHTML = "-- Previous Banks --";
  $("#bank_history").append(titleOption);
  titleOption.disabled = true;
}

function displayOrderHistory(customer_id = null) {
  $.ajax({
    url: "/orders/customer_order/by_customer/" + customer_id,
    type: "GET",
    dataType: "json",
    success: function (data) {
      updateHistoryTable(data);
    }
  });

  return null;
}


function setClickEvents() {
  // Choose Customer
  $('#cmdCompany').click(function () {
    selectCustomer(this);
  });


  // Toggle Edit View
  $(".editIcon").click(function () {
    var intID = $(this).data("item_id");
    $('.dropdown-content').hide();
    editMode(intID);
  });


  $(".deleteIcon").click(function () {
    var intID = $(this).data("item_id") ?? null;

    var confirmation = confirm("Are you sure you want to delete this item? (ID: " + intID + ")");

    if (confirmation) {
      let id_package = {};
      id_package['order_id'] = intID;

      $.ajax({
        url: "/orders/customer_order",
        type: "DELETE",
        dataType: "json",
        encode: true,
        data: id_package,
        success: function (data) {
          window.location.reload(true);
        }
      });
    }
  });


  $('#customer_address_id').on('change', function () {
    var optionSelected = $(this);
    //var valueSelected  = optionSelected.val();
    var textSelected   = optionSelected.text();
    $('#shipping_address').val(this.selectedOptions[0].text);
  });

  $('#bank_history').on('change', function () {
    console.log("Hello");
    
    var optionSelected = $(this);
    //var valueSelected  = optionSelected.val();
    var textSelected   = optionSelected.text();
    $('#order_bank').val(this.selectedOptions[0].text);
  });

  return null;
}

function selectCustomer($customerButton) {
  var $button = $($customerButton).parent();
  $button.children(".dropdown-content").toggle();
}

function editMode(intID) {

  // var $productRow = $('#product1').clone();
  $('.repeatable').not(':first').remove();
  // $('#productRows').append($productRow);
  // $('#productRows').empty();
  // $('#productRows').append($productRowTemplate);

  $.ajax({
    url: "/orders/customer_order/" + intID,
    type: "GET",
    dataType: "json",
    success: function (data) {
      if (typeof (data) != 'undefined' && data != null && typeof (data.orders) != 'undefined' && typeof (data.orders.order_id) != 'undefined') {
        console.log(data);
        
        let order_details = data.orders;
        let shipping_addresses = data.addresses;
        let banks = data.banks;

        updateHistoryTable(order_details);

        $('#cmdCompany').hide();
        const bsTab = new bootstrap.Tab('#newOrder-tab');
        bsTab.show();

        //insertAddrBankData(order_details.customer_id, order_details.customer_address_id);
        resetAddressHistory();
        resetBankHistory();
        fillAddressHistory(shipping_addresses, order_details.order_id);
        fillBankHistory(banks, order_details.order_id);

        displayOrderHistory(order_details.customer_id);

        $('#order_id').val(order_details.order_id ?? '');
        $("#customer_id").val(order_details.customer_id);
        $("#customer_heading").html(order_details.customer_name);
        $('#facility_order_id').val(order_details.facility_order_id);
        $('#poc_name').val(order_details.poc_name);
        $('#order_date').val(order_details.order_date);
        $('#delivery_date').val(order_details.delivery_date);

        let i = 1;
        if (order_details.products.length > 0) {
          order_details.products.forEach(
            (element) => {
              if (i > 1) $("#addProduct").trigger("click");
              // Popoulate product fields
              var $row = $('#product' + i);
              var $selectedProduct = $($row).find(".productSelection[data-product_name='" + element.name + "']");
              $($selectedProduct).trigger("click");
              filterButton($($selectedProduct).parent());

              $row.children(".unitSize").val(element.product_id);
              $row.children(".number_units").val(element.quantity);
              $row.children(".order_item_id").val(element.order_item_id);

              var $selectedSize = $row.find(".unitSize");
              console.log("Size", $selectedSize);
              console.log("Children:", $row.children(".unitSize").val(element.product_id));
              
              $($selectedSize).trigger('click');
              
              checkConcerns($($selectedSize), element.product_id);
              i++;
            });
        }

        getCustomerData(order_details.customer_id);
        $('#shipping_address').val(order_details.shipping_address);
        
        $('#payment_method').val(order_details.payment_method_id);
        $('#payment_method_id').val(order_details.payment_method_id);
        $('#order_bank').val(order_details.order_bank);
        
        $('#address_different').attr("checked", order_details.address_different ? true : false);
        $('#bank_name_different').attr("checked", order_details.bank_name_different ? true : false);
        $('#payment_different').attr("checked", order_details.payment_different ? true : false);

        $('#atypical_order').attr("checked", order_details.atypical_order ? true : false);
        $('#larger_order').attr("checked", order_details.larger_order ? true : false);
        $('#end_use_verified').attr("checked", order_details.end_use_verified ? true : false);
        $('#order_method').val(order_details.order_method);

        $('#urgent_shipping').attr("checked", order_details.urgent_shipping ? true : false);
        $('#immediate_custody').attr("checked", order_details.immediate_custody ? true : false);
        $('#transporter_name').val(order_details.transporter_name);
        $('#transporter_address').val(order_details.transporter_address);
        $('#transporter_phone').val(order_details.transporter_phone);

        $('#first_time_transporter').attr("checked", order_details.first_time_transporter ? true : false);
        $('#shipment_verification').attr("checked", order_details.shipment_verification ? true : false);
        $('#unusual_routing').attr("checked", order_details.unusual_routing ? true : false);
        $('#unusual_labeling').attr("checked", order_details.unusual_labeling ? true : false);
        $('#unusual_handling').attr("checked", order_details.unusual_handling ? true : false);
        $('#ppe_concern').attr("checked", order_details.ppe_concern ? true : false);
        $('#route_safety_concern').attr("checked", order_details.route_safety_concern ? true : false);
        
        updateConcernSummary();
      }
    }
  });

  $('#orderForm').removeClass("orderFormDisplay");
}


function updateHistoryTable(data) {
  if (typeof (data) != 'undefined' && data != null && typeof (data.order_id) != 'undefined') {
    var customer_history = data.address_different + data.bank_name_different + data.bank_address_different + data.payment_different;
    $('#customer_history_past').html(customer_history);

    var customer_activity = data.atypical_order + data.larger_order + data.end_use_verified;
    $('#customer_activity_past').html(customer_activity);

    var customer_shipping = data.urgent_shipping + data.immediate_custody + data.first_time_transporter + data.shipment_verification +
      data.unusual_routing + data.unusual_labeling + data.unusual_handling + data.ppe_concern + data.route_safety_concern;
    $('#customer_shipping_past').html(customer_shipping);
    $("#total_past").html(customer_history + customer_activity + customer_shipping);
  }
  else {
    $('#customer_history_past').html("");
    $('#customer_activity_past').html("");
    $('#customer_shipping_past').html("");
    $('#total_past').html("");
  }
} // End Function updateHistoryTable()


function getCustomerData(customer_id){
  $.ajax({
    url: "/customers/customer_details/" + customer_id,
    type: "GET",
    dataType: "json",
    success: function (data) {
      if (typeof (data) != 'undefined' && data != null && typeof (data.customer_id) != 'undefined') {
        if(data.sanctioned == 1) { $('#sanctioned_entity').show(); }
        else { $('#sanctioned_entity').hide(); }
      }
    }
  });
}

function updateConcernSummary() {
  let historySwitchCount = $(".history:checked").length;
  let activitySwitchCount = $(".activity:checked").length;
  let shippingSwitchCount = $(".shipping:checked").length;
  $("#customer_history_current").html(historySwitchCount);
  $("#customer_activity_current").html(activitySwitchCount);
  $("#customer_shipping_current").html(shippingSwitchCount);
  $("#total_current").html(historySwitchCount + activitySwitchCount + shippingSwitchCount);   
}