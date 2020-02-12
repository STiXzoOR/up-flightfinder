var searchParams = new URLSearchParams(window.location.search);
var flightsElement = $("#flightSearchResult");
var spinner = $(".loader");
var returnDateVal = {};
var timeoutVar;

$("body").addClass("pace-top");

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
  if (flightsElement.length) {
    flightsElement.html("");
    flightsElement.addClass("d-none");
  }
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

function startResendTimer() {
  var $btn = $("#btnResend");
  var btnOriginalText = "Resend";
  var secs = 30;

  $btn.text(btnOriginalText + " (" + secs + ")").prop({ disabled: true });

  var timer = setInterval(function() {
    secs--;
    $btn.text(btnOriginalText + " (" + secs + ")");
    if (secs === 0) {
      $btn.text(btnOriginalText).prop({ disabled: false });
      clearInterval(timer);
    }
  }, 1000);
}

function fixPacePosition() {
  var $header = $(".toolbar-waterfall");
  var $pace = $(".pace-top > .pace > .pace-progress");

  if ($header.hasClass("bg-alt-primary") || $header.hasClass("waterfall")) {
    $pace.css({ top: $header.outerHeight() + "px" });
  } else {
    $pace.css({ top: 0 });
  }
}

$.fn.isPartial = function() {
  var elementTop = $(this).offset().top;
  var elementBottom = elementTop + $(this).outerHeight();

  var viewportTop = $(window).scrollTop();
  var viewportBottom = viewportTop + $(window).height();

  return elementBottom >= viewportBottom;
};

$(window).on("scroll", function() {
  var $header = $(".toolbar-waterfall");
  var $pace = $(".pace-top > .pace > .pace-progress");

  if ($(window).scrollTop() > 0) {
    $header.addClass("waterfall");
    $pace.css({ top: $header.outerHeight() + "px" });
  } else {
    $header.removeClass("waterfall");
    fixPacePosition();
  }
});

$(function() {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/_get_max_date",
    success: function(data) {
      genDatePickers(data.date);
    },
    error: function(jqXHR, textStatus, errorThrown) {
      alert(errorThrown);
    }
  });

  function genDatePickers(maxDate) {
    var datePickerOptions = {
      cancel: "Clear",
      closeOnCancel: false,
      closeOnSelect: true,
      firstDay: 1,
      hiddenName: true,
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
      min: true,
      max: new Date(maxDate)
    };

    var returnDatePickerOptions = $.extend({}, datePickerOptions);
    returnDatePickerOptions.onSet = function() {
      returnDateVal.visible = $("#returnDatePicker").val();
      returnDateVal.hidden = $('input[name="returnDate"]').val();
    };

    $("#departDatePicker")
      .pickdate(datePickerOptions)
      .prop("readonly", false);

    $("#returnDatePicker")
      .pickdate(returnDatePickerOptions)
      .prop("readonly", false);
  }
});

$(function() {
  $(document).ajaxStart(function() {
    $("body")
      .removeClass("pace-center")
      .addClass("pace-top");
    Pace.restart();
    fixPacePosition();
  });

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
    var $btn = $(this);
    var $form = $btn.closest("form");

    if (validateForm($form)) {
      $("body")
        .removeClass("pace-top")
        .addClass("pace-center");

      // START OF HACKY WORKAROUND
      // Hacky workardound to prevent pace from timeout if body is already loaded
      $("body").append(
        $("<input/>").attr({ id: "dummyCounter", type: "hidden", value: 0 })
      );

      var timer = setInterval(function() {
        for (var i = 0; i < 1000; i++) {
          var val = parseInt($("#dummyCounter").val()) + 1;
          $("#dummyCounter")
            .val(val)
            .text(val)
            .trigger("change");
        }
      }, 10);

      setTimeout(function() {
        clearInterval(timer);
      }, 10000);
      // END OF HACKY WORKAROUND

      $("html, body").css({
        overflow: "hidden",
        height: "100%"
      });

      $("header, .jumbotron, main").wrapAll("<div class='fullscreen-pace'/>");
      Pace.restart();
      var $pace = $(".pace-center > .pace > .pace-progress");
      $pace.append(genLoading());

      Pace.on("hide", function() {
        $("header, .jumbotron, main").unwrap();
        $("html, body").css({
          overflow: "",
          height: ""
        });
        $("#dummyCounter").remove();
      });

      return;
    } else {
      return false;
    }
  });

  $(".needs-validation").submit(function() {
    var $form = $(this);
    validateForm($form);
  });

  $(":input", "#flightForm").on("change", function() {
    clearFlightsResult();
  });

  $("#flightForm").submit(function() {
    var $form = $(this);
    if (!validateForm($form)) return false;
    event.preventDefault();
    var found;

    $.ajax({
      type: "GET",
      url: $SCRIPT_ROOT + "/flights/search-flights",
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
        clearFlightsResult();
      },
      success: function(data) {
        if (data.message === "no_result") {
          found = false;
          $.snackbar({
            content: "There aren't any available flights for this route yet.",
            style: "snackbar-left mb-2"
          });
        } else {
          found = true;
          flightsElement.html(
            '<div class="text-center my-3"><h2 class="text-dark font-weight-bold mb-1">Flights</h2><p class="text-muted mb-0">Total: ' +
              data.total +
              "</p></div>"
          );
          flightsElement.append(data.content);
        }
      },
      complete: function() {
        if (found) {
          flightsElement.removeClass("d-none");
          if (flightsElement.isPartial()) {
            var $scrollDistance = $("#flightSearchResult div")
              .first()
              .offset().top;
            scrollDown($scrollDistance - 65);
          }
        }
        return false;
      },
      error: function(jqXHR, textStatus, errorThrown) {
        alert(errorThrown);
      }
    });
  });

  $(document).on("click", ".load-more-flights", function(e) {
    e.preventDefault();

    var $scrollDistance = $(this).offset().top;
    $.ajax({
      type: "GET",
      url: $SCRIPT_ROOT + "/flights/search-flights",
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
      },
      success: function(data) {
        flightsElement.append(data.content);
      },
      complete: function() {
        if (flightsElement.isPartial()) {
          scrollDown($scrollDistance - 65);
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        alert(errorThrown);
      }
    });
  });

  $("#fromAirport").on("change", function() {
    var $target = $("#toAirport");

    if ($(this).val() === "") {
      $target
        .find("option")
        .remove()
        .end()
        .append("<option/>")
        .prop("disabled", true)
        .trigger("change");
      return;
    }

    $.ajax({
      type: "GET",
      url: $SCRIPT_ROOT + "/_get_airports",
      contentType: "application/json; charset=utf-8",
      data: {
        airport: $(this).val()
      },
      beforeSend: function() {
        $target
          .find("option")
          .remove()
          .end()
          .append("<option/>")
          .prop("disabled", true)
          .trigger("change");
      },
      success: function(data) {
        $.each(data.result, function(index, airport) {
          $target.append(
            $("<option/>")
              .attr("value", airport.value)
              .text(airport.text)
          );
        });
      },
      complete: function() {
        $target.prop("disabled", false);
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
    $("#returnDatePicker")
      .prop({ disabled: false, required: true })
      .val(returnDateVal.visible)
      .trigger("change");

    $('input[name="returnDate"]')
      .val(returnDateVal.hidden)
      .trigger("change");
  });

  $("#nav-oneway-tab").on("click", function() {
    $("#returnDatePicker")
      .prop({ disabled: true, required: false })
      .val("One Way")
      .trigger("change");

    $('input[name="returnDate"]')
      .val("One Way")
      .trigger("change");
  });

  $("#btnResend").on("click", function() {
    var $that = $(this);
    $.ajax({
      type: "POST",
      url: $SCRIPT_ROOT + "/customer/resend",
      contentType: "application/json; charset=utf-8",
      data: {
        email: $("#email").text(),
        next: searchParams.get("next")
      },
      beforeSend: function() {
        $that.text("Sending...");
      },
      success: function(data) {
        if (!isset(data.message)) {
          window.location = "/index.html";
        } else {
          $.snackbar({
            content: data.message,
            style: "snackbar-left justify-content-center mb-2"
          });
        }
      },
      complete: function() {
        startResendTimer();
      },
      error: function(jqXHR, textStatus, errorThrown) {
        alert(errorThrown);
      }
    });
  });

  $(".reverse-destinations").on("click", function() {
    var $btn = $(this);
    var $icon = $btn.children().first();
    var $from = $('select[name="fromAirport"]');
    var $to = $('select[name="toAirport"]');
    var fromVal = $from.val();

    $icon
      .removeClass("fa-exchange-alt")
      .addClass("fa-sync")
      .addClass("fa-spin")
      .addClass("text-alt-primary");

    $from.val($to.val()).trigger("change");

    clearTimeout(timeoutVar);
    timeoutVar = setTimeout(function() {
      $icon
        .removeClass("fa-spin")
        .removeClass("fa-sync")
        .addClass("fa-exchange-alt")
        .removeClass("text-alt-primary");
      $to.val(fromVal).trigger("change");
    }, 500);
  });

  $(".accordion-toggler").hover(function() {
    var $accordion = $(this);
    var $hr = $accordion.children().find("hr");

    if (!$accordion.is(":focus")) {
      $hr.toggleClass("hr-icon-fix");
    }
  });

  $(".accordion-toggler").blur(function() {
    var $accordion = $(this);
    var $hr = $accordion.children().find("hr");

    if ($hr.hasClass("hr-icon-fix")) {
      $hr.removeClass("hr-icon-fix");
    }
  });
});
