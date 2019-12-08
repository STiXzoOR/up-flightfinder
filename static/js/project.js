var returnDateVal = "";

function clearForm(formID) {
  $(":input", "#" + formID)
    .not(":button, :submit, :reset, :hidden")
    .val("")
    .prop("checked", false)
    .prop("selected", false)
    .trigger("change");
}

function setSameHeight(firstSelector, secondSelector) {
  $(firstSelector).each(function() {
    $(this).css("height", $(secondSelector).height() + "px");
  });
}

function isset(variable) {
  if (typeof variable !== "undefined" && variable !== null) {
    return true;
  } else {
    return false;
  }
}

function showSnackbar(options) {
  if (isset(options)) {
    if (isset(options.content)) {
      $("#snackarBody").html(options.content);
    }

    if (isset(options.dismiss)) {
      var btn =
        '<button id="snackbarDismissBtn" class="snackbar-btn" type="button">Dismiss</button>';
      $("#snackbar").append($(btn));
    } else {
      if ($("#snackbarDismissBtn").length) {
        $("#snackbarDismissBtn").remove();
      }
    }

    if (isset(options.alignleft)) {
      $("#snackbar").attr("class", "snackbar snackbar-left position-fixed");
    } else if (isset(options.alignright)) {
      $("#snackbar").attr("class", "snackbar snackbar-right position-fixed");
    } else {
      $("#snackbar").attr("class", "snackbar position-fixed");
    }
  }

  if ($(".snackbar.show").length > 0) {
    $(".snackbar.show")
      .removeClass("show")
      .one("webkitTransitionEnd transitionEnd", function() {
        $("#snackbar").addClass(function() {
          setTimeout(function() {
            $("#snackbar").removeClass("show");
          }, 5000);

          return "show";
        });
      });
  } else {
    $("#snackbar").addClass(function() {
      setTimeout(function() {
        $("#snackbar").removeClass("show");
      }, 5000);

      return "show";
    });
  }
}

$(window).on("scroll", function() {
  if ($(window).scrollTop() > 0) {
    $(".toolbar-waterfall").addClass("waterfall");
  } else {
    $(".toolbar-waterfall").removeClass("waterfall");
  }
});

$(function() {
  $('<span class="form-control-ripple"></span>').insertAfter(
    "[data-ripple-line]"
  );
});

$(function() {
  var $password = $("input[type='password'][data-password]");
  var $icon = $('<i class="material-icons">visibility_off</i>');

  $password.wrap(
    $("<div/>", {
      class: "position-relative",
    })
  );

  $password.css({
    paddingRight: 32,
  });

  $password.after($icon);

  $icon.wrap(
    $("<div/>", {
      class: "form-password-icon",
    }).css({
      top: $password.outerHeight() / 2 - 16,
    })
  );

  var invalid_feedback = $password
    .parent()
    .parent()
    .find(".invalid-feedback");

  if (invalid_feedback.length) {
    $password.after(invalid_feedback.clone());
    invalid_feedback.remove();
  }

  var ripple_line = $password
    .parent()
    .parent()
    .find(".form-control-ripple");

  if (ripple_line.length) {
    $password.after(ripple_line.clone());
    ripple_line.remove();
  }

  $(".form-password-icon").on("click", function() {
    var clicks = $(this).data("clicks");
    if (clicks) {
      // odd clicks
      $(this)
        .html('<i class="material-icons">visibility_off</i>')
        .prevAll(":input")
        .attr("type", "password");
    } else {
      // even clicks
      $(this)
        .html('<i class="material-icons">visibility</i>')
        .prevAll(":input")
        .attr("type", "text");
    }
    $(this).data("clicks", !clicks);
  });
});

$(function() {
  "use strict";
  $(".needs-validation").submit(function() {
    var form = $(this);
    if (form[0].checkValidity() === false) {
      event.preventDefault();
      event.stopPropagation();
    }
    form.addClass("was-validated");
  });
});

$(function() {
  $("#flightSearch").click(function() {
    $.ajax({
      type: "GET",
      url: $SCRIPT_ROOT + "/search-flights",
      contentType: "application/json; charset=utf-8",
      data: {
        fromAirport: $('select[name="fromAirport"]').val(),
        toAirport: $('select[name="toAirport"]').val(),
        departDate: $('input[name="departDate"]').val(),
        returnDate: $('input[name="returnDate"]').val(),
        numPassengers: $('select[name="numPassengers"]').val(),
        flightClass: $('select[name="flightClass"]').val(),
      },
      cache: false,
      success: function(response) {
        if (response === "no_result") {
          $.snackbar({
            content: "There aren't any available flights for this route yet.",
            style: "snackbar-left mb-2",
          });
        } else {
          $("#flightSearchResult").html(response);
        }
      },
      complete: function() {
        $("#flightsContainer").simpleLoadMore({
          item: ".more-item",
          count: 5,
        });
        $(function() {
          setSameHeight(".price", ".flight");
        });
      },
      error: function(jqXHR, textStatus, errorThrown) {
        alert(errorThrown);
      },
    });
  });
});

$(function() {
  $("#fromAirport").change(function() {
    if ($(this).val() != "") {
      $("#toAirport").prop("disabled", false);
    } else {
      $("#toAirport").prop("disabled", true);
    }

    $("#toAirport")
      .find("option")
      .remove()
      .end()
      .append("<option></option>")
      .trigger("change");

    var opts = $("#fromAirport option")
      .map(function() {
        return this.value;
      })
      .get();

    $.ajax({
      type: "POST",
      url: $SCRIPT_ROOT + "/_get_airports",
      contentType: "application/json; charset=utf-8",
      //   dataType: "json",
      data: JSON.stringify({
        airport: $(this).val(),
        airports: opts,
      }),
      success: function(data) {
        $.each(data.result, function(index) {
          var name = data.result[index];
          $("#toAirport").append(
            '<option value="' + name + '">' + name + "</option>"
          );
        });
      },
      error: function(jqXHR, textStatus, errorThrown) {
        alert(errorThrown);
      },
    });
  });
});

$(function() {
  $("#nav-roundtrip-tab").click(function() {
    $("#returnDatePicker").prop({ disabled: false, required: true });
    // clearForm('flightForm')
    $("#returnDatePicker")
      .val(returnDateVal)
      .trigger("change");
    $("#flightSearchResult").html("");
  });
});

$(function() {
  $("#nav-oneway-tab").click(function() {
    $("#returnDatePicker").prop({ disabled: true, required: false });
    // clearForm('flightForm')
    $("#returnDatePicker")
      .val("One Way")
      .trigger("change");
    $("#flightSearchResult").html("");
  });
});

$("#departDatePicker").pickdate({
  cancel: "Clear",
  closeOnCancel: false,
  closeOnSelect: true,
  container: "body",
  containerHidden: "body",
  firstDay: 1,
  format: "dd mmm yyyy",
  formatSubmit: "yyyy-mm-dd",
  hiddenPrefix: "prefix_",
  hiddenSuffix: "_suffix",
  labelMonthNext: "Go to the next month",
  labelMonthPrev: "Go to the previous month",
  labelMonthSelect: "Choose a month from the dropdown menu",
  labelYearSelect: "Choose a year from the dropdown menu",
  ok: "Close",
  onClose: function() {
    // $("body").snackbar({ content: "Depart date selected." });
    // $.snackbar('Depart date selected')
    // $.snackbar({
    //   content: "Depart date selected",
    //   style: "snackbar-left mb-2",
    // });
  },
  onOpen: function() {
    // console.log("Datepicker opens");
  },
  // onSet            : function (date) {
  //   var selectedDate = new Date(date.select);
  //   var endDate = new Date(selectedDate.getTime());

  //   $("#datepicker_Fei2").data('md.pickdate')._config.min = endDate;
  //   // $("#datepicker_Fei2").pickdate({ min: endDate });
  // },
  selectMonths: true,
  selectYears: 5,
  min: true,
});

$("#returnDatePicker").pickdate({
  cancel: "Clear",
  closeOnCancel: false,
  closeOnSelect: true,
  container: "body",
  containerHidden: "body",
  firstDay: 1,
  format: "dd mmm yyyy",
  formatSubmit: "yyyy-mm-dd",
  hiddenPrefix: "prefix_",
  hiddenSuffix: "_suffix",
  labelMonthNext: "Go to the next month",
  labelMonthPrev: "Go to the previous month",
  labelMonthSelect: "Choose a month from the dropdown menu",
  labelYearSelect: "Choose a year from the dropdown menu",
  ok: "Close",
  onClose: function() {
    // console.log("Datepicker closes");
    // $("body").snackbar({ content: "Return date selected." });
    // $.snackbar('Return date selected.')
    // $.snackbar({
    //   content: "Return date selected.",
    //   style: "snackbar-left mb-2",
    // });
  },
  onOpen: function() {
    // console.log("Datepicker opens");
  },
  onSet: function(date) {
    returnDateVal = $("#returnDatePicker").val();
    // var selectedDate = new Date(date.select)
    // var endDate = new Date(selectedDate.getTime())

    // $("#datepicker_Fei2").data('md.pickdate')._config.min = endDate;
    // $("#datepicker_Fei2").pickdate({ min: endDate });
  },
  selectMonths: true,
  selectYears: 5,
  min: true,
});

function parseDate(str) {
  var date = str.split("/");
  var months = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
  ];

  var year = parseInt(date[2]);
  var month = months.indexOf(date[1].toLowerCase());
  var day = parseInt(date[0]);

  return new Date(year, month, day);
}

$(function() {
  $("#snackbarDismissBtn").click(function() {
    $("#snackbar").removeClass("show");
  });
});

// $(function() {
//   $(".flight-row").on("resize", function() {
//     setSameHeight(".price", ".flight");
//   });
// });
