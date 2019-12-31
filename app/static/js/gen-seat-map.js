var $btnVal;
var $selectedSeat = $("#selectedSeat");
var $seatPrice = $("#seatPrice");
var $summaryListNames = $(".price-list-names");
var $summaryListPrices = $(".price-list-prices");
var $totalPrice = $(".total-price");
var $totalPriceInput = $("#totalPrice");

$(function() {
  var sc = $("#seat-map").seatCharts({
    map: [
      "fff_fff",
      "bbb_bbb",
      "eee_eee",
      "eee_eee",
      "eee_eee",
      "eee_eee",
      "eee_eee",
      "eee_eee",
      "eee_eee",
      "eee_eee",
      "eee_eee",
      "eee_eee",
      "eee_eee",
      "eee_eee",
      "eee_eee"
    ],
    seats: {
      f: {
        price: 15,
        classes: "first-class",
        category: "First Class"
      },
      b: {
        price: 10,
        classes: "business-class",
        category: "Businnes Class"
      },
      e: {
        price: 5,
        classes: "economy-class",
        category: "Economy Class"
      }
    },
    naming: {
      top: false,
      left: false,
      columns: ["A", "B", "C", " ", "D", "E", "F"],
      getId: function(character, row, column) {
        return row + column;
      }
    },
    legend: {
      node: $("#legend"),
      items: [
        ["f", "available", "First class"],
        ["b", "available", "Businnes class"],
        ["e", "available", "Economy class"],
        ["u", "unavailable", "Unavailable"]
      ]
    },
    click: function() {
      var seatID = this.settings.id;
      var seatCategory = this.data().category;
      var seatPrice = this.data().price;
      var $seatPassenger = $("#seatPassenger-" + $btnVal);
      var $seatClassPassenger = $("#seatClassPassenger-" + $btnVal);
      var $seatPassengerCurrent = $("#currentSeatPassenger-" + $btnVal);
      var $seatClassPassengerCurrent = $(
        "#currentSeatClassPassenger-" + $btnVal
      );
      var seatPassengerCurrentValue = $seatPassenger.val();

      if (this.status() == "available") {
        if (seatPassengerCurrentValue !== "") {
          sc.get(seatPassengerCurrentValue).click();
        }

        $selectedSeat.text(seatCategory + " Seat: " + seatID);
        $seatPrice.text("€" + seatPrice);

        $seatPassenger.val(seatID).trigger("change");
        $seatClassPassenger.val(seatCategory).trigger("change");

        $seatPassengerCurrent.text(seatID);
        $seatClassPassengerCurrent.text(seatCategory);

        $summaryListNames.each(function() {
          $(this).append(
            $("<div/>")
              .attr("class", "seat-" + seatID)
              .text(seatCategory + " Seat: " + seatID)
          );
        });

        $summaryListPrices.each(function() {
          $(this).append(
            $("<div/>")
              .attr("class", "seat-" + seatID + "-price")
              .text("€" + seatPrice)
          );
        });

        $totalPrice.each(function() {
          var price = parseInt($(this).text());
          $(this).text(price + seatPrice);
        });

        $totalPriceInput.val(parseInt($totalPriceInput.val()) + seatPrice);
        return "selected";
      } else if (this.status() == "selected") {
        $selectedSeat.text("");
        $seatPrice.text("");

        $seatPassenger.val("").trigger("change");
        $seatClassPassenger.val("").trigger("change");

        $seatPassengerCurrent.text("None");
        $seatClassPassengerCurrent.text("None");

        if ($summaryListPrices.find(".seat-" + seatID + "-price").length) {
          $totalPrice.each(function() {
            var price = parseInt($(this).text());
            $(this).text(price - seatPrice);
          });
        }

        $(".seat-" + seatID).each(function() {
          $(this).remove();
        });

        $(".seat-" + seatID + "-price").each(function() {
          $(this).remove();
        });

        $totalPriceInput.val(parseInt($totalPriceInput.val()) - seatPrice);
        return "available";
      } else if (this.status() == "unavailable") {
        return "unavailable";
      } else {
        return this.style();
      }
    }
  });

  $("#selectSeat").on("show.bs.modal", function(e) {
    var $btn = $(e.relatedTarget);
    $btnVal = $btn.data("value");
    var $seatPassenger = $("#seatPassenger-" + $btnVal);
    var seatPassengerCurrentValue = $seatPassenger.val();

    if (seatPassengerCurrentValue !== "") {
      var $seat = sc.get(seatPassengerCurrentValue);

      sc.status(seatPassengerCurrentValue, "selected");
      $selectedSeat.text($seat.data().category + " Seat: " + $seat.settings.id);
      $seatPrice.text("€" + $seat.data().price);
    }
  });

  $("#selectSeat").on("hide.bs.modal", function(e) {
    var $seatPassenger = $("#seatPassenger-" + $btnVal);
    var seatPassengerCurrentValue = $seatPassenger.val();

    $selectedSeat.text("");
    $seatPrice.text("");
    if (seatPassengerCurrentValue !== "") {
      sc.status(seatPassengerCurrentValue, "unavailable");
    }
  });

  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/_get_seats",
    contentType: "application/json; charset=utf-8",
    data: {
      departFlightID: $("#DepartFlightID").val()
    },
    success: function(data) {
      $.each(data.result, function(index, seat) {
        sc.status(seat.id, "unavailable");
      });
    },
    error: function(jqXHR, textStatus, errorThrown) {
      alert(errorThrown);
    }
  });
});
