var flightsElement = $("#flightSearchResult");
var spinner = $(".loader");
var returnDateVal = "";
var timeoutVar;

var datePickerOptions = {
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
  selectMonths: true,
  selectYears: 5,
  min: true
};

var returnDatePickerOptions = datePickerOptions;
returnDatePickerOptions.onSet = function() {
  returnDateVal = $("#returnDatePicker").val();
};

function validateForm(form) {
  if (form[0].checkValidity() === false) {
    event.preventDefault();
    event.stopPropagation();
    form.addClass("was-validated");
    return false;
  }
  return true;
}

function clearForm(formID) {
  $(":input", "#" + formID)
    .not(":button, :submit, :reset, :hidden")
    .val("")
    .prop("checked", false)
    .prop("selected", false)
    .trigger("change");
}

function clearFlightsResult() {
  if (flightsElement.length) flightsElement.html("");
}

function setSameHeight() {
  $(".price").each(function() {
    $(this).css("height", $(".flight").height() + "px");
    $(".price-body").css("height", $(".flight").height() + "px");
  });
}

function scrollDown(distance) {
  $("html, body").animate(
    {
      scrollTop: distance
    },
    "slow"
  );
}

function isset(variable) {
  if (typeof variable !== "undefined" && variable !== null) {
    return true;
  } else {
    return false;
  }
}

function genLoading() {
  var $progress = $("<div/>").attr({
    id: "loadingSpinner",
    class: "progress-circular mx-auto"
  });
  var $progressWrapper = $("<div/>").attr("class", "progress-circular-wrapper");
  var $progressBody = $("<div/>").attr("class", "progress-circular-inner");

  $progressBody.append(
    $("<div/>")
      .attr("class", "progress-circular-left")
      .append($("<div/>").attr("class", "progress-circular-spinner"))
  );
  $progressBody.append($("<div/>").attr("class", "progress-circular-gap"));
  $progressBody.append(
    $("<div/>")
      .attr("class", "progress-circular-right")
      .append($("<div/>").attr("class", "progress-circular-spinner"))
  );

  $progressWrapper.append($progressBody);
  $progress.append($progressWrapper);

  return $progress;
}

$(window).on("scroll", function() {
  if ($(window).scrollTop() > 0) {
    $(".toolbar-waterfall").addClass("waterfall");
    $("#imageLogo").attr("src", "../static/images/svg/logo_light.svg");
  } else {
    $(".toolbar-waterfall").removeClass("waterfall");
    $("#imageLogo").attr("src", "../static/images/svg/logo_dark.svg");
  }
});

$(function() {
  $(".uppercase-input").bind("input", function() {
    $(this)
      .val(
        $(this)
          .val()
          .toUpperCase()
      )
      .trigger("change");
  });

  $('<span class="form-control-ripple"></span>').insertAfter(
    "[data-ripple-line]"
  );

  $("input[type='password'][data-password]").each(function() {
    var $password = $(this);
    var $icon = $('<i class="material-icons">visibility_off</i>');

    $password.wrap(
      $("<div/>", {
        class: "position-relative"
      })
    );

    $password.css({
      paddingRight: 32
    });

    $password.after($icon);

    $icon.wrap(
      $("<div/>", {
        class: "form-password-icon"
      }).css({
        top: $password.outerHeight() / 2 - 16
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
  });

  $(".form-password-icon").on("click", function() {
    var clicks = $(this).data("clicks");
    if (clicks) {
      $(this)
        .html('<i class="material-icons">visibility_off</i>')
        .prevAll(":input")
        .attr("type", "password");
    } else {
      $(this)
        .html('<i class="material-icons">visibility</i>')
        .prevAll(":input")
        .attr("type", "text");
    }
    $(this).data("clicks", !clicks);
  });

  $(document).on("click", ".process-form", function(e, clicked) {
    if (clicked == null) {
      var $btn = $(this);
      var $form = $btn.closest("form");

      if (validateForm($form)) {
        e.preventDefault();
        spinner.html(genLoading());
        spinner.addClass("d-flex");
        $("header, .jumbotron, main").wrapAll("<div class='blurred'/>");
        $("body").removeClass("body-content");
        setTimeout(function() {
          $btn.trigger("click", ["continue"]);
        }, 2000);
      } else {
        return false;
      }
    }
  });

  $(".needs-validation").submit(function() {
    var $form = $(this);
    validateForm($form);
  });

  $(":input", "#flightForm").change(function() {
    clearFlightsResult();
  });

  $("#flightForm").submit(function() {
    var $scrollDistance = flightsElement.offset().top;
    var $form = $(this);
    if (!validateForm($form)) return false;
    event.preventDefault();
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
        startLimit: $('input[name="startLimit"]').val(),
        endLimit: $('input[name="endLimit"]').val()
      },
      cache: false,
      beforeSend: function() {
        flightsElement.html(genLoading());
      },
      success: function(data) {
        if (data.message === "no_result") {
          $.snackbar({
            content: "There aren't any available flights for this route yet.",
            style: "snackbar-left mb-2"
          });
        }
        flightsElement.html(data.content);
      },
      complete: function() {
        clearTimeout(timeoutVar);
        timeoutVar = setTimeout(setSameHeight(), 500);
        scrollDown($scrollDistance);
        return false;
      },
      error: function(jqXHR, textStatus, errorThrown) {
        alert(errorThrown);
      }
    });
  });

  $(document).on("click", ".load-more-flights", function(e) {
    e.preventDefault();
    var $currentLocation = $(this).offset().top;
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
        startLimit: $('input[name="startLimitMore"]').val(),
        endLimit: $('input[name="endLimitMore"]').val()
      },
      cache: false,
      beforeSend: function() {
        $("#loadMoreBtn").remove();
        flightsElement.append(genLoading());
      },
      success: function(data) {
        $("#loadingSpinner").remove();
        flightsElement.append(data.content);
      },
      complete: function() {
        clearTimeout(timeoutVar);
        timeoutVar = setTimeout(setSameHeight(), 500);
        scrollDown($currentLocation);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        alert(errorThrown);
      }
    });
  });

  $("#fromAirport").change(function() {
    if ($(this).val() != "") {
      $("#toAirport").prop("disabled", false);
    } else {
      $("#toAirport").prop("disabled", true);
      return;
    }

    $("#toAirport")
      .find("option")
      .remove()
      .end()
      .append("<option/>")
      .trigger("change");

    $.ajax({
      type: "GET",
      url: $SCRIPT_ROOT + "/_get_airports",
      contentType: "application/json; charset=utf-8",
      data: {
        airport: $(this).val()
      },
      success: function(data) {
        $.each(data.result, function(index) {
          var value = data.result[index].value;
          var text = data.result[index].text;
          $("#toAirport").append(
            $("<option/>")
              .attr("value", value)
              .text(text)
          );
        });
      },
      error: function(jqXHR, textStatus, errorThrown) {
        alert(errorThrown);
      }
    });
  });

  $('#nav-tab a[data-toggle="tab"]').on("shown.bs.tab", function() {
    clearFlightsResult();
  });

  $("#nav-roundtrip-tab").on("click", function() {
    var $target = $("#returnDatePicker");
    $target.prop({ disabled: false, required: true });
    $target.val(returnDateVal).trigger("change");
  });

  $("#nav-oneway-tab").on("click", function() {
    var $target = $("#returnDatePicker");
    $target.prop({ disabled: true, required: false });
    $target.val("One Way").trigger("change");
  });

  $(".snackbar-btn").on("click", function() {
    $(".snackbar").removeClass("show");
  });
});

$("#departDatePicker")
  .pickdate(datePickerOptions)
  .prop("readonly", false);

$("#returnDatePicker")
  .pickdate(returnDatePickerOptions)
  .prop("readonly", false);
